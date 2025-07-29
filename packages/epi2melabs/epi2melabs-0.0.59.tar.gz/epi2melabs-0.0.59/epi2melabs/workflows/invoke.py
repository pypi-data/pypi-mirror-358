"""Launch a nextflow workflow."""

import argparse
import http.client as httplib
import json
import logging
from multiprocessing.connection import Listener
import os
import queue
import subprocess
import sys
import threading
from typing import Any, Dict, Union

from epi2melabs.workflows.database import get_session, Instance, Statuses
from epi2melabs.workflows.launcher import popen


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute a netflow workflow and update the database.",
        usage=(
            "invoke_nextflow -w epi2melabs/wf-alignment -i <instance_id> "
            "-w <workflow_name> -p <params_file> -r <revision> -m <meta_file> "
            "-wd <work_dir> -l <log_file> -s <stdout_file> -d <database> "
            "-rpc <port>"
        )
    )

    parser.add_argument(
        '-n',
        '--nextflow',
        required=True,
        default='nextflow',
        help='Path to the nextflow executable.'
    )

    parser.add_argument(
        '-i',
        '--id',
        required=True,
        help='ID of the database instance record to acquire and update.'
    )

    parser.add_argument(
        '-w',
        '--workflow',
        required=True,
        help='Path to or name of the workflow to be run.'
    )

    parser.add_argument(
        '-p',
        '--params',
        required=True,
        help='Path to the workflow params file.'
    )

    parser.add_argument(
        '-r',
        '--revision',
        required=False,
        default=None,
        help='Workflow revision to execute.'
    )

    parser.add_argument(
        '-wd',
        '--work_dir',
        required=True,
        help='Path to what should become the working directory.'
    )

    parser.add_argument(
        '-l',
        '--log_file',
        required=True,
        help='Path to which the logs should be written.'
    )

    parser.add_argument(
        '-s',
        '--std_out',
        required=True,
        help='Path to which the stdout should be written.'
    )

    parser.add_argument(
        '-m',
        '--meta_file',
        required=True,
        help=(
            'Path at which to write JSON file containing '
            'meta information such as the commands executed.'
        )
    )

    parser.add_argument(
        '-d',
        '--database',
        required=True,
        help='Path to the SQLITE database to update.'
    )

    parser.add_argument(
        '-rpc',
        '--rpc_port',
        required=True,
        help=(
            'Port by which to communicate via rpc. '
            'Overrides the "rpc" key within -m, if given.'
        )
    )

    parser.add_argument(
        '-wsl',
        action='store_true',
        help='Run command in wsl'
    )

    start = 0
    if 'invoke_nextflow' in sys.argv[0]:
        start = 1

    return parser.parse_args(sys.argv[start:])


def have_internet(use_shell=False):
    """Check if we have internet."""
    if use_shell:
        return not popen(
            ['ping', '-c 4', '8.8.8.8'],
            stdout=subprocess.DEVNULL).wait()
    # Thankyou https://stackoverflow.com/a/29854274
    conn = httplib.HTTPSConnection("8.8.8.8", timeout=5)
    try:
        conn.request("HEAD", "/")
        return True
    except Exception as e:
        logging.info(e)
        return False
    finally:
        conn.close()


#
# Functionality needed for implementing a sigint
# equivalent in windows
#
def _thread_process_wait(queue, proc):
    """Wait for a process to complete then notify main thread."""
    ret = proc.wait()
    queue.put(ret)


def _thread_ipc_listen(queue, port, _id):
    """Wait for a signal then notify main thread."""
    address = ('localhost', int(port))
    listener = Listener(address, authkey=bytes(
        _id, encoding='utf8'))
    conn = listener.accept()
    while True:
        msg = conn.recv()
        if msg[0] == 'close' and msg[1] == _id:
            break
    conn.close()
    listener.close()
    queue.put(False)


def kill_process_wsl(pidfile, stdout, stderr, threads=None):
    """End a process running in wsl."""
    popen(
        ['wsl', 'kill', f'$(cat {pidfile})'], windows=True,
        stdout=stdout, stderr=stderr).wait()
    if threads:
        [thread.join() for thread in threads]


def wait_for_workflow(proc, port, _id):
    """Wait for a process to end or an interrupt on windows."""
    q = queue.Queue()
    listener = threading.Thread(
        target=_thread_ipc_listen, args=(q, port, _id))
    waiter = threading.Thread(
        target=_thread_process_wait, args=(q, proc))
    listener.start()
    waiter.start()
    return q.get(), [listener, waiter]


def invoke(
    id: str, workflow: str, params: str, work_dir: str,
    log_file: str, meta_file: str, std_out: str, database: str,
    nextflow: str, rpc_port: str, revision: Union[str, None] = None,
    wsl: bool = False
) -> None:
    """Run nextflow workflow."""
    logging.basicConfig(
        format='invoke_nextflow <%(asctime)s>: %(message)s',
        level=logging.DEBUG)
    logging.info('Initialising.')

    # This somehow fixes when the path when it contains spaces
    nextflow = fr"{nextflow}"

    # Containers for the process and execution threads we'll use
    proc = None
    threads = []

    # Establish settings container
    meta: Dict[str, Any] = dict(
        id=id, workflow=workflow, params=params, work_dir=work_dir,
        log_file=log_file, std_out=std_out, database=database,
        nextflow=nextflow, revision=revision, rpc_port=rpc_port,
        wsl=wsl, wsl_pidfile=None, run_command=None, pull_command=None,
        offline=False)

    # Get command to run workflow
    run_command = [
        nextflow, '-log', log_file, 'run', workflow,
        '-params-file', params, '-w', work_dir,
        '-ansi-log', 'false']

    # Check if we can connect to the internet
    can_connect = have_internet(use_shell=not wsl)

    # Set up command to update workflow
    pull_command = None
    if can_connect:
        if not os.path.isfile(workflow):
            pull_command = [nextflow, 'pull', workflow]
    # Set offline mode if no connection
    else:
        logging.info(
            'Cannot connect to the internet,'
            'not updating workflow.')
        meta['offline'] = True
        run_command.append('-offline')

    # If we are using wsl, we need to adjust our command
    # to store the wsl process pid
    if wsl:
        logging.info('Setting command to run in WSL.')
        meta["wsl_pidfile"] = os.path.dirname(
            work_dir) + '/' + 'wsl_proc.pid'
        wsl_preexec = [
            'wsl', 'echo', '$$', '>', f'{meta["wsl_pidfile"]};', 'exec']
        run_command = wsl_preexec + run_command
        if pull_command:
            pull_command = ['wsl'] + pull_command

    # If we have specified a revision, add it to the
    # end of the command
    if revision:
        logging.info(f'Using revision {revision}.')
        run_command = run_command + ['-r', revision]

    # Get the invocation instance by id from the
    # database and update the pid with this script's
    # Note: this may become somewhat legacy after
    # switching to RPC for killing procs.
    db = get_session(database)
    invocation = db.query(Instance).get(id)
    pid = os.getpid()
    logging.info(f'The wrapper PID is {pid}.')
    invocation.pid = pid
    db.commit()

    # Get handles for outputs
    cli_logfile = open(std_out, 'a')
    stdout = cli_logfile
    stderr = cli_logfile

    try:
        # Update the workflow
        if pull_command:
            logging.info('Updating workflow.')
            meta["pull_command"] = " ".join(pull_command)
            logging.info(f'Command: {meta["pull_command"]}.')
            # We use our custom popen wrapper that helps to
            # prevent the creation of cmd windows on Windows,
            # and at the moment -wsl is synonymous with using
            # Windows.
            proc = popen(
                pull_command, windows=wsl, stdout=stdout,
                stderr=stderr)
            if proc.wait():
                logging.info(
                    'Could not update workflow, are you connected '
                    'to the internet?')

        # Invoke the workflow
        logging.info('Launching workflow.')
        meta["run_command"] = " ".join(run_command)
        logging.info(f'Command: {meta["run_command"]}.')
        proc = popen(
            run_command, windows=wsl, stdout=stdout,
            stderr=stderr)
        logging.info(f'The workflow PID is {proc.pid}.')

        # Set initial database status
        invocation.status = Statuses.LAUNCHED
        db.commit()

        # Dump the meta information to file
        with open(meta_file, 'w', encoding='utf8') as mf:
            mf.write(json.dumps(meta))

        # Listen for a sigint via rpc and/or wait
        # for the workflow to exit
        ret, threads = wait_for_workflow(
            proc, rpc_port, id)
        if ret is False:
            raise KeyboardInterrupt
        sys.exit(ret)

    # If we receive sigint, assume the process was
    # terminated intentionally and exit gracefully
    except KeyboardInterrupt:
        logging.info('Interrupt detected: terminating workflow.')
        if wsl and proc:
            kill_process_wsl(
                meta["wsl_pidfile"], stdout, stderr, threads)
        elif proc:
            proc.kill()
        invocation.status = Statuses.TERMINATED
        db.commit()
        sys.exit(0)

    except SystemExit as e:
        # If we receive system exit of 0, assume the process
        # ended peacefully and exit gracefully.
        if not e.code:
            logging.info('Workflow completed.')
            invocation.status = Statuses.COMPLETED_SUCCESSFULLY
            db.commit()
            sys.exit(0)

        # If we receive a non-zero system exit update the
        # status to reflect an error. Exit with code 1.
        logging.info('Workflow encountered an error.')
        logging.info('See nextflow output for details.')
        invocation.status = Statuses.ENCOUNTERED_ERROR
        db.commit()
        sys.exit(1)

    # This error is thrown if the path to Nextflow
    # is not available, and therefore cannot be launched
    except FileNotFoundError as e:
        logging.info(f"Cant find '{nextflow}' on the path.")
        logging.info(e)
        invocation.status = Statuses.ENCOUNTERED_ERROR
        db.commit()
        sys.exit(1)

    # Handle all other exception classes in the event of
    # unhandled exceptions occurring within the callable.
    # Set the status to error and exit with code 1.
    except Exception as e:
        logging.info('Workflow encountered an error.')
        logging.info(e)
        invocation.status = Statuses.ENCOUNTERED_ERROR
        db.commit()
        sys.exit(1)


def main():
    """Parse arguments and launch a workflow."""
    args = parse_args()
    invoke(
        id=args.id,
        workflow=args.workflow,
        params=args.params,
        revision=args.revision,
        work_dir=args.work_dir,
        log_file=args.log_file,
        rpc_port=args.rpc_port,
        meta_file=args.meta_file,
        std_out=args.std_out,
        database=args.database,
        nextflow=args.nextflow,
        wsl=args.wsl)


if __name__ == '__main__':
    main()

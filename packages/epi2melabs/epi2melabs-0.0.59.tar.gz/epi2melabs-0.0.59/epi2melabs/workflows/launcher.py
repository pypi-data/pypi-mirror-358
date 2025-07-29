"""Launch and track nextflow workflows."""

from dataclasses import dataclass
from datetime import datetime
import json
from multiprocessing.connection import Client
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from typing import Callable, Dict, List, Optional, Tuple, TypedDict, Union
from urllib.parse import quote_plus

import psutil
import requests
import shortuuid

from epi2melabs.workflows.database import get_session, Instance, Statuses


class LauncherException(Exception):
    """A catch-all for application exceptions."""

    ...


class PathResponse(TypedDict):
    """Expected fields in path response."""

    name: str
    path: str
    isdir: bool
    exists: bool
    error: Optional[str]
    updated: Optional[float]
    breadcrumbs: Optional[List['PathResponse']]


class FilePathResponse(PathResponse):
    """Expected fields in file response."""

    contents: Union[None, List[str]]


class DirectoryPathResponse(PathResponse):
    """Expected fields in directory response."""

    contents: Union[None, List[PathResponse]]


class InstanceCreateResponse(TypedDict):
    """Expected fields in instance create response."""

    created: bool
    instance: dict
    error: Union[str, None]


@dataclass
class Workflow:
    """Representation of a nextflow workflow."""

    url: str
    name: str
    desc: str
    path: str
    target: str
    schema: Dict
    defaults: Dict
    demo_data: Dict
    docs: Dict

    def to_dict(self):
        """Return workflow data as dict."""
        return {
            'url': self.url,
            'name': self.name,
            'desc': self.desc,
            'path': self.path,
            'target': self.target,
            'schema': self.schema,
            'defaults': self.defaults,
            'demo_data': self.demo_data,
            'docs': self.docs}


class WorkflowLauncher(object):
    """Manages workflow CRUD operations."""

    MAINNF: str = 'main.nf'
    PARAMS: str = 'params.json'
    SCHEMA: str = 'nextflow_schema.json'

    def __init__(
        self, base_dir=None, workflows_dir=None,
        invoker='invoke_nextflow', nextflow='nextflow',
        labsversion='unknown'
    ) -> None:
        """Initialise instance of WorkflowLauncher."""
        self._workflows: Dict[str, Workflow] = {}

        self.curr_dir = os.getcwd()
        self.base_dir = base_dir or os.path.join(
            os.getcwd(), 'nextflow')
        self.workflows_dir = workflows_dir or os.path.join(
            self.base_dir, 'workflows')
        self.instance_dir = os.path.join(
            self.base_dir, 'instances')
        self.database_uri = f'sqlite:///{self.base_dir}/db.sqlite'

        self._invoker = invoker
        self.nextflow = nextflow
        if self.platform in ["win32"]:
            self.nextflow = self._get_wslpath(nextflow)

        self.get_or_create_dir(self.base_dir)
        self.get_or_create_dir(self.instance_dir)
        self.get_or_create_dir(self.workflows_dir)
        self.db = get_session(self.database_uri)

        self.labsversion = labsversion

    @property
    def invoker(self) -> List[str]:
        """Get the command for the nextflow launch script."""
        # Determine if the invoker is a subcommand or not
        if isinstance(self._invoker, list):
            return self._invoker
        return [self._invoker]

    @property
    def platform(self) -> str:
        """Get launcher platform via remote."""
        return sys.platform

    #
    # Workflows
    #
    @property
    def workflows(self) -> Dict:
        """Get data for all visible workflows."""
        for item in os.listdir(self.workflows_dir):
            if self._workflows.get(item):
                continue
            path = os.path.join(self.workflows_dir, item)
            if not os.path.isdir(path):
                continue
            if self.SCHEMA not in os.listdir(path):
                continue
            try:
                self._workflows[item] = self.load_workflow(
                    item, path)
            except LauncherException:
                pass
        return {
            workflow.name: workflow.to_dict()
            for workflow in self._workflows.values()
        }

    def get_workflow(self, name: str) -> Dict:
        """Get data for a single workflow."""
        if workflow := self.workflows.get(name):
            return workflow
        return {}

    def _get_workflow(self, name: str) -> Union[Workflow, None]:
        """Get a workflow instance."""
        if not self.workflows:
            pass
        if workflow := self._workflows.get(name):
            return workflow
        return None

    def load_workflow(self, name: str, path: str) -> Workflow:
        """Create a workflow instance."""
        schema = self._load_schema(os.path.join(path, self.SCHEMA))

        if not schema:
            raise LauncherException(
                f'Cannot reload {name}: missing schema')

        defaults = self._get_schema_defaults(schema)
        demo_data = self._get_schema_demo_data(schema)

        target = None
        main_nf = os.path.join(path, self.MAINNF)
        if os.path.exists(main_nf):
            target = main_nf

        if not target:
            target = schema.get('title', ' ')
            if ' ' in target:
                raise LauncherException(
                    'Cannot load {name}: invalid title')

        if not target:
            raise LauncherException(
                'Cannot load {name}: no entrypoint')

        return Workflow(
            name=name,
            path=path,
            target=target,
            schema=schema,
            defaults=defaults,
            demo_data=demo_data,
            url=schema.get('url', '#'),
            desc=schema.get('description', ''),
            docs=schema.get('docs', {}))

    #
    # Schema
    #
    def _load_schema(self, path: str) -> Dict:
        """Load data from a workflow schema."""
        with open(path, "r") as schema_path:
            try:
                schema = json.load(schema_path)
                self._annotate_parameter_order(schema)
                return schema
            except json.decoder.JSONDecodeError:
                return {}

    def _annotate_parameter_order(self, schema: Dict) -> Dict:
        """Annotate parameters in a workflow schema with order field."""
        sections = schema.get("definitions", {})
        for _, section in sections.items():
            for index, param in enumerate(
                section.get(
                    "properties", {}
                ).values()
            ):
                param['order'] = index
        return sections

    def _get_schema_demo_data(
        self, schema: Dict
    ) -> Dict[str,  Union[str, int, float, bool]]:
        """Extract demo_data key values from parameters in a schema."""
        return self._get_param_key_value_pairs_from_schema(
            schema, self._get_parameter_demo_data)

    def _get_parameter_demo_data(
        self, param: Dict
    ) -> Union[str, int, float, bool, None]:
        """Extract demo_data value for a parameter in a schema."""
        return param.get('demo_data')

    def _get_schema_defaults(
        self, schema: Dict
    ) -> Dict[str,  Union[str, int, float, bool]]:
        """Extract default key values from parameters in a schema."""
        return self._get_param_key_value_pairs_from_schema(
            schema, self._get_parameter_default)

    def _get_parameter_default(
        self, param: Dict
    ) -> Union[str, int, float, bool, None]:
        """Extract default value for a parameter in a schema."""
        default = None
        if 'default' in param:
            default = self._sanitise_parameter_default(
                param['default'], param.get('type'))
        return default

    def _get_param_key_value_pairs_from_schema(
        self, schema: Dict, getter: Callable
    ) -> Dict[str,  Union[str, int, float, bool]]:
        """Apply getter to parameters in a schema and return results."""
        extracted = self._get_param_key_value_pairs_from_schema_section(
            schema.get("properties", {}), getter)
        sections = schema.get("definitions", {})
        for _, section in sections.items():
            extracted = {
                **extracted,
                **self._get_param_key_value_pairs_from_schema_section(
                    section.get("properties", {}), getter)}
        return extracted

    def _get_param_key_value_pairs_from_schema_section(
        self, schema_section: Dict, getter: Callable
    ) -> Dict[str,  Union[str, int, float, bool]]:
        """Apply getter to parameters in a schema section."""
        extracted = {}
        for key, param in schema_section.items():
            default = getter(param)
            if default is None:
                continue
            extracted[key] = default
        return extracted

    def _sanitise_parameter_default(
        self,
        default: Union[str, int, float, bool],
        _type=None
    ) -> Union[str, int, float, bool]:
        """Coerce schema defaults to appropriate pythom types."""
        if not _type:
            return default
        elif _type == "boolean":
            if not isinstance(default, bool):
                default = (default == "true")
            return default
        elif isinstance(default, str) and default.strip() == "":
            return ""
        elif _type == "integer":
            return int(default)
        elif _type == "number":
            return float(default)
        return str(default)

    #
    # Instances
    #
    @property
    def instances(self) -> Dict:
        """Get data for all workflow run instances."""
        return {
            instance.id: instance.to_dict()
            for instance in self.db.query(Instance).all()
        }

    def get_instance(self, id: str) -> Dict:
        """Get data for a single workflow run instance."""
        if instance := self._get_instance(id):
            return instance.to_dict()
        return {}

    def _get_instance(self, id: str) -> Union[Instance, None]:
        """Get a workflow run instance."""
        if instance := self.db.query(Instance).get(id):
            return instance
        return None

    def create_instance(
        self, name: str, workflow_name: str, params: Dict
    ) -> InstanceCreateResponse:
        """Create a new workflow run instance if workflow is available."""
        workflow = self._get_workflow(workflow_name)

        if not workflow or not workflow.target:
            return InstanceCreateResponse(
                created=False, instance={},
                error='Could not create instance, workflow unknown')

        return self._create_instance(
            name, workflow.name, workflow.target,
            workflow.schema, params)

    def _create_instance(
        self, name: str, workflow_name: str, workflow_target: str,
        workflow_schema: Dict, params: Dict
    ) -> InstanceCreateResponse:
        """Create and launch new workflow run instance."""
        # Generate instance details
        _id = str(shortuuid.uuid())
        now = datetime.now().strftime("%Y-%m-%d-%H-%M")
        dirname = '_'.join([now, workflow_name, _id])
        path = os.path.join(self.instance_dir, dirname)

        # Create instance db record
        instance = Instance(_id, path, name, workflow_name)
        self.db.add(instance)
        self.db.commit()

        # Construct instance filepaths
        params_file = os.path.join(path, self.PARAMS)
        nf_logfile = os.path.join(path, 'nextflow.log')
        nf_std_out = os.path.join(path, 'nextflow.stdout')
        iv_std_out = os.path.join(path, 'invoke.stdout')
        meta_file = os.path.join(path, 'meta.json')
        out_dir = os.path.join(path, 'output')
        work_dir = os.path.join(path, 'work')

        # Touch instance files and directories
        self.get_or_create_dir(path)
        self.get_or_create_dir(out_dir)
        self.get_or_create_dir(work_dir)

        for targ in [nf_logfile, nf_std_out, iv_std_out]:
            with open(targ, 'a'):
                pass

        # Coerce params and write to file
        params = self._fix_parameters(workflow_schema, params)
        # Todo: generalise to support 3rd party wfs
        params['out_dir'] = out_dir
        params['wf'] = {'agent': f'labslauncher/{self.labsversion}'}
        self.write_json(params, params_file)

        # Get version
        wfversion = params['wfversion']
        revision = wfversion if not os.path.exists(workflow_target) else None

        # Get a port for comms with the workflow wrapper
        rpc_port = self.get_free_port()

        # Handle being on windows
        windows = False
        if self.platform in ["win32"]:
            windows = True

            # Make sure nextflow is executable
            chmodx = ['wsl', 'chmod', '+x', self.nextflow]
            proc = popen(chmodx, windows=windows)
            proc.wait()

            # Re-write paths within params file
            wsl_params = self._get_wslpath_params(workflow_schema, params)
            params_file = os.path.join(path, f"wsl-{self.PARAMS}")
            self.write_json(wsl_params, params_file)
            params_file = self._get_wslpath(params_file)

            # Re-write nextflow command paths
            work_dir = self._get_wslpath(work_dir)
            nf_logfile = self._get_wslpath(nf_logfile)
            if os.path.exists(workflow_target):
                workflow_target = self._get_wslpath(workflow_target)

        # Launch process
        error = self._start_instance(
            instance, workflow_target, params_file, work_dir, nf_logfile,
            nf_std_out, iv_std_out, meta_file, rpc_port, self.database_uri,
            revision, windows)

        return InstanceCreateResponse(
            created=True, instance=instance.to_dict(), error=error)

    def _start_instance(
        self, instance: Instance, workflow_target: str, params_file: str,
        work_dir: str, nf_logfile: str, nf_std_out: str, iv_std_out: str,
        meta_file: str, rpc_port: str, database: str,
        revision: Union[str, None], windows: bool
    ) -> Union[str, None]:
        """Launch new workflow run instance."""
        command = self.invoker + [
            '-i', instance.id, '-w', workflow_target, '-m', meta_file,
            '-p', params_file, '-wd', work_dir, '-l', nf_logfile,
            '-s', nf_std_out, '-d', database, '-n', self.nextflow,
            '-rpc', rpc_port]

        if windows:
            command = command + ['-wsl']

        if revision:
            command = command + ['-r', revision]

        # Ensure the default location for docker on MacOS is available
        env = os.environ.copy()
        env["PATH"] = "/usr/local/bin:" + env["PATH"]

        # Setup process fds
        logfile = open(iv_std_out, 'a')
        stdout = logfile
        stderr = logfile

        # Create settings map
        kwargs = dict(
            stdout=stdout, stderr=stderr, close_fds=True,
            cwd=self.base_dir, env=env)

        # Update settings per platform
        if windows:
            newgrp = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore
            kwargs.update(creationflags=newgrp)
        else:
            kwargs.update(start_new_session=True)

        # Launch invocation script
        try:
            proc = popen(command, windows=windows, **kwargs)
        except FileNotFoundError:
            error = 'Could not launch instance, invocation script not found'
            logfile.write(error)
            instance.status = Statuses.ENCOUNTERED_ERROR  # type: ignore
            self.db.commit()
            return error

        instance.pid = proc.pid  # type: ignore
        self.db.commit()

    def delete_instance(self, id: str, delete: bool = False) -> bool:
        """Delete a workflow run instance."""
        instance = self._get_instance(id)
        if not instance:
            return False

        # Stop any process
        actioned = self._stop_instance(instance)
        if actioned:
            instance.status = Statuses.TERMINATED  # type: ignore
            self.db.commit()

        # Optionally delete the directory
        if delete:
            try:
                shutil.rmtree(instance.path)
            except FileNotFoundError:
                pass

            # Delete record
            self.db.delete(instance)
            self.db.commit()

        return True

    def _stop_instance(self, instance) -> bool:
        """Stop a workflow run instance from running."""
        if instance.status != Statuses.LAUNCHED:
            return False

        meta_file = os.path.join(instance.path, 'meta.json')
        meta_data = {}

        for _ in range(3):
            try:
                with open(meta_file, 'r', encoding='utf8') as mf:
                    meta_data = json.load(mf)
                    break
            except Exception:
                time.sleep(2)

        if rpc_port := meta_data.get('rpc_port', None):
            address = ('localhost', int(rpc_port))
            conn = Client(address, authkey=bytes(
                instance.id, encoding='utf8'))
            conn.send(('close', instance.id))
            conn.close()
            return True
        return False

    #
    # Pathing
    #
    def get_path(self, path: str) -> PathResponse:
        """Get information on a filesystem path."""
        # Explicitly handle special 'root' keyword
        if path.lower() == 'root':
            return self._get_root_path_response()
        path = self._fix_path(path)
        return self._get_path_response(path)

    def get_file(
        self,
        path: str,
        contents: bool = False
    ) -> FilePathResponse:
        """Get information on a filesystem file path."""
        lines = None
        path = self._fix_path(path)
        resp = self._get_path_response(path)
        if resp.get('exists'):
            if contents:
                lines = self.read_file(path)
            if resp.get('isdir'):
                resp['error'] = 'Path is not a file'
        return FilePathResponse(**resp, contents=lines)

    def read_file(self, path: str) -> List[str]:
        """Load file data."""
        lines = []
        with open(path) as lf:
            lines = lf.readlines()
            lines = [self._process_line(line) for line in lines]
        return lines

    def _process_line(self, line: str) -> str:
        """Strip a line of text of ANSI sequences."""
        line = line.rstrip()
        # 7-bit C1 ANSI sequences
        # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', line)

    def get_directory(
        self,
        path: str,
        contents: bool = False
    ) -> DirectoryPathResponse:
        """Get information on a filesystem directory path."""
        # Explicitly handle special 'root' keyword
        if path.lower() == 'root':
            return self._get_root_directory_response(
                self.platform)
        items = None
        path = self._fix_path(path)
        resp = self._get_path_response(path)
        if resp.get('exists'):
            if contents:
                items = self.list_dir(path)
            if not resp.get('isdir'):
                resp['error'] = 'Path is not a directory'
        return DirectoryPathResponse(**resp, contents=items)

    def list_dir(self, path: str) -> List[PathResponse]:
        """List the contents of a directory."""
        items = []
        for item in os.listdir(path):
            item_abspath = self._fix_path(
                os.path.join(path, item))
            items.append(self._get_path_response(item_abspath))
        return items

    def _get_root_path_response(
        self,
    ) -> PathResponse:
        resp = PathResponse(
            name='root', path='root', updated=None,
            exists=True, error=None, isdir=True, breadcrumbs=None)
        return resp

    def _get_root_directory_response(
        self,
        platform: str,
    ) -> DirectoryPathResponse:
        resp = self._get_root_path_response()
        if platform in ["win32"]:
            items = self._get_drives()
            return DirectoryPathResponse(**resp, contents=items)
        items = self.list_dir('/')
        return DirectoryPathResponse(**resp, contents=items)

    def _get_drives(self):
        """Get the contents of 'root' (drives) on Windows."""
        partitions = psutil.disk_partitions()
        return [self._get_path_response(
            d.device.replace(os.sep, '/')) for d in partitions]

    def _get_path_response(
        self,
        abspath: str,
        breadcrumbs=True,
        exists_error="Path does not exist or host cannot see it."
    ) -> PathResponse:
        """Generate an undifferentiated path response."""
        name = os.path.basename(abspath) or abspath
        exists = os.path.exists(abspath)
        is_dir = os.path.isdir(abspath)
        error = None if exists else exists_error
        modified = os.path.getmtime(abspath) if exists else None
        breadcrumbs = self._get_breadcrumbs(
            abspath) if breadcrumbs else None
        return PathResponse(
            name=name,
            path=abspath,
            updated=modified,
            exists=exists,
            error=error,
            isdir=is_dir,
            breadcrumbs=breadcrumbs)

    def _get_breadcrumbs(
        self,
        path: str,
        _breadcrumbs: Optional[List[PathResponse]] = None
    ) -> List[PathResponse]:
        """Get seperate path responses for each path section."""
        if not os.path.abspath(path):
            raise ValueError('Path is not absolute')
        if not _breadcrumbs:
            _breadcrumbs = []
        head, _ = os.path.split(path)
        if not head or head in ['/', path]:
            return _breadcrumbs
        _breadcrumbs.append(
            PathResponse(
                name=os.path.basename(head) or head,
                path=head,
                updated=None,
                exists=True,
                error=None,
                isdir=True,
                breadcrumbs=None))
        _breadcrumbs = self._get_breadcrumbs(head, _breadcrumbs)
        return _breadcrumbs

    def _fix_path(self, path: str) -> str:
        """Convert a relative filesystem path to absolute."""
        if not os.path.isabs(path):
            path = os.path.join(self.base_dir, path)
        return os.path.abspath(path).replace(os.sep, "/")

    def get_or_create_dir(self, path: str) -> Tuple[bool, str]:
        """Get or create a directory."""
        if not os.path.exists(path):
            os.mkdir(path)
        if os.path.isdir(path):
            return True, os.path.abspath(path)
        return False, os.path.abspath(path)

    def _fix_parameters(
        self, schema: Dict, params: Dict
    ) -> Dict:
        """Convert path-like parameter values to absolute paths."""
        return self._fix_pathing_params(
            schema, params, self._fix_path)

    def _get_wslpath_params(
        self, schema: Dict, params: Dict
    ) -> Dict:
        """Convert path-like parameter values to WSL paths."""
        return self._fix_pathing_params(
            schema, params, self._get_wslpath)

    def _fix_pathing_params(
        self, schema: Dict, params: Dict, fixer: Callable
    ) -> Dict:
        """Apply fixer to each path-like parameter subschema in params."""
        updated = {}
        for name, value in params.items():
            param_schema = self._get_schema_for_param(schema, name)
            fmt = param_schema.get('format')
            if fmt in ['path', 'file-path', 'directory-path']:
                if any(value.startswith(i) for i in
                        ['http', 's3', r'${projectDir}']):
                    updated[name] = value
                    continue
                updated[name] = fixer(value)
                continue
            updated[name] = value
        return updated

    def _get_schema_for_param(
        self, schema: dict, param_name: str
    ) -> Dict:
        """Get the schema section for a given parameter."""
        sections = schema.get('definitions', {})
        for section in sections.values():
            for k, v in section.get('properties', {}).items():
                if k == param_name:
                    return v
        return {}

    def _get_wslpath(self, path: str) -> str:
        """Get the WSL path for a given host path."""
        path = path.replace('\\', '/')
        proc = popen(
            ["wsl", "wslpath", "-a", path],
            windows=True,
            text=True,
            stdout=subprocess.PIPE)
        return proc.stdout.readline().rstrip()

    def write_json(self, data, path):
        """Write data to a json file."""
        with open(path, 'w') as json_file:
            json_file.write(json.dumps(data, indent=4))

    def get_free_port(self):
        """Find a free port."""
        sock = socket.socket()
        sock.bind(('', 0))
        return str(sock.getsockname()[1])


class RemoteWorkflowLauncher(WorkflowLauncher):
    """Manages workflow CRUD operations via remote."""

    def __init__(
        self, base_dir, workflows_dir,
        ip: str = '0.0.0.0', port: str = '8090'
    ) -> None:
        """Initialise instance of RemoteWorkflowLauncher."""
        self.ip = ip
        self.port = port

        super().__init__(base_dir, workflows_dir)

    @property
    def platform(self):
        """Get launcher platform via remote."""
        response = requests.get(
            f'http://{self.ip}:{self.port}/platform')
        data = response.json()
        return data.get('platform', None)

    @property
    def instances(self) -> Dict:
        """Get data for all workflow run instances via remote."""
        response = requests.get(
            f'http://{self.ip}:{self.port}'
            f'/instances?uuid={shortuuid.uuid()}')
        return response.json()

    def get_instance(self, id: str) -> Dict:
        """Get data for a single workflow run instance via remote."""
        response = requests.get(
            f'http://{self.ip}:{self.port}'
            f'/instances/{id}?uuid={shortuuid.uuid()}')
        return response.json()

    def create_instance(
        self, name: str, workflow_name: str, params: Dict
    ) -> InstanceCreateResponse:
        """Create a new workflow run instance via remote."""
        workflow = self._get_workflow(workflow_name)

        if not workflow or not workflow.target:
            return InstanceCreateResponse(
                created=False, instance={},
                error='Could not create instance, workflow unknown')

        response = requests.post(
            f'http://{self.ip}:{self.port}/instances',
            data=json.dumps({
                'name': name,
                'workflow_name': workflow_name,
                'workflow_target': workflow.target,
                'workflow_schema': workflow.schema,
                'params': params,
            }),
            headers={
                'Content-type': 'application/json',
                'Accept': 'text/plain'
            })

        data = response.json()
        return data

    def delete_instance(
        self, id: str, delete: bool = False
    ) -> bool:
        """Delete a workflow run instance via remote."""
        response = requests.delete(
            f'http://{self.ip}:{self.port}'
            f'/instances/{id}?delete={delete}')

        data = response.json()
        return data['deleted']

    def get_path(self, path: str) -> PathResponse:
        """Get information on a filesystem path via remote."""
        response = requests.get(
            f'http://{self.ip}:{self.port}'
            f'/path/{quote_plus(quote_plus(path))}')
        return response.json()

    def get_file(
        self, path: str, contents: bool = False
    ) -> FilePathResponse:
        """Get information on a filesystem file path via remote."""
        _cont = ''
        if contents:
            _cont = f'?contents={shortuuid.uuid()}'
        response = requests.get(
            f'http://{self.ip}:{self.port}'
            f'/file/{quote_plus(quote_plus(path))}{_cont}')
        return response.json()

    def get_directory(
        self, path: str, contents: bool = False
    ) -> DirectoryPathResponse:
        """Get information on a filesystem directory path via remote."""
        _cont = ''
        if contents:
            _cont = f'?contents={shortuuid.uuid()}'
        response = requests.get(
            f'http://{self.ip}:{self.port}'
            f'/directory/{quote_plus(quote_plus(path))}{_cont}')
        return response.json()

    def _get_wslpath(self, path: str) -> str:
        """Get the WSL path for a given host path via remote."""
        response = requests.get(
            f'http://{self.ip}:{self.port}'
            f'/wslpath/{quote_plus(quote_plus(path))}')
        data = response.json()
        return data.get('path', '')


def get_workflow_launcher(
    base_dir, workflows_dir, remote=False,
    ip=None, port=None
):
    """Create the correct workflow launcher."""
    if remote:
        kwargs = {'ip': ip, 'port': port}
        for k, v in kwargs.items():
            if v is None:
                kwargs.pop(k)
        return RemoteWorkflowLauncher(base_dir, workflows_dir, **kwargs)
    return WorkflowLauncher(base_dir, workflows_dir)


def popen(
    cmd: List[str], windows: bool = False, **kwargs
) -> subprocess.Popen:
    """Run subprocess, ensuring no popups on windows."""
    if windows:
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
        kwargs.update(startupinfo=startupinfo)
    return subprocess.Popen(cmd, **kwargs)

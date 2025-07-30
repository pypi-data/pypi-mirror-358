"""
Module to read and parse YAML or JSON files, locally or remotely (gitlab only)

subclasses "jsonref", adding YAML reading and datapath discovery
"""
import functools
import json
import sys
import warnings
import inspect
import copy
from json.decoder import JSONDecodeError
from pathlib import Path
from urllib import parse as urlparse
from urllib.parse import unquote
import logging

import yaml  # WCC

# obsinfo imports
from ..misc.remoteGitLab import gitLabFile
from ..misc.datapath import Datapath

# jsonref imports
from .jsonref import (JsonRef, JsonLoader,
                      dump as jref_dump, dumps as jref_dumps)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")

PY3 = sys.version_info[0] >= 3


class YAMLRef(JsonRef):
    """
    Datapath-aware version of JsonRef

    Additional Attributes:
        datapath (:class:`Datapath`): stores directories to search for files
    """
    def __init__(self, *args, **kwargs):
        self.datapath = kwargs.pop('datapath', None)
        super().__init__(*args, **kwargs)

    @property
    def _ref_kwargs(self):
        outdict = super()._ref_kwargs
        outdict['datapath'] = self.datapath
        # print(f'_ref_kwargs() {outdict=}')
        return outdict

    @property
    def full_uri(self):
        """
        This method/property returns the full uri to reference a ``$ref`` object.
        It's the heart of how a datapath is used to either access a local
        or remote (gitlab) file.
        All schema files are supposed to be local, part of the obsinfo
        distribution

        :returns: updated full uri
        :raises: ValueError
        """
        kwargs = self._ref_kwargs

        if kwargs['jsonschema']:
            value =  super().full_uri
            # print(f"full_uri: {value=}", flush=True)  # DEBUG
        else:
            dp = kwargs["datapath"]
            if not dp:
                msg = f'Error in datapath in full_uri, reference: {self.__reference__["$ref"]}'
                logger.error(msg)
                raise ValueError(msg)
            base_uri = Path(dp.build_datapath(self.__reference__["$ref"]))

            tupl = urlparse.urlsplit(str(base_uri))
            path = unquote(tupl.path)
            frag = tupl.fragment
            new_uri = Datapath.add_frag(path, frag)
            # define the uri depending on whether it is remote or not
            if gitLabFile.isRemote(str(base_uri)):
                self.base_uri = new_uri
            else:
                self.base_uri = unquote(base_uri.as_uri())

            value = self.base_uri
            # print(f"full_uri: {value=}", flush=True)  # DEBUG
        return value

    def _error(self, message, cause=None):
        # Handle case where self.__reference doesn't exist
        if not hasattr(self, '__reference__'):  # WCC
            self.__reference__ = None
        msg = f"Error {message} in {self.__reference__}: {cause}"
        logger.exception(msg)
        # print(f"_error: {msg=}, {cause=}", flush=True)
        super()._error(msg, cause)


class YAMLLoader(JsonLoader):
    """
    Adds YAML read
    """

    def get_remote_json(self, uri, **kwargs):
        """
        Adds yaml read and possibility to get a gitlab remote file
        (using gitlab API version 4)
        """
        # print('get_remote_json()')
        scheme = urlparse.urlsplit(uri).scheme
        path = urlparse.urlsplit(uri).path

        if scheme == "file" and path[0] == '/' and path[2] == ':':
            # path like start with / and 3rd char is : means windows path like
            # /C:/User/ssomething/somthing.yaml
            # eliminate starting / then windows can load file
            path = path[1:]

        logger.debug(f"Opening file: {path}")
        # Open locally or remotely according to scheme
        if scheme == 'file':
            try:
                with open(path, "rt") as fp:
                    strm = fp.read()
            except FileNotFoundError:
                msg = f'File not found: {path}'
                logger.exception(msg)
                raise
            except (IOError, OSError):
                msg = f'Input/Output error with file: {path}'
                logger.exception(msg)
                raise
        else:
            strm = gitLabFile.get_gitlab_file(uri)

        result = _yaml_loads(strm, **kwargs)   # LFA
        return result
        

jsonloader = YAMLLoader()


def load(fp, base_uri="", loader=None, jsonschema=False, load_on_repr=True,
         datapath=None, **kwargs):
    """
    jsonref:load() plus datapath and yaml reading

    Args:
        datapath (:class:`Datapath`):  object to implement file discovery
    """
    # print('load()')
    if loader is None:
        loader = functools.partial(jsonloader, **kwargs)
    base_uri = unquote(base_uri)
    obj = YAMLRef.replace_refs(_yaml_load(fp, **kwargs),
                                base_uri=base_uri,
                                loader=loader,
                                jsonschema=jsonschema,
                                load_on_repr=load_on_repr,
                                datapath=datapath)
    return obj

def loads(s, base_uri="", loader=None, jsonschema=False, load_on_repr=True,
          datapath=None, recursive=True, **kwargs):
    """
    jsonref:loads() plus datapath and yaml reading

    Args:
        datapath (:class:`Datapath`):  object to implement file discovery
    """
    #  print('loads()')
    if loader is None:
        loader = functools.partial(jsonloader, **kwargs)
    dic = _yaml_loads(s, **kwargs) if isinstance(s, str) else s
    if recursive:
        obj = YAMLRef.replace_refs(
            dic,  # WCC et LFA
            base_uri=base_uri,
            loader=loader,
            jsonschema=jsonschema,
            load_on_repr=load_on_repr,
            datapath=datapath,
        )
        return obj
    else:
        return dic


def load_uri(uri, base_uri=None, loader=None, jsonschema=False, load_on_repr=True,
             datapath=None):
    """
    jsonref:load_uri() plus datapath and yaml reading

    Args:
        datapath (:class:`Datapath`):  object to implement file discovery

    Returns:
        newref (dict): parsed YAML or JSON formats
    """
    # print('load_uri()')
    if loader is None:
        loader = jsonloader
    if base_uri is None:
        base_uri = uri
    return YAMLRef.replace_refs(
        loader(uri),
        base_uri=base_uri,
        loader=loader,
        jsonschema=jsonschema,
        load_on_repr=load_on_repr,
        datapath=datapath)


def dump(*args, **kwargs):
    jref_dump(*args, **kwargs)


def dumps(*args, **kwargs):
    jref_dumps(*args, **kwargs)


# obsinfo-specific functions

def _yaml_load(fp, **kwargs):
    """
    Call {yaml,json}.load according to file type. Invoked by :func: load

    Args:
        fp (file-like): object containing JSON document
        kwargs (dict): Any of the keyword arguments from
            :meth:`YAMLRef.replace_refs`. Any other keyword arguments
            will be passed to :func:`_yaml_loads`
    Returns:
        (dict): parsed YAML or JSON formats
    Raises:
        JSONDecodeError, YAMLError
    """
    # print('_yaml_load()')
    try:      
        obj = json.load(fp, **kwargs)
    except Exception as jsonError:
        fp.seek(0)
        try:
            obj = yaml.safe_load(fp)
        except Exception as yamlError:
            msg = f'file {fp.name} is neither JSON nor YAML.'
            logger.exception(msg)
            if fp.name.split('.')[-1].upper() == 'YAML':
                logger.exception(str(yamlError))
                raise yaml.YAMLError(yamlError)
            elif fp.name.split('.')[-1].upper() in ('JSON', 'JSN'):
                logger.exception(str(jsonError))
                raise JSONDecodeError(msg, fp.name, 0)
            else:
                raise ValueError(msg)
    return obj


# Method validate in ObsMetadata uses loads, not load. loads loads a string, not a file.
def _yaml_loads(s, **kwargs):
    """
    Call {yaml,json}.loads according to file type. Invoked by :func: loads

    Args:
        s (str): JSON document string
        kwargs (dict): This function takes any of the keyword arguments from
            :meth:`YAMLRef.replace_refs`. Any other keyword arguments will
            be passed to :func:`_yaml_loads`
    Returns:
        (dict): parsed YAML or JSON formats
    Raises:
        JSONDecodeError, YAMLError
    """
    # print('_yaml_loads()')
    # print('v'*80)
    # print(s)
    a = None

    kw = copy.deepcopy(kwargs)  # copy to make sure you don't alter the original kwargs
    kw.pop('base_uri', None)
    kw.pop('datapath', None)

    if s[:3] == '---':
        try:
            a = yaml.safe_load(s, **kw)
        except Exception:
            try:
                a = json.loads(s, **kwargs)
            except Exception:
                msg = 'String is neither JSON nor YAML'
                logger.exception(msg)
                raise JSONDecodeError(msg)

    else:
        try:
            a = json.loads(s, **kwargs)
        except BaseException as jerr:
            try:
                a = yaml.safe_load(s, **kwargs)
            except BaseException as yerr:
                msgs = ('String is neither JSON nor YAML',
                        f'JSON error message: {str(jerr)}',
                        f'YAML error message: {str(yerr)}')
                for msg in msgs:
                    logger.error(msg)
                    print(msg)
                raise ValueError('\n'.join(msgs))
    # print('^'*80)
    return a

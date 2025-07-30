"""
obsinfo information file routines, contained in superclass ObsMetadata for
generality
"""
# Standard library modules
import json
from pathlib import Path, PurePath
from urllib.parse import urlparse
from urllib.parse import unquote
import logging
from time import perf_counter
import inspect

# Non-standard modules
import jsonschema
import yaml

# Local modules
from ..misc import yamlref
from ..misc.yamlref import JsonLoader
from ..misc.remoteGitLab import gitLabFile
from ..misc.datapath import Datapath

import pdb

logger = logging.getLogger("obsinfo")

overwrite_string = 'replace_'      # Used by safe_update
root_symbol = "#"
VALID_FORMATS = ["JSON", "YAML"]
DEFAULT_SCHEMA_PATH = Path(__file__).parent.parent.joinpath('data', 'schemas')
VALID_TYPES = [Path(f.stem).stem
               for f in DEFAULT_SCHEMA_PATH.glob('*.schema.json')]


class ObsMetadata(dict):
    def __init__(self, *args, **kwargs):
        """
        Constructor, create a dict subclass object

        """
        # print('ObsMetadata.__init__() START')
        super().__init__(*args, **kwargs)
        self._convert_to_obsmetadata()

    def list_valid_types():
        """
        Returns a list of valid information file types
        """
        return VALID_TYPES

    @staticmethod
    def is_valid_type(type):
        """
        Returns true if input string corresponds to a valid schema type
        
        Args:
            type (str): type name to test
        """
        return type in VALID_TYPES

    def validate(self, info_filename, schemas_path=None, remote=False,
                 file_format=None, file_type=None, verbose=False,
                 schema_filename=None, quiet=False, dp=None,
                 check_schema=False, debug=False):
        """
        Validates a YAML or JSON file against schema

        Args:
            info_filename (str or path-like): name of information file to
                validate
            schemas_path (str or :class:`Path`): path to schema files.
                If None, uses DEFAULT_SCHEMA_PATH
            remote (bool): whether to search for info_filename in a remote
                repository
            file_format (str): "JSON" or "YAML"
            file_type (str): type of info file: "network", "station",
                "instrumentation", "datalogger", "preamplifier", "sensor",
                "stage", "filter"
            verbose (bool): Print progression of validation steps with
                filenames
            schema_file (str): name (without path) of schema file
            quiet (bool): No output at all
            dp (:class:`Datapath`): datapath for information files.  If None,
                defaults to values stored in .obsinforc
            check_schema (bool): validate schema file as well

        If file_type and/or format are not provided, tries to figure them out
        from the info_filename, which should end with "*{FILETYPE}.{FORMAT}*
        """
        # print('validate() START')
        if quiet:
            verbose = False

        # Get schema filename
        if debug is True:
            tic = perf_counter()
        if not schema_filename:
            if not file_type:
                file_type = ObsMetadata.get_information_file_type(info_filename)
            if file_type in (None, type(None)):
                logger.error(f'Could not determine file type for {info_filename}')
            if quiet is False:
                print(f'{file_type=}')
            schema_filename = file_type + '.schema.json'

        if debug is True:
            tic = _timing_message(tic, 'ObsMetadata.validate() get_information_file_type()')

        # Get infofile instance and schema
        if dp is None:
            dp = Datapath()
        instance = self.read_info_file(info_filename, dp, remote, False,
                                       file_format, verbose)
        if debug is True:
            tic = _timing_message(tic, 'ObsMetadata.validate() read_info_file()')
        x =  self.validate_infodict(instance, schema_filename,
                                    verbose=verbose, quiet=quiet,
                                    schemas_path=schemas_path,
                                    check_schema=check_schema,
                                    debug=debug)
        if debug is True:
            tic = _timing_message(tic, 'ObsMetadata.validate() validate_info_dict()')
        return x

    def validate_infodict(self, info_dict, schema_filename, verbose=False,
                          quiet=False, schemas_path=None, check_schema=True,
                          debug=False):
        """
        Validates an infofile dict against schema

        Args:
            info_dict (dict or :class:`ObsMetadata`): information to
                validate
            verbose (bool): Print progression of validation steps with
                filenames
            schema_filename (str): name (without path) of schema file
            schemas_path (str or :class:`Path`): path to schema files.
                If None, uses DEFAULT_SCHEMA_PATH
            check_schema (bool): validate schema file as well
            debug (bool): print timing info
        """
        if debug is True:
            tic = perf_counter()
        # Get schema filename
        if ".schema.json" not in schema_filename:
            schema_filename += '.schema.json'

        # pdb.set_trace()
        instance = ObsMetadata(info_dict)

        if debug is True:
            tic = _timing_message(tic, 'Obsmetadata:validate_infodict() ObsMetadata()')

        schema, schema_fullpath = self._read_schema_file(schema_filename,
                                                         schemas_path,
                                                         debug=debug)
        if debug is True:
            tic = _timing_message(tic, 'Obsmetadata:validate_infodict()  _read_schema_file()')
        if schema is False:
            logger.error('Could not read schema file {} at {}'.format(
                schema_filename, schemas_path))
            return False
        e = self._report_errors(instance, schema, schema_fullpath, verbose,
                                quiet, check_schema)
        if debug is True:
            tic = _timing_message(tic, 'obsmetadata:validate_infodict()  _report_errors()')
        return e

    @staticmethod
    def check_schema(schema, verbose, quiet=False, debug=True):
        """
        Runs jsonschema.Draft7Validator on the provided schema
        
        Returns:
            result (bool): True if schema checks out, false if not
        """
        if debug:
            tic = perf_counter()
        msg = "\tTesting schema ..."
        logger.info(msg)
        if verbose:
            print(msg, end="")

        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except jsonschema.ValidationError as e:
            logger.exception("SCHEMA ERROR: " + e.message)
            return False
        logger.info("OK")
        if verbose:
            print("OK")
        if debug is True:
            _timing_message(tic, 'check_schema()')
        return True

    def get_information_file_format(filename):
        """
        Determines if a filename is in JSON or YAML format.

        Assumes that the filename is "*.{FORMAT}*"

        Args:
            filename (str): filename to determine the type of
        Returns:
            file_format
        Raises:
            (ValueError): on unknown format
        """
        suffix = PurePath(filename).suffix
        file_format = suffix[1:].upper()
        if file_format in VALID_FORMATS:
            return file_format
        msg = f"Unknown file_format: {file_format}"
        logger.error(msg)
        raise ValueError(msg)

    def get_information_file_type(filename):
        """
        Determines the type of a file from its filename.

        Assumes that the filename is "*.{TYPE}.{SOMETHING}*""

        Args:
            filename (str): filename to determine the type of
        Returns:
            (str): file type
        Raises:
            ValueError
        """
        stem = PurePath(filename).stem
        suffix = PurePath(stem).suffix
        type = suffix[1:]
        if type in VALID_TYPES:
            return type
        msg = f"File '{filename}' is of unknown type: {type}"
        logger.warning(msg)
        return None

    def read_json_yaml(filename, file_format=None):
        """
        Reads a JSON or YAML file. Does NOT use jsonReference  DEPRECATED.

        DEPRECATED. Not being used by any obsinfo method or function. Kept
        for compatibility

        Args:
            filename (str): filename
            file_format (str): "YAML" or "JSON"
        Returns:
            (dict):  JSON or YAML parsed information files
        Raises:
            (JSONDecodeError): problem with JSON read
            (FileNotFoundError): file not found
            (IOError): File input/output erre
        """
        if not file_format:
            # Also validates that format is legal and exits if not
            file_format = ObsMetadata.get_information_file_format(filename)

        with open(filename, "r") as f:
            if file_format == "YAML":
                try:
                    element = yaml.safe_load(f)
                except Exception:
                    msg = f"Error loading YAML file: {filename}"
                    logger.exception(msg)
                    raise
            else:
                try:
                    element = json.load(f)
                except json.JSONDecodeError as e:
                    msg = ("JSONDecodeError: Error loading JSON file: "
                           f"{filename}: {str(e)}")
                    logger.exception(msg)
                    raise
                except Exception:
                    msg = f"Error loading JSON file: {filename}"
                    logger.exception(msg)
                    raise
        return element

    def read_json_yaml_ref_datapath(filename, datapath, file_format=None):
        """
        Reads a JSON or YAML file using jsonReference using OBSINFO_DATAPATH

        Args:
            filename (str): filename
            datapath (:class:`.Datapath`): list of directories to search
                for info files
            file_format(str): "YAML" or "JSON"
        Returns:
            (dict):  JSON or YAML parsed information files
        Raises:
            (JSONDecodeError): problem with JSON read
            (FileNotFoundError): file not found
            (IOError): File input/output erre
        """
        if not file_format:
            file_format = ObsMetadata.get_information_file_format(filename)

        bu = unquote(filename)

        if gitLabFile.isRemote(bu):
            base_uri = unquote(urlparse(bu).path)
            # loader = JsonLoader()
            loader = YAMLLoader()
            jsonstr = loader.get_remote_json(bu, base_uri=base_uri,
                                              datapath=datapath)
            return yamlref.loads(jsonstr, base_uri=base_uri, datapath=datapath)
        else:
            base_uri = Path(bu).as_uri()
            try:
                with open(unquote(filename), "r") as f:
                    return yamlref.load(f, base_uri=base_uri,
                                        datapath=datapath)
            except FileNotFoundError:
                msg = f'File not found: {filename}'
                logger.exception(msg)
                raise
            except (IOError, OSError):
                msg = f'Input/Output error with file: {filename}'
                logger.exception(msg)
                raise

    def read_json_yaml_ref(filename, datapath, file_format=None):
        """
        Reads a JSON or YAML file using jsonReference

        Like read_json_yaml_ref, but does not look for files in
        OBSINFO_DATAPATH
        $ref within the data files without absolute or relative path will be
        still looked for in OBSINFO_DATAPATH

        Args:
            filename (str): filename
            datapath (:class:`.Datapath`): object to store list of
            directories to search info files. Used as a dummy.
            file_format (str): "YAML" or "JSON"
        Returns:
            (dict): JSON or YAML parsed information files
        Raises:
            (JSONDecodeError): problem with JSON read
            (FileNotFoundError): file not found
            (IOError): File input/output erre
        """
        if not file_format:
            file_format = ObsMetadata.get_information_file_format(filename)

        bu = unquote(filename)
        base_uri = Path(bu).as_uri()

        try:
            with open(filename, "r") as f:
                a = yamlref.load(f, base_uri=base_uri, datapath=datapath)
            # if not isinstance(a, list):
            #     raise FileNotFoundError(filename)
            return a
        except FileNotFoundError as error:
            msg = f'File not found: {error.args}'
            logger.exception(msg)
            raise FileNotFoundError(msg)
        except IOError as error:
            msg = f'Input/Output error with file: {error.args}'
            logger.exception(msg)
            raise IOError(msg)
        except OSError as error:
            msg = f'OS error with file: {error.args}'
            logger.exception(msg)
            raise OSError(msg)
        except Exception as error:
            raise error

    @staticmethod
    def read_info_file(filename, datapath, remote=False, validate=True,
                       file_format=None, verbose=False,  quiet=False,
                       debug=False):
        """
        Reads an information file

        Args:
            filename (str): filename
            datapath (:class:`.Datapath`): stores list of directories to
                search info files
            validate (bool): validate before reading
            remote (bool): whether to use absolute/relative path locally
                or OBSINFO_DATAPATH
            file_format (str):"YAML" or "JSON"
            verbose (bool): say more
            quiet (bool): say nothing
            debug (bool): print timing information

        Returns:
            (:class:`ObsMetadata`): JSON or YAML parsed info files
        """
        # print('read_info_file() START')
        if quiet is True:
            verbose = False
        if validate:
            if debug is True:
                tic = perf_counter()
            file_type = ObsMetadata.get_information_file_type(filename)
            if debug is True:
                tic = _timing_message(tic, 'ObsMetadata.read_info_file: get_information_file_type()')
            if file_type is None:
                logger.error(f'Could not determine type of file {filename}')
            msg = f'Validating {file_type} file: {filename}'
            logger.info(msg)
            if verbose:
                print(msg)
            ObsMetadata().validate(str(filename), DEFAULT_SCHEMA_PATH,
                                   remote=remote, verbose=verbose, quiet=quiet,
                                   debug=debug)
            if debug is True:
                tic = _timing_message(tic, 'ObsMetadata.read_info_file: validate()')
        else:
            msg = f"Reading {filename}"
            logger.info(msg)
            if verbose:
                print(msg)

        if remote:
            return ObsMetadata.read_json_yaml_ref_datapath(filename, datapath,
                                                           file_format)
        else:
            return ObsMetadata.read_json_yaml_ref(filename, datapath,
                                                  file_format)

    def get_configured_modified_base(self, higher_modifs={},
                                     accept_extras=False):
        """
        Return a fully configured and modified base_dict

        Handles ``base``, ``modifications`` and ``configuration``
        fields in self and higher_modifs.  Doest not handle any of
        these subelements in ``modifications`` or ``configuration``: they
        simply get added into ``base`` using the ``safe_update()`` method.

        Values in higher-modifs outrank those in self.  Modifications outrank
        configurations.  Uses safe_update() to only change specified elements.

        Args:
            self: base-configuration-modification dictionary.
                  Must have "base", can have "configuration" and
                  "modification" AND NOTHING ELSE.
            higher_modifs (dict or :class:`ObsMetadata`): modifications
                dictionary.  Can have "base", "configuration" and/or
                "modification" AND NOTHING ELSE
            accept_extras (bool): accept other keys than 'base', 'configuration',
                and 'modifications'.  These will be put into the output
                dict as is if they don't duplicate an existing key.
        Returns:
                base_dict (:class:`ObsMetadata`): fully configured and modified
                    attribute dictionary
        Raises:
            ValueError: if self or higher_modifs contain keys other than
                "base", "configuration" and/or "modification"
        """
        caller = inspect.stack()[1]
        a = self.copy()
        base_dict = self.__class__(a.pop('base', {}))
        configuration = base_dict.pop('configuration_default', None)
        if 'configuration' in a:
            configuration = a.pop('configuration')
        modifs = self.__class__(a.pop('modifications', {}))
        if len(list(a.keys())) > 0 and accept_extras==False:
            raise ValueError('base-configuration-modification dict '
                             f'has leftover keys: {a}')

        # Update with higher-level modifications
        b = self.__class__(higher_modifs.copy())
        if 'base' in b:
            base_dict = self.__class__(b.pop("base"))
            configuration = base_dict.pop('configuration_default', None)
            modifs = ObsMetadata({})
        if 'configuration' in b:
            configuration = b.pop("configuration")
        if "modifications" in b:
            high_modifs = b.pop("modifications")
            # modifications can also specify BASE and CONFIGURATION
            if 'base' in high_modifs:
                base_dict = self.__class__(high_modifs.pop("base"))
                configuration = base_dict.pop('configuration_default', None)
                modifs = ObsMetadata({})
            if 'configuration' in high_modifs:
                configuration = high_modifs.pop('configuration')
            modifs.safe_update(high_modifs)
        if len(list(b.keys())) > 0:
            raise ValueError('higher_level base-configuration-modification '
                             f'dict had leftover elements: {b}')

        # Configure, then modify
        configs = base_dict.pop("configurations", None)
        if configuration is not None:
            if configs is None:
                raise ValueError(f"'{configuration}' configuration requested "
                                 f"by {Path(caller.filename).name}, but no "
                                 f"configurations were specified. {base_dict=}")
            if configuration not in configs:
                raise ValueError(
                    f"Requested configuration ('{configuration}') doesn't "
                    f"match specified configurations: {list(configs.keys())}")
            base_dict.safe_update(configs[configuration])
            base_dict['configuration'] = configuration
        base_dict.safe_update(modifs)
        if len(list(a.keys())) > 0:
            base_dict.safe_update(a, warn_crush=True)

        return base_dict

    def safe_update(self, update_dict, allow_overwrite=True, warn_crush=False):
        """
        Update that only changes explicitly specfied fields

        Drills recursively through dicts inside the dict, only changing fields
        which are specified in update_dict.  Lists are completely replaced,
        however, to avoid ambiguity.

        Args:
            update_dict (dict or :class:`ObsMetadata`): dictionary containing
                fields to update
            allow_overwrite (bool): allow a field that was originally a dict
                to be overwritten by a field that is not a dict.  Same for lists.
            warn_crush (bool): write out a warning when a value is replaced
        """
        if not isinstance(update_dict, dict):
            logger.error('update_dict is not a dict')
            raise TypeError('update_dict is not a dict')
        if not isinstance(update_dict, self.__class__):
            update_dict = self.__class__(update_dict)
        for key, value in update_dict.items():
            # Change any dict into ObsMetadata
            if isinstance(value, dict) and not isinstance(value, self.__class__):
                value = self.__class__(value)
            if key.startswith(overwrite_string):
                key = key[len(overwrite_string):]  # Strip overwrite_string
                if key in self:
                    logger.info(f'Overwrite ordered for {key=}')
                else:
                    logger.info(f'Overwrite ordered for non-existant {key=}')
                self[key] = value
                continue  # Go to next loop iteration
            if key not in self:  # Add new key and its value
                self[key] = value
                continue  # Go to next loop iteration
            # Key exists in self and not forced overwrite
            if isinstance(self[key], dict):  # If original item is a dict
                # if value is also a dictionary, update it
                if isinstance(value,  dict):
                    # if replacement value is a dictionary, recurse
                    self[key].safe_update(value,
                                          allow_overwrite=allow_overwrite,
                                          warn_crush=warn_crush)
                else:
                    # if replacement value is not a dictionary
                    if allow_overwrite:  # replace & warn
                        self[key] = value
                        logger.warning(f'dict field "{key}" '
                                       'was replaced by a non-dict')
                    else:  # reject & warn
                        logger.warning(
                            f'replacement field "{key}" was not inserted '
                            'into original because original was a dict '
                            'but replacement was not')
            elif isinstance(self[key], list):  # If original item is a list
                if isinstance(value,  list):   # If replacement is also a list
                    # Replace the list
                    self[key] = value
                    logger.debug(f'"{key}": {len(self[key])}-element list replaced by {len(value)}-element list')
                else:
                    # if replacement value is not a list
                    if allow_overwrite:  # replace & warn
                        self[key] = value
                        msg = f'field "{key}" was a list, replaced by a non-list'
                        logger.warning(msg)
                    else:  # reject & warn
                        msg = (f'replacement field "{key}" not inserted '
                               'into original because original was a list '
                               'but replacement was not')
                        logger.warning(msg)
            else:
                # Replace existing others
                if key in self and warn_crush is True:
                    msg = f'replacing self["{key}"]: was {self[key]}, now {value}'
                    logger.warning(msg)
                self[key] = value

    def copy(self):
        return ObsMetadata(super().copy())

    def _convert_to_obsmetadata(self):
        """
        Make all contained dictionaries objects of :class: `.ObsMetadata`
        """
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = self.__class__(value)
            elif isinstance(value, list):
                for x in value:
                    if isinstance(x, dict):
                        x = self.__class__(x)

    @staticmethod
    def _read_schema_file(base_file, schemas_path=None, debug=False):
        if debug is True:
            tic = perf_counter()
        if schemas_path is None:
            schemas_path = DEFAULT_SCHEMA_PATH
        schema_fullpath = PurePath(schemas_path) / base_file
        base_uri = unquote(PurePath(schema_fullpath).as_uri())
        schema_datapath = Datapath(schemas_path)
        if debug is True:
            tic = _timing_message(tic, 'obsmetadata:_read_schema_file(): Datapath')
        try:
            with open(schema_fullpath, "r") as f:
                try:
                    s = f.read()
                except Exception:
                    logger.exception()
                    return False, False
                if debug is True:
                    tic = _timing_message(tic, 'obsmetadata:_read_schema_file(): f.read())')
                try:
                    schema = yamlref.loads(
                        s, base_uri=base_uri, jsonschema=True,
                        datapath=schema_datapath, recursive=True)
                except json.decoder.JSONDecodeError as e:
                    msg = ("JSONDecodeError: Error loading JSON schema "
                           f"file: {schema_fullpath}")
                    logger.exception(msg)
                    logger.error(str(e))
                    return False, False
                except BaseException as e:
                    msg = "{}: Error loading JSON schema file: {}".format(
                        type(e), schema_fullpath)
                    logger.exception(msg)
                    logger.error(e)
                    return False, False
                if debug is True:
                    tic = _timing_message(tic, 'obsmetadata:_read_schema_file(): yamlref_loads())')
        except FileNotFoundError:
            msg = f'File not found: {schema_fullpath}'
            logger.exception(msg)
            raise FileNotFoundError(msg)
        except (IOError, OSError):
            msg = f'Input/Output error with file: {schema_fullpath}'
            logger.exception(msg)
            raise
        if debug is True:
            tic = _timing_message(tic, 'obsmetadata:_read_schema_file(): Done')
        return schema, schema_fullpath

    @staticmethod
    def _report_errors(instance, schema, schema_fullpath=Path(""),
                       verbose=False, quiet=False, check_schema=True):
        """
        Lazily report all errors in the instance vis-a-vis the schema

        ASSUMES DRAFT7 SCHEMA (I couldn't get it to work otherwise)
        """
        msg = f"schema =   {schema_fullpath.name}"
        logger.info(msg)
        if verbose:
            print(msg)
        if check_schema:
            if not ObsMetadata.check_schema(schema, verbose, quiet):
                return False

        msg = "\tTesting instance ..."
        logger.info(msg)
        if verbose:
            print(msg, end="")

        v = jsonschema.Draft7Validator(schema)

        if not v.is_valid(instance):
            errors = sorted(v.iter_errors(instance), key=lambda e: e.path)
            for error in errors:
                err_path = ''.join([f"['{e}']" for e in error.path])
                msg = f"{err_path}: {error.message} \tFAILED"
                logger.error(msg)  # errors get printed to console
            return False
        else:
            if verbose:
                print("OK")
            logger.info("OK")
            return True

def _timing_message(tic=None, message=None):
    """
    Returns perf_timer()
    
    If tic and message provided, writes out time elapsed message
    """
    toc = perf_counter()
    if message is not None:
        print(f'{toc-tic:.1f} seconds: {message}')
    return toc

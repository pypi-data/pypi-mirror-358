from pathlib import Path
from urllib.parse import urlparse

from synapse_sdk.i18n import gettext as _
from synapse_sdk.utils.storage.registry import STORAGE_PROVIDERS


def get_storage(connection_param: str | dict):
    """Get storage class with connection param.

    Args:
        connection_param (str | dict): The connection param for the Storage provider.

    Returns:
        BaseStorage: The storage class object with connection param.
    """
    if connection_param is None:
        raise ValueError(_('Connection parameter cannot be None'))

    storage_scheme = None
    if isinstance(connection_param, dict):
        if not connection_param:
            raise ValueError(_('Connection parameter dictionary cannot be empty'))

        # Check if there's a URL field that should take priority
        if 'url' in connection_param and connection_param['url']:
            storage_scheme = urlparse(connection_param['url']).scheme
        elif 'provider' in connection_param:
            storage_scheme = connection_param['provider']
            if not storage_scheme:
                raise ValueError(_('Provider name cannot be empty'))
        else:
            raise ValueError(_('Dictionary must contain either "url" or "provider" field'))
    elif isinstance(connection_param, str):
        if not connection_param or connection_param.isspace():
            raise ValueError(_('Connection parameter string cannot be empty'))

        parsed_url = urlparse(connection_param)
        storage_scheme = parsed_url.scheme
        if not storage_scheme:
            raise ValueError(_('Invalid URL format: no scheme found'))
    else:
        raise TypeError(_('Connection parameter must be a string or dictionary'))

    if storage_scheme not in STORAGE_PROVIDERS:
        supported_schemes = ', '.join(STORAGE_PROVIDERS.keys())
        raise ValueError(
            _('Storage provider "{}" not supported. Supported providers: {}').format(storage_scheme, supported_schemes)
        )

    return STORAGE_PROVIDERS[storage_scheme](connection_param)


def get_pathlib(storage_config: str | dict, path_root: str) -> Path:
    """Get pathlib object with synapse-backend storage config.

    Args:
        storage_config (str | dict): The storage config by synapse-backend storage api.
        path_root (str): The path root.

    Returns:
        pathlib.Path: The pathlib object.
    """
    storage_class = get_storage(storage_config)
    return storage_class.get_pathlib(path_root)


def get_path_file_count(storage_config: str | dict, path_root: str) -> int:
    """Get the file count in the path.

    Args:
        storage_config (str | dict): The storage config by synapse-backend storage api.
        path (str): The path.

    Returns:
        int: The file count in the path.
    """
    storage_class = get_storage(storage_config)
    pathlib_obj = storage_class.get_pathlib(path_root)
    return storage_class.get_path_file_count(pathlib_obj)


def get_path_total_size(storage_config: str | dict, path_root: str) -> int:
    """Get total size of the files in the path.

    Args:
        storage_config (str | dict): The storage config by synapse-backend storage api.
        path (str): The path.

    Returns:
        int: The total size of the files in the path.
    """
    storage_class = get_storage(storage_config)
    pathlib_obj = storage_class.get_pathlib(path_root)
    return storage_class.get_path_total_size(pathlib_obj)

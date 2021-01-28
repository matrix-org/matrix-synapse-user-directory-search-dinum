from typing import Dict, Tuple
from unittest.mock import Mock

from synapse.module_api import ModuleApi

from matrix_synapse_user_directory_search_dinum.user_directory_search import (
    ModuleConfig,
    UserDirectorySearchModule,
)


def create_user_directory_search_module_with_config(
    config: Dict,
) -> Tuple[UserDirectorySearchModule, Mock, ModuleConfig]:
    """Create a UserDirectorySearchModule with a given config and a mock'd ModuleApi

    Args:
        config: The configuration dictionary to pass to
            UserDirectorySearchModule.parse_config.

    Returns:
        A tuple containing:
            * The initialised UserDirectorySearchModule.
            * The ModuleApi mock. To be used to check calls to ModuleApi that the
                module may make.
            * The ModuleConfig object returned by parse_config.
    """
    # Parse the given config dict into a ModuleConfig object
    parsed_config = UserDirectorySearchModule.parse_config(config)

    # Create a mock to act as Synapse's ModuleApi class
    module_api_mock = Mock(spec=ModuleApi)

    # Create and return a UserDirectorySearchModule instance with this config
    return (
        UserDirectorySearchModule(parsed_config, module_api_mock),
        module_api_mock,
        parsed_config,
    )

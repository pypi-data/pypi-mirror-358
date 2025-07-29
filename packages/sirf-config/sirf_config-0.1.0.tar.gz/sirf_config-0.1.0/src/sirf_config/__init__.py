"""
SIRF Configuration Management

A Python package for managing scanner and reconstruction configurations
for SIRF SPECT/PET workflows.
"""

from .config_loader import (
    ConfigLoader,
    create_reconstruction_args,
    get_y90_spect_params,
    get_y90_pet_params,
)
from .utils import (
    get_default_config_dir,
    validate_config_files,
    create_user_config_template,
)

__version__ = "0.1.0"
__author__ = "Sam Porter"
__email__ = "sam.porter.18@ucl.ac.uk"

__all__ = [
    "ConfigLoader",
    "create_reconstruction_args", 
    "get_y90_spect_params",
    "get_y90_pet_params",
    "get_default_config_dir",
    "validate_config_files",
    "create_user_config_template",
]
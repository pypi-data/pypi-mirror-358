"""Top-level package for frogml core"""

from frogml.core.inner.di_configuration import wire_dependencies
from frogml.core.model_loggers.artifact_logger import (  # noqa: F401,E501
    load_file,
    log_file,
)
from frogml.core.model_loggers.data_logger import load_data, log_data  # noqa: F401

_container = wire_dependencies()

from .main import ReverseProxy
from .utils.dummy_server import DummyServer, shutdown_dummy_servers
from .utils.logger import setup_logging as _setup_logging

_setup_logging()

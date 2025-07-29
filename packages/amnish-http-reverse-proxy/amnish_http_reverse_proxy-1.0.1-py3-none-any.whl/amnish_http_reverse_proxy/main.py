## Features needed

# 1. Request forwarding
# 2. Security like - SSL termination, filtering malicious requests.
# 3. Caching
# 4. Load balancing

# Interface to configure and spin up the reverse proxy


from amnish_http_reverse_proxy.utils.dummy_server import DummyServer
from amnish_http_reverse_proxy.reverse_proxy import ReverseProxy
import sys
import signal
from dotenv import load_dotenv
from amnish_http_reverse_proxy.utils.logger import logger

# Load the local environment variables
load_dotenv()

# Driver code for testing purposes
def main():
    try:
        # Spin up the dummy servers
        dummy_ports = [3001, 3002, 3003]
        DummyServer.run_dummy_servers(dummy_ports)

        # Start the actual proxy server
        proxy = ReverseProxy(targets=[f"http://localhost:{p}" for p in dummy_ports])
        proxy.run(port=8080)

    except Exception as error:
        logger.error(f"Unexpected error: {error}. Shutting down...")

if __name__ == "__main__":
    main()

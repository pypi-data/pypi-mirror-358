from flask import Flask, request, jsonify
from multiprocessing import Process
from .logger import logger
import signal
import sys

class DummyServer:
    """
    A utility to spin up dummy servers for testing the behavior of reverse proxy server
    """
    def __init__(self, port: int):
        self.port = port # Port will act as the unique identifier of a dummy server
        self.process = None

    def _run_server(self):
        app = Flask(__name__)

        @app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE"])
        @app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
        def echo(path):
            return jsonify({
                "server": self.port,
                "path": path,
                "method": request.method,
                "headers": dict(request.headers),
                "args": request.args,
                "form": request.form,
                "json": request.get_json(silent=True),
                "data": request.get_data(as_text=True)
            })

        app.run(port=self.port)

    def start(self):
        logger.info(f"Starting dummy server on port {self.port}")
        self.process = Process(target=self._run_server)
        self.process.start()

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process.join()

    @staticmethod
    def run_dummy_servers(ports: list[int]):
        servers = [DummyServer(port) for port in ports]

        try:
            # Start dummy servers
            for s in servers:
                s.start()

            # Register signal handler for clean shutdown
            signal.signal(signal.SIGINT, lambda sig, frame: shutdown_dummy_servers(servers))

            return servers
        except Exception as error:
            logger.error(f"Error while spinning dummy servers: {error}. Shutting down...")
            # Clean all dummy servers
            shutdown_dummy_servers(servers)

def shutdown_dummy_servers(servers: list[DummyServer]):
    logger.info("Cleaning up dummy servers...")
    for s in servers:
        s.stop()

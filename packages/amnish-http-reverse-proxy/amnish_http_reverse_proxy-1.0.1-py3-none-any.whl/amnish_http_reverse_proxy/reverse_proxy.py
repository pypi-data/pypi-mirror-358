from typing import Optional, Callable
from flask import Flask, request, Response as FlaskResponse, Request, jsonify
from .utils.logger import logger
import logging
from .lib.load_balancing.round_robin import round_robin_generator
import requests
from .lib.cache import TTLCache
import hashlib

class ReverseProxy:
    """
    Runs a web server that routes client requests to a set of web servers.

    Takes care of:
    1. Security
    2. Load balancing
    3. Caching
    """
    DEFAULT_PORT = 8080

    def __init__(self, targets: Optional[list[str]], ttl_seconds = 5, request_filter: Optional[Callable[[Request], bool]] = None):
        self.targets = targets if targets is not None else []
        self.round_robin_generator = round_robin_generator(targets)
        self.cache = TTLCache(ttl_seconds) # A Time-to-live cache that expires entries after 30 seconds of existence
        self.request_filter = request_filter
        self.app = self._setup_server_app()


    def run(self, port: Optional[int] = None):
        # Validate the arguments and run the proxy server
        port = port if port is not None else ReverseProxy.DEFAULT_PORT
        debug_mode = logger.level == logging.DEBUG
        self.app.run(port=port, debug=debug_mode)

    def test_client(self):
        return self.app.test_client()

    def _setup_server_app(self) -> Flask:
        app = Flask(__name__)

        @app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE"])
        @app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
        def index(path: str = ""):
            return self._handle_request(request)

        app.logger.setLevel(logger.level)

        return app


    def _handle_request(self, req: Request) -> FlaskResponse:
        """
            This holds the core logic of the reverse proxy, and works as follows:

            1. Executes the security checks against all incoming requests.
            2. Checks if the response to incoming request is cached.
            3. Forwards the request to the appropriate server using the "Round Robin" strategy.
            4. Caches the response with a configured TTL.
        """
        # Check if the request is secure enough to be forwarded
        if not self._security_check(req):
            logger.warning(f"Blocked request due to failing security check: {req.method} {req.path}")
            fail_status = 405
            return jsonify({"error": "Request does not comply with security policies", "status": fail_status}), fail_status

        # Return the cached response if available
        cached_response = self._get_cached_response(req)
        if cached_response is not None:
            logger.debug(f"Cache hit: {req}")
            return cached_response

        # Forward the request to next target server
        response = self._forward_request(req)

        # Cache the returned response
        self._cache_response(req, response)

        return response

    def _forward_request(self, req: Request) -> FlaskResponse:
        """
        Finds the next target server using "Round Robin" algorithm, forwards the request to it, and returns the response.
        https://www.vmware.com/topics/round-robin-load-balancing

        Args:
            request (Request): The request to be forwarded

        Returns:
            FlaskResponse: returned from the target server
        """
        # Find the next target server to route the request to
        target_url = next(self.round_robin_generator)
        full_url = f"{target_url.rstrip('/')}/{req.path.lstrip('/')}"

        try:
            # Forward the request with method, headers, and data
            # and return the response for target server
            logger.info(f'Forwarding request to server at "{target_url}"')
            forwarded_response = requests.request(
                method=req.method,
                url=full_url,
                headers={key: value for key, value in req.headers if key.lower() != 'host'},
                data=req.get_data(),
                cookies=req.cookies,
                allow_redirects=False,
            )

            return FlaskResponse(
                response=forwarded_response.content,
                status=forwarded_response.status_code,
                headers=dict(forwarded_response.headers),
            )
        except requests.RequestException as e:
            logger.error(f"Request forwarding failed: {e}")
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/502
            return FlaskResponse("Upstream request failed", status=502)

    def _generate_cache_key(self, req: Request) -> str:
        body = req.get_data(as_text=False) or b""
        key_string = f"{req.method}:{req.path}:{req.query_string.decode()}"
        combined = key_string.encode() + b"::" + body

        # Use a hash to ensure fixed-length keys (and avoid issues with large payloads)
        return hashlib.sha256(combined).hexdigest()

    def _get_cached_response(self, req: Request) -> Optional[FlaskResponse]:
        cache_key = self._generate_cache_key(req)
        raw_cached_response = self.cache.get(cache_key)

        if raw_cached_response is None:
            return None


        cached_response = self._build_flask_response(raw_cached_response)
        return cached_response

    def _cache_response(self, req: Request, res: FlaskResponse):
        cache_key = self._generate_cache_key(req)

        self.cache.set(cache_key, self._build_cacheable_response(res))

    @staticmethod
    def _build_cacheable_response(response: FlaskResponse) -> dict:
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.get_data(),
        }

    @staticmethod
    def _build_flask_response(cached_response: dict) -> FlaskResponse:
        return FlaskResponse(
            response=cached_response["content"],
            status=cached_response["status_code"],
            headers=cached_response["headers"],
        )

    def _security_check(self, req: Request) -> bool:
        """
        Checks if the request is suitable to forward to origin servers

        Args:
            req (Request): The request to be evaluated

        Returns:
            bool: `True` if the request passes security checks, `False` if request is determined to be malicious
        """

        if self.request_filter is not None:
            return self.request_filter(req)

        # TODO: The current security check is very simple and is not sufficient for production-grade usage.
        #       But this is good enough for demonstration purposes, since users can configure a custom security function via `self.request_filter`.
        allowed_methods = ["GET", "PUT", "POST", "DELETE"]
        return req.method in allowed_methods


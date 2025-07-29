"""
Test suite for `ReverseProxy` class.

Had to refer my own blog post for some parts 😄
https://dev.to/amnish04/testing-in-python-4ne7
"""

import pytest
from amnish_http_reverse_proxy import ReverseProxy, DummyServer, shutdown_dummy_servers
from amnish_http_reverse_proxy.utils.logger import logger
import json
import time

TTL_CACHE_DURATION=1 # Seconds

@pytest.fixture
def client():
    # Run dummy servers in background to test against
    dummy_ports = [3001, 3002, 3003]
    dummy_servers = DummyServer.run_dummy_servers(dummy_ports)

    # Give the servers time to start
    # TODO: This is not the best solution, could result in race conditions
    time.sleep(1)

    targets = targets = [f"http://localhost:{port}" for port in dummy_ports]
    proxy_server = ReverseProxy(targets=targets, ttl_seconds=TTL_CACHE_DURATION)

    with proxy_server.test_client() as client:
        yield client

    # Manually clean up dummy servers after tests finish running
    logger.info("Cleaning up dummy servers")
    shutdown_dummy_servers(dummy_servers)


def test_load_balancing(client):
    """
    1. Sends requests to same route with 4 different HTTP methods, without waiting for TTL cache to expire.
    2. Expects routing to different server each time (we have 3 dummy target servers that rotate using "Round Robin")
    """
    # Make first request, should go to first server
    response1 = client.get("/resource")
    assert response1.status_code == 200
    response1_body = json.loads(response1.get_data())
    assert response1_body["server"] == 3001

    # Make second request, should go to second server
    response2 = client.put("/resource")
    assert response2.status_code == 200
    response2_body = json.loads(response2.get_data())
    assert response2_body["server"] == 3002

    # Make third request, should go to third server
    response3 = client.post("/resource")
    assert response3.status_code == 200
    response3_body = json.loads(response3.get_data())
    assert response3_body["server"] == 3003

    # Make fourth request, should go back to first server
    response4 = client.delete("/resource")
    assert response4.status_code == 200
    response4_body = json.loads(response4.get_data())
    assert response4_body["server"] == 3001

def test_caching(client):
        """
        1. Sends 3 requests to proxy server after 2 seconds each, which is the TTL duration for cache.
        2. Verifies the request returns from a different server each time (we have 3 dummy target servers using "Round Robin")
        3. Sends 4th request without waiting for TTL duration, expect the same server response
        """

        # Make first request, should go to first server
        response1 = client.get("/resource")
        assert response1.status_code == 200
        response1_body = json.loads(response1.get_data())
        assert response1_body["server"] == 3001

        # Wait for cached response to expire
        time.sleep(TTL_CACHE_DURATION)

        # Make second request, should go to second server
        response2 = client.get("/resource")
        assert response2.status_code == 200
        response2_body = json.loads(response2.get_data())
        assert response2_body["server"] == 3002

        # Wait for cached response to expire
        time.sleep(TTL_CACHE_DURATION)

        # Make third request, should go to third server
        response3 = client.get("/resource")
        assert response3.status_code == 200
        response3_body = json.loads(response3.get_data())
        assert response3_body["server"] == 3003

        # Make fourth request without waiting for cache to expire
        # Expect the same server
        response4 = client.get("/resource")
        assert response4.status_code == 200
        response4_body = json.loads(response4.get_data())
        assert response4_body["server"] == 3003

def test_security(client):
    """
    1. Sends requests with illegal methods (anything except ["GET", "POST", "PUT", "DELETE"] is illegal based on default security policy)
    2. Expect failure with a 405 - Method not allowed
    """
    # Send an HTTP "TRACE" request
    response1 = client.trace("/resource")
    logger.info(response1)
    assert response1.status_code == 405

    # Send an HTTP "HEAD" request
    response2 = client.head("/resource")
    assert response2.status_code == 405


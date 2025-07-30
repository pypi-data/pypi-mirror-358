import socket
import sys
import types
import pytest

import ub


def test_check_port_available():
    # Pick a high port number that is likely to be free
    port = 54321
    assert ub.check_port_available("127.0.0.1", port)
    # Bind to the port, then check again
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", port))
    try:
        assert not ub.check_port_available("127.0.0.1", port)
    finally:
        s.close()
    # After closing, should be available again
    assert ub.check_port_available("127.0.0.1", port)


def test_find_available_port():
    port = ub.find_available_port(54321, host="127.0.0.1", max_attempts=5)
    assert isinstance(port, int)
    assert 54321 <= port < 54326
    assert ub.check_port_available("127.0.0.1", port)

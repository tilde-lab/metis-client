"Test MetisError"

from metis_client.exc import MetisError


def test_error_string():
    "Test MetisError"
    status = -1234
    message = "mEsSaGe"
    err = MetisError(status=status, message=message)
    assert str(status) in str(err), "Status should be printed"
    assert str(message) in str(err), "Message should be printed"

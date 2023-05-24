from . import test_base, test_example_requests


def test_run(test_client):
    test_base.test_ping(test_client)
    test_base.ping_thread(test_client)
    test_base.close(test_client)
    test_base.test_reconnect(test_client)

    test_example_requests.test_uuid(test_client)

    # base.shutdown(test_client)

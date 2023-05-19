from example_protocol.example_client import Client
from .fixture_example_client import test_client


def test_uuid(test_client: Client):
    title = "Test Title"
    response = test_client.get_uuid(title)
    assert response.data.title == title
    assert response.data.uuid is not None

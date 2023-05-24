from .fixture_example_client import test_client, Client



def test_uuid(test_client: Client):
    title = "Test Title"
    response = test_client.get_uuid(title)
    assert response.data.title == title
    assert response.data.uuid is not None

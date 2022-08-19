import responses
from _pytest.python_api import raises

from booker.pantry import upload, get_url

test_id = "15e240e3-5f4c-413b-bf7b-88c8e0dd10ef"


def test_no_pantry_id_raises_exception():
    with raises(Exception):
        upload("", "", [])


def test_url():
    assert get_url("a", "b") == "https://getpantry.cloud/apiv1/pantry/a/basket/b"


@responses.activate
def test_pantry_upload_succeeds(mock_single_book):
    responses.add(
        responses.POST,
        "https://getpantry.cloud/apiv1/pantry/a/basket/b",
        status=200,
        json="Your Pantry was updated with basket: b!",
    )
    response = upload("a", "b", mock_single_book)
    assert response == '"Your Pantry was updated with basket: b!"'


@responses.activate
def test_pantry_upload_fails_server_error(mock_single_book):
    responses.add(
        responses.POST,
        "https://getpantry.cloud/apiv1/pantry/a/basket/b",
        status=500,
        json="pantry is out",
    )
    with raises(Exception) as context:
        upload("a", "b", mock_single_book)
    assert (
        "Pantry is experiencing internal issues. Error Code: 500"
        == context.value.__str__()
    )


@responses.activate
def test_pantry_upload_fails_server_error(mock_single_book):
    responses.add(
        responses.POST,
        "https://getpantry.cloud/apiv1/pantry/a/basket/b",
        status=400,
        json="Failed to update: b",
    )
    with raises(Exception) as context:
        upload("a", "b", mock_single_book)
    assert '"Failed to update: b". Error Code: 400' == context.value.__str__()

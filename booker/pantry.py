import json

import requests

from bs4 import BeautifulSoup

from booker.bookerdataclasses import BookList
from booker.control import outcome
from booker.error import EXPORT_ERROR

BASE_URL = "https://getpantry.cloud/apiv1/pantry"
headers = {"Content-Type": "application/json"}


def get_url(pantry_id: str, basket_id: str) -> str:
    return f"{BASE_URL}/{pantry_id}/basket/{basket_id}"


@outcome(
    requires=("pantry_id", "basket_id", "book_list"),
    returns="response",
    registers={Exception: EXPORT_ERROR},
)
def upload(pantry_id: str, basket_id: str, book_list: BookList) -> str:
    if pantry_id.strip() == "":
        raise Exception(f"no pantry id. Provide a pantry id with the --pantry-id flag.")

    contents = json.dumps({"reading_list": book_list})
    url = get_url(pantry_id, basket_id)
    res = requests.post(url, headers=headers, data=contents)
    status_code = res.status_code
    text = BeautifulSoup(res.text, features="html.parser").getText().split("\n")
    response = ". ".join(text)

    if 200 <= status_code <= 399:
        return response
    elif status_code >= 500:
        raise Exception(
            f"Pantry is experiencing internal issues. Error Code: {status_code}"
        )
    else:
        raise Exception(f"{response}. Error Code: {status_code}")

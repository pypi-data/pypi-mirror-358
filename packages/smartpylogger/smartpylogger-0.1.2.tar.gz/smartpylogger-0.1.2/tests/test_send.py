import requests

API_URL = "http://localhost:8500/mock"

def test_post():
    payload = {"foo": "JS", "number": 123}
    response = requests.post(API_URL, json=payload)
    print("Status code:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    test_post()
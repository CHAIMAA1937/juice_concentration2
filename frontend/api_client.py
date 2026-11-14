
import requests

API_URL = "http://127.0.0.1:8000"


def register_user(username, email, password, confirm_password):
    url = f"{API_URL}/register"

    data = {
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": confirm_password
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        return response
    except requests.RequestException:
        return None


def login_user(username_or_email, password):
    url = f"{API_URL}/login"

    data = {
        "username_or_email": username_or_email,
        "password": password
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        return response
    except requests.RequestException:
        return None


def get_current_user(token):
    url = f"{API_URL}/me"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        return response
    except requests.RequestException:
        return None


def logout_user(token):
    url = f"{API_URL}/logout"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            timeout=10
        )
        return response
    except requests.RequestException:
        return None

def save_calculation(token, results):
    url = f"{API_URL}/calculations"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.post(
            url,
            json={"results": results},
            headers=headers,
            timeout=10
        )
        return response
    except requests.RequestException:
        return None


def get_calculations(token):
    url = f"{API_URL}/calculations"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
        return response
    except requests.RequestException:
        return None


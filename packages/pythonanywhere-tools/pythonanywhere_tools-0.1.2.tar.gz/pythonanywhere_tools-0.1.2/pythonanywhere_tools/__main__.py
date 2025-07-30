import datetime as dt
import os
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

load_dotenv()


class PythonAnywhereTool:
    """
    Example:
    username = os.getenv("USERNAME")
    python_anywhere_tool = PythonAnywhereTool(username=username)

    try:
        python_anywhere_tool.login_pythonanywhere_website()
        python_anywhere_tool.extend_python_anywhere()
        print("Success extending PythonAnywhere 3 months freetier.")
    except:
        raise Exception
    """

    BASE_URL = "https://www.pythonanywhere.com"
    LOGIN_URL = f"{BASE_URL}/login/"
    api_reload_url = f"{BASE_URL}/api/v0/user/#/webapps/#.pythonanywhere.com/reload/"
    extend_url = (
        "https://www.pythonanywhere.com/user/#/webapps/#.pythonanywhere.com/extend"
    )
    web_app_tab_type = "%23tab_id_#_pythonanywhere_com"

    def __init__(self, username):
        self.client = requests.Session()
        self.session_id = ""
        self.csrftoken = ""
        self.fill_username_in_urls(username)

    def fill_username_in_urls(self, username):
        self.api_reload_url = self.api_reload_url.replace("#", username)
        self.extend_url = self.extend_url.replace("#", username)
        self.web_app_tab_type = self.web_app_tab_type.replace("#", username)

    def login_pythonanywhere_website(self) -> None:
        self.client.get(self.LOGIN_URL)
        if "csrftoken" in self.client.cookies:
            self.csrftoken = self.client.cookies["csrftoken"]
        else:
            # older versions
            self.csrftoken = self.client.cookies["csrf"]

        login_data = {
            "auth-username": os.getenv("AUTH_USERNAME"),
            "auth-password": os.getenv("AUTH_PASSWORD"),
            "csrfmiddlewaretoken": self.csrftoken,
            "login_view-current_step": "auth",
        }
        self.client.post(
            self.LOGIN_URL, data=login_data, headers=dict(Referer=self.LOGIN_URL)
        )
        self.session_id = self.client.cookies["sessionid"]

    def extend_python_anywhere(self) -> None:
        headers = {
            "Host": "www.pythonanywhere.com",
            "Referer": "https://www.pythonanywhere.com/user/manuelseromenho/webapps/",
            "Cookie": (
                f"web_app_tab_type={self.web_app_tab_type}; "
                f"cookie_warning_seen=True;"
                f"csrftoken={self.csrftoken};"
                f"sessionid={self.session_id};"
            ),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        r = self.client.post(
            self.extend_url,
            data={"csrfmiddlewaretoken": self.csrftoken, "next": "/"},
            headers=headers,
        )

        # TODO improve logging here
        print(f"status_code: {r.status_code}, reason: {r.reason}, ok->{r.ok}")
        portugal_datetime = dt.datetime.now(ZoneInfo("Europe/Lisbon"))
        print(f"Portugal time: {portugal_datetime}")

    def api_reload_python_anywhere(self) -> None:
        token = os.getenv("API_TOKEN")

        requests.post(
            self.api_reload_url,
            headers={"Authorization": "Token {token}".format(token=token)},
        )

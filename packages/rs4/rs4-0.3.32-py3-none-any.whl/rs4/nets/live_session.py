from requests import Session
from urllib.parse import urljoin
import requests
import os

class LiveSession (Session):
    def __init__(self, prefix_url = "http://localhost:5000", default_headers = None, *args, **kwargs):
        super ().__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.default_headers = default_headers or {}

    def request (self, method, url, *args, **kwargs):
        url = urljoin (self.prefix_url, url)
        headers = self.default_headers.copy ()
        if 'headers' in kwargs:
            headers.update (kwargs ['headers'])
            kwargs ["headers"] = headers
        else:
            kwargs ["headers"] = headers
        return super ().request (method, url, *args, **kwargs)


from copy import copy

import requests
from requests import HTTPError

from mycroft.configuration import ConfigurationManager
from mycroft.identity import IdentityManager
from mycroft.version import VersionManager

__author__ = 'jdorleans'


class Api(object):
    """Mycroft API Request class
    """
    def __init__(self, path):
        self.path = path
        config = ConfigurationManager().get()
        config_server = config.get("server")
        self.url = config_server.get("url")
        self.version = config_server.get("version")
        self.identity = IdentityManager.get()

    def request(self, params):
        """API Request method
            Args:
                params: request parameters
	    Return:
                params: parameters sent to the API server
	"""
        self.check_token()
        self.build_path(params)
        self.old_params = copy(params)
        return self.send(params)

    def check_token(self):
        """API token check
            This method will determine if the user's registration token is valid.
            If valid, do nothing. If not, call refresh_token.
        """
        if self.identity.refresh and self.identity.is_expired():
            self.identity = IdentityManager.load()
            if self.identity.is_expired():
                self.refresh_token()

    def refresh_token(self):
        """API Teken refresh
            Contact API server and get a new identity token.
        """
        data = self.send({
            "path": "auth/token",
            "headers": {
                "Authorization": "Bearer " + self.identity.refresh
            }
        })
        IdentityManager.save(data)

    def send(self, params):
        """API send
            Send GET request to API server with params
            Args:
                params: parameters
        """
        method = params.get("method", "GET")
        headers = self.build_headers(params)
        data = self.build_data(params)
        json = self.build_json(params)
        query = self.build_query(params)
        url = self.build_url(params)
        response = requests.request(method, url, headers=headers, params=query,
                                    data=data, json=json, timeout=(3.05, 15))
        return self.get_response(response)

    def get_response(self, response):
        """API get response:
            Args:
                Args:
                    response: response
            Returns:
                data: response data returned from API server
        """
        data = self.get_data(response)
        if 200 <= response.status_code < 300:
            return data
        elif response.status_code == 401\
                and not response.url.endswith("auth/token"):
            self.refresh_token()
            return self.send(self.old_params)
        raise HTTPError(data, response=response)

    def get_data(self, response):
        """API get data
            Args:
                response: response
        """
        try:
            return response.json()
        except:
            return response.text

    def build_headers(self, params):
        """API build headers for requests
            Args:
                params: parameters
            Returns:
                headers (list): resulting response headers
        """
        headers = params.get("headers", {})
        self.add_content_type(headers)
        self.add_authorization(headers)
        params["headers"] = headers
        return headers

    def add_content_type(self, headers):
        """API request add content type to header
           Args:
               headers (list): returns content type application/json
        """
        if not headers.__contains__("Content-Type"):
            headers["Content-Type"] = "application/json"

    def add_authorization(self, headers):
        """API request add Bearer token to header
            Args:
                headers (list): updated headers including bearer token
        """
        if not headers.__contains__("Authorization"):
            headers["Authorization"] = "Bearer " + self.identity.access

    def build_data(self, params):
        """API request data builder
            Args:
                params: parameters
        """
        return params.get("data")

    def build_json(self, params):
        """API request json builder
            Args:
                params: parameters
            Returns:
                json (object): a json object 
        """
        json = params.get("json")
        if json and params["headers"]["Content-Type"] == "application/json":
            for k, v in json.iteritems():
                if v == "":
                    json[k] = None
            params["json"] = json
        return json

    def build_query(self, params):
        """API request query builder
            Args:
                params: parameters
        """
        return params.get("query")

    def build_path(self, params):
        """API request path builder
            Args:
                params: parameters
        """
        path = params.get("path", "")
        params["path"] = self.path + path
        return params["path"]

    def build_url(self, params):
        """API request url builder
            Args:
                params: parameters
        """
        path = params.get("path", "")
        version = params.get("version", self.version)
        return self.url + "/" + version + "/" + path


class DeviceApi(Api):
    """Device API class
    """
    def __init__(self):
        super(DeviceApi, self).__init__("device")

    def get_code(self, state):
        """Device API get pairing code
            Args:
                state: device pairing state
        """
        IdentityManager.update()
        return self.request({
            "path": "/code?state=" + state
        })

    def activate(self, state, token):
        """Device API activate device
            Args:
                state: device state
                token: autorizention token
        """
        version = VersionManager.get()
        return self.request({
            "method": "POST",
            "path": "/activate",
            "json": {"state": state,
                     "token": token,
                     "coreVersion": version.get("coreVersion"),
                     "enclosureVersion": version.get("enclosureVersion")}
        })

    def find(self):
        """Device API find -- what does this do?
        """
        return self.request({
            "path": "/" + self.identity.uuid
        })

    def find_setting(self):
        """Device API find setting -- what does this do?
        """
        return self.request({
            "path": "/" + self.identity.uuid + "/setting"
        })

    def find_location(self):
        """Device API find location -- what does this do?
        """
        return self.request({
            "path": "/" + self.identity.uuid + "/location"
        })


class STTApi(Api):
    """STT API sends audio to STT
    """
    def __init__(self):
        super(STTApi, self).__init__("stt")

    def stt(self, audio, language, limit):
        """STT API method
            Args:
                audio: audio file
                language: configured language
                limit: limit of what? 
        """
        return self.request({
            "method": "POST",
            "headers": {"Content-Type": "audio/x-flac"},
            "query": {"lang": language, "limit": limit},
            "data": audio
        })

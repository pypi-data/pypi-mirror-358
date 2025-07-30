import requests
from .exceptions import AsanakSmsException, AsanakHttpException


class AsanakSmsClient:
    def __init__(self, username: str, password: str, base_url: str = "https://sms.asanak.ir"):
        self.username = username
        self.password = password
        self.base_url = base_url

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        data = {
            "username": self.username,
            "password": self.password,
            **payload
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        api_response = response.json()
        return self._process_response(api_response)

    def send_sms(self, source: str, destination: str, message: str, send_to_black_list: bool = True) -> dict:
        return self._post("/webservice/v2rest/sendsms", {
            "source": source,
            "destination": destination,
            "message": message,
            "send_to_black_list": int(send_to_black_list)
        })

    def send_p2p(self, source: list, destination: list, message: list, send_to_black_list: list = None) -> dict:
        if send_to_black_list is None:
            send_to_black_list = [1] * len(source)

        data = []
        for i in range(len(source)):
            data.append({
                "source": source[i],
                "destination": destination[i] if i < len(destination) else "",
                "message": message[i] if i < len(message) else "",
                "send_to_black_list": int(send_to_black_list[i]) if i < len(send_to_black_list) else 1
            })

        return self._post("/webservice/v2rest/p2psendsms", {"data": data})

    def send_template(self, template_id: int, parameters: dict, destination: str, send_to_black_list: bool = True) -> dict:
        return self._post("/webservice/v2rest/template", {
            "template_id": template_id,
            "parameters": parameters,
            "destination": destination,
            "send_to_black_list": int(send_to_black_list)
        })

    def msg_status(self, msg_ids: list | str) -> dict:
        msgid_str = ",".join(msg_ids) if isinstance(msg_ids, list) else msg_ids
        return self._post("/webservice/v2rest/msgstatus", {"msgid": msgid_str})

    def get_credit(self) -> dict:
        return self._post("/webservice/v2rest/getcredit", {})

    def get_rial_credit(self) -> dict:
        return self._post("/webservice/v2rest/getrialcredit", {})

    def get_templates(self) -> dict:
        return self._post("/webservice/v2rest/templatelist", {})

    def _process_response(self, response: dict) -> dict:
        if 'meta' not in response or 'status' not in response['meta']:
            raise RuntimeError("Invalid API response structure")

        status = response['meta']['status']

        if status == 200:
            return response.get('data', {})

        code = int(status) if isinstance(status, int) or str(status).isdigit() else 400
        error_message = response['meta'].get('message', "Bad request error")
        raise RuntimeError(f"{error_message} (status code: {code})")
import requests

class SlackNotify:
    def __init__(self, url):
        self.url = url

    def send_message(self, message):
        headers = {
                "Content": "application/json"
                }
        body = {
                "text": message
                }
        response = requests.post(url = self.url, headers = headers, json = body)
        if response.status_code != 200:
            print(response)

import requests

class ApiClient():

    @staticmethod
    def post(url, data):
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            print(response)
            return response.text
        except requests.RequestException as e:
            print(e)
            return f"An error occurred: {e}"
        
    @staticmethod
    def get(url):
        response = requests.get(url)
        response.raise_for_status()
        print(response)
        return response.text
# windowsworld-api/windowsworld_api/api.py

import requests
class WindowsWorldAPIError(Exception):
    """Custom exception for Windows World API errors."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.message}"
    


# windowsworld-api/windowsworld_api/api.py

import requests

class WindowsWorldAPI:
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.windowsworldcartoon.workers.dev"

    def create_client(self, api_key):
        self.api_key = api_key

    def get_groups(self):
        """Fetch a list of groups."""
        if not self.api_key:
            raise WindowsWorldAPIError("API key not set. Use create_client() to set the API key.")
        headers = {"X-API-KEY": self.api_key}
        response = requests.get(f"{self.base_url}/api/groups", headers=headers)
        return response.json()

    def get_organizations(self):
        """Fetch a list of organizations."""
        if not self.api_key:
            raise WindowsWorldAPIError("API key not set. Use create_client() to set the API key.")
        headers = {"X-API-KEY": self.api_key}
        response = requests.get(f"{self.base_url}/api/organizations", headers=headers)
        return response.json()
    
    def custom_endpoint(self, endpoint):
        """Fetch data from a custom endpoint."""
        if not self.api_key:
            raise WindowsWorldAPIError("API key not set. Use create_client() to set the API key.")
        
        headers = {"X-API-KEY": self.api_key}
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers)
        
        if response.status_code != 200:
            raise WindowsWorldAPIError(f"Error fetching data from {endpoint}: {response.text}")
        
        return response.json()




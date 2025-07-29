# Windows World API Client

A Python client for the Windows World API.

## Installation

To install the client, run the following command:
```bash
pip install windowsworld-api
```



```python
from windowsworld_api import WindowsWorldAPI

api = WindowsWorldAPI()

```
## Usage

To use the client, create an instance of the WindowsWorldAPI class and call the create_client method with your API key:

```python
from windowsworld_api import WindowsWorldAPI

client = WindowsWorldAPI()
client.create_client("YOUR_API_KEY_HERE")

groups = client.get_groups()
organizations = client.get_organizations()

print(groups)
print(organizations)
```

Replace `YOUR_API_KEY_HERE` with your actual API key.

## Methods

The client provides the following methods:

- `get_groups()`: Retrieves a list of groups from the API.
- `get_organizations()`: Retrieves a list of organizations from the API.
- `custom_endpoint(endpoint)`: Retrieves data from a custom endpoint.
## License

This client is licensed under the MIT License.

## Author

WindowsWorldCartoon
Contact Email: [windowsworldcartoon@gmail.com](mailto:windowsworldcartoon@gmail.com)
# opsduty-client
A client library for accessing opsduty

## Usage
First, create a client:

```python
from opsduty_client import Client

client = Client(base_url="https://opsduty.io")
```

If the endpoints you're going to hit require authentication, use `AuthenticatedClient` instead:

```python
from opsduty_client import AuthenticatedClient

client = AuthenticatedClient(base_url="https://opsduty.io", token="oAuth2 access token")
```

Now call your endpoint and use your models:

```python
from opsduty_client.models import MyDataModel
from opsduty_client.api.my_tag import get_my_data_model
from opsduty_client.types import Response

with client as client:
    my_data: MyDataModel = get_my_data_model.sync(client=client)
    # or if you need more info (e.g. status_code)
    response: Response[MyDataModel] = get_my_data_model.sync_detailed(client=client)
```

Or do the same thing with an async version:

```python
from opsduty_client.models import MyDataModel
from opsduty_client.api.my_tag import get_my_data_model
from opsduty_client.types import Response

async with client as client:
    my_data: MyDataModel = await get_my_data_model.asyncio(client=client)
    response: Response[MyDataModel] = await get_my_data_model.asyncio_detailed(client=client)
```

## Advanced customizations

There are more settings on the generated `Client` class which let you control more runtime behavior, check out the docstring on that class for more info. You can also customize the underlying `httpx.Client` or `httpx.AsyncClient` (depending on your use-case):

```python
from opsduty_client import Client

def log_request(request):
    print(f"Request event hook: {request.method} {request.url} - Waiting for response")

def log_response(response):
    request = response.request
    print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

client = Client(
    base_url="https://opsduty.io",
    httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
)

# Or get the underlying httpx client to modify directly with client.get_httpx_client() or client.get_async_httpx_client()
```

You can even set the httpx client directly, but beware that this will override any existing settings (e.g., base_url):

```python
import httpx
from opsduty_client import Client

client = Client(
    base_url="https://opsduty.io",
)
# Note that base_url needs to be re-set, as would any shared cookies, headers, etc.
client.set_httpx_client(httpx.Client(base_url="https://opsduty.io", proxies="http://localhost:8030"))
```

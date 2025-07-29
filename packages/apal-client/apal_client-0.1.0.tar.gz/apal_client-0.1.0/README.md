# APAL Python Client

A Python client library for the APAL secure P2P communication platform.

## Installation

```bash
pip install apal-client
```

## Quick Start

```python
import asyncio
from apal_client import APALClient
from uuid import UUID

async def main():
    # Initialize client
    client = APALClient(
        base_url="http://localhost:8000",
        email="your@email.com",
        password="your-password"
    )
    
    # Register a new business account
    account = await client.register(
        email="business@example.com",
        password="secure-password",
        business_name="Example Business"
    )
    
    # Send a message
    message = await client.send_message(
        receiver_id=UUID("receiver-uuid"),
        content={
            "type": "payment",
            "data": {
                "amount": 100.00,
                "currency": "USD",
                "payment_method": "bank_transfer",
                "reference_id": "PAY-123456"
            }
        }
    )
    
    # List messages
    messages = await client.list_messages()
    
    # Get message status
    status = await client.get_message_status(message["id"])

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Asynchronous API client
- Automatic authentication handling
- Message encryption/decryption
- Error handling and validation
- Support for all APAL API endpoints

## Environment Variables

The client can be configured using environment variables:

- `APAL_API_KEY`: Your API key
- `APAL_EMAIL`: Your registered email
- `APAL_PASSWORD`: Your password
- `APAL_BASE_URL`: API base URL (default: http://localhost:8000)

## Error Handling

The client raises custom exceptions for different error cases:

```python
from apal_client import (
    APALError,
    ValidationError,
    AuthenticationError,
    MessageError,
    APIError
)

try:
    await client.send_message(...)
except ValidationError as e:
    print(f"Message validation failed: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except MessageError as e:
    print(f"Message processing failed: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## License

MIT License 
# Jamm SDK for Python

A Python client SDK for interacting with the Jamm API using Protocol Buffers over HTTP.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import jamm

# Basic configuration
client = jamm.configure(
    client_id="your_client_id",
    client_secret="your_client_secret",
    env="develop"  # or "staging", "production", etc.
)

# Make a healthcheck request
response = client.healthcheck()
print(response)
```

## Configuration

The SDK can be configured using environment variables or programmatically:

### Programmatic Configuration

```python
from jamm import JammClient, ClientConfig

config = ClientConfig(
    api_base_url="https://api.staging.jamm.com/v1",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

client = JammClient(config)
```

## Features

The Jamm SDK provides comprehensive functionality for payment processing, customer management, and banking operations:

- **Health Check**: Verify API connectivity
- **Customer Management**: Create, update, get, and delete customers
- **Payment Processing**: On-session and off-session payments
- **Contract Management**: Create contracts with or without charges
- **Charge Operations**: Create charges with/without redirects, retrieve and list charges
- **Banking**: Search banks, get bank information, and manage bank branches

## API Reference

### Health Check

```python
# Verify API connectivity
response = client.healthcheck()
print(response)
```

### Customer Management

```python
# Create a customer
from datetime import datetime, timedelta

buyer_data = {
    "email": "customer@example.com",
    "name": "John Doe",
    "katakana_last_name": "ドウ",
    "katakana_first_name": "ジョン",
    "address": "123 Tokyo Street, Shibuya",
    "birth_date": "1990-01-01",
    "gender": "male",
    "force_kyc": False,
    "metadata": {"source": "api"}
}

customer = client.customers.create(buyer=buyer_data)
print(f"Created customer: {customer['customer']['customer']['id']}")

# Get a customer
customer = client.customers.get("cus-customer_id_here")

# Update a customer
updated_customer = client.customers.update(
    customer_id="cus-customer_id_here",
    data={
        "name": "Updated Name",
        "metadata": {"updated": True}
    }
)

# Get customer's contract
contract = client.customers.get_contract("cus-customer_id_here")

# Delete a customer
result = client.customers.delete("cus-customer_id_here")
```

### Payment Processing

```python
from datetime import datetime, timedelta

# Calculate expiration date
expires_at = (datetime.now() + timedelta(days=2)).isoformat() + "Z"

# Off-session payment (no user interaction required)
result = client.payments.off_session(
    customer_id="cus-customer_id_here",
    price="1000",  # Amount in smallest currency unit (e.g., cents)
    description="Monthly subscription",
    expires_at=expires_at
)

# On-session payment with redirect URLs
result = client.payments.on_session(
    customer_id="cus-customer_id_here",
    price="1000",
    description="One-time payment",
    redirect_urls={
        "success_url": "https://yoursite.com/success",
        "failure_url": "https://yoursite.com/cancel"
    },
    expires_at=expires_at
)

# Create contract without charge (setup only)
result = client.payments.on_session(
    buyer=buyer_data,
    redirect_urls={
        "success_url": "https://yoursite.com/success",
        "failure_url": "https://yoursite.com/cancel"
    },
    expires_at=expires_at
)

# Create contract with initial charge
result = client.payments.on_session(
    buyer=buyer_data,
    charge={
        "price": "1000",
        "description": "Initial payment"
    },
    redirect_urls={
        "success_url": "https://yoursite.com/success",
        "failure_url": "https://yoursite.com/cancel"
    },
    expires_at=expires_at
)
```

### Contract Management

```python
# Create contract with charge
contract = client.contracts.create_with_charge(
    buyer=buyer_data,
    charge={
        "price": 1000,
        "description": "Setup fee",
        "expires_at": expires_at
    },
    redirect={
        "success_url": "https://yoursite.com/success",
        "failure_url": "https://yoursite.com/cancel"
    }
)

# Create contract without charge
contract = client.contracts.create_without_charge(
    buyer=buyer_data,
    redirect={
        "success_url": "https://yoursite.com/success",
        "failure_url": "https://yoursite.com/cancel"
    }
)

# Get existing contract
contract = client.contracts.get("cus-customer_id_here")
```

### Charge Operations

```python
# Create charge without redirect (direct processing)
charge = client.charges.create_without_redirect(
    customer_id="cus-customer_id_here",
    price=1500,
    description="Product purchase",
    expires_at=expires_at,
    metadata={"order_id": "12345"}
)

# Create charge with redirect (user will be redirected to payment page)
charge = client.charges.create_with_redirect(
    customer_id="cus-customer_id_here",
    price=2000,
    success_url="https://yoursite.com/success",
    failure_url="https://yoursite.com/failure",
    description="Premium service",
    expires_at=expires_at,
    metadata={"service": "premium"}
)

# Get specific charge
charge = client.charges.get("trx-charge_id_here")

# List charges for a customer
charges = client.charges.list(
    customer_id="cus-customer_id_here",
    page_size=10
)
```

### Banking Operations

```python
# Get specific bank information
bank = client.banks.get("0001")  # Bank code

# Get major banks
major_banks = client.banks.get_major_banks()
for bank_key, bank_info in major_banks.items():
    print(f"{bank_info['name']} - Code: {bank_info['code']}")

# Search banks
search_results = client.banks.search("みずほ")  # Search for Mizuho Bank
for bank in search_results.get("banks", []):
    print(f"{bank['name']} - Code: {bank['code']}")

# Get specific bank branch
branch = client.bank_branches.get("0001", "001")  # Bank code, branch code

# Search branches within a bank
branches = client.bank_branches.search("0001", "東京")  # Bank code, search term
for branch in branches[:5]:  # First 5 results
    print(f"{branch['name']} - Branch Code: {branch['branchCode']}")

# List all branches for a bank
all_branches = client.bank_branches.list_for_bank("0001")
print(f"Total branches: {len(all_branches)}")
```

## Authentication

The SDK automatically handles OAuth 2.0 authentication flows using your client credentials.

## Development

### Setup Development Environment

```bash
# Clone the repository
cd jamm-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Running Tests

You can run the comprehensive test suite that covers all SDK functionality:

```bash
# Run the test script with your credentials
python tests/test_sdk.py --client-id your_client_id --client-secret your_client_secret --env develop

# The test script will verify:
# - Health check functionality
# - Customer CRUD operations
# - Payment processing (on-session and off-session)
# - Contract management
# - Charge operations
# - Banking and branch operations
```

The test script includes realistic examples of:
- Creating customers with Japanese names and addresses
- Processing payments with proper expiration dates
- Managing contracts and charges
- Banking operations with Japanese bank codes
- Error handling and debugging information

### Example Test Output

```bash
✅ Successfully retrieved response: {...}
✅ Successfully created customer: {...}
✅ Successfully created off session: {...}
✅ Successfully created charge with redirect: {...}
✅ Successfully retrieved major banks: {...}
```

## Helper Functions

### Generating Test Data

The SDK test suite includes a helpful `generate_buyer()` function for creating realistic customer data:

```python
from faker import Faker
import time

def generate_buyer(base_email=None, name=None, force_kyc=False):
    """Generate realistic buyer data for testing"""
    fake_en = Faker("en_US")
    fake_jp = Faker("ja_JP")
    timestamp = int(time.time())
    
    return {
        "email": f"{fake_en.user_name()}+{timestamp}@jamm-pay.jp",
        "name": name or fake_en.name(),
        "katakana_last_name": fake_jp.last_kana_name(),
        "katakana_first_name": fake_jp.first_kana_name(),
        "address": fake_jp.address(),
        "birth_date": fake_en.date_of_birth(minimum_age=20, maximum_age=70).strftime("%Y-%m-%d"),
        "gender": fake_en.random_element(["male", "female"]),
        "force_kyc": force_kyc,
        "metadata": {"source": "faker_generated", "timestamp": str(timestamp)}
    }

# Usage
buyer_data = generate_buyer()
customer = client.customers.create(buyer=buyer_data)
```

## Error Handling

The SDK provides detailed error information for debugging:

```python
try:
    customer = client.customers.get("invalid-id")
except Exception as e:
    print(f"Error: {e}")
    # Check authentication headers if needed
    if hasattr(client.customers, "_get_auth_headers"):
        headers = client.customers._get_auth_headers()
        print(f"Auth headers: {headers}")
```

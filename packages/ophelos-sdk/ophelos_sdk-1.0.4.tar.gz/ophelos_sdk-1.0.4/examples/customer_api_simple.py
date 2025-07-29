import json
import os
from datetime import date, datetime

from ophelos_sdk import OphelosClient
from ophelos_sdk.models import ContactDetail, ContactDetailSource, ContactDetailType, ContactDetailUsage, Customer

customer = Customer(
    id="cust_123",
    object="customer",
    kind="individual",
    first_name="John",
    last_name="Doe",
    preferred_locale="en-GB",
    date_of_birth=date(1990, 1, 15),
    contact_details=[
        ContactDetail(
            id="cd_123",
            object="contact_detail",
            type=ContactDetailType.EMAIL,
            value="john@example.com",
            primary=True,
            usage=ContactDetailUsage.PERMANENT,
            source=ContactDetailSource.CLIENT,
            status="verified",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        ContactDetail(
            type=ContactDetailType.MOBILE_NUMBER,
            value="+447466123456",
            primary=True,
        ),
    ],
    debts=["debt_123", "debt_456"],
    created_at=datetime.now(),
    updated_at=datetime.now(),
)

api_body = customer.to_api_body()
print("Generated API body:")
print(json.dumps(api_body, indent=2))

# Initialize client with access token or OAuth2 credentials
access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhrUEJSV0dkMi1DS09pVnNLbUIzayJ9.eyJvcGhlbG9zOmFjY2VzcyI6e30sImlzcyI6Imh0dHBzOi8vb3BoZWxvcy1kZXYuZXUuYXV0aDAuY29tLyIsInN1YiI6ImFla0dwTVBYa3hPOFFURUkxMTd1SnoyZmNjNWp1ZnpRQGNsaWVudHMiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjMwMDAiLCJpYXQiOjE3NTA3MTA3MjEsImV4cCI6MTc1MDc5NzEyMSwic2NvcGUiOiJyZWFkOmRlYnQgYWRtaW4iLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJhZWtHcE1QWGt4TzhRVEVJMTE3dUp6MmZjYzVqdWZ6USIsInBlcm1pc3Npb25zIjpbInJlYWQ6ZGVidCIsImFkbWluIl19.ReDXuRGeUxOa9-GC6_vEznnC-4YeHn0oUrXLBYh5V93yYIrBBHARqmFi2jbmd1jRnGz0UzsfHKHvf3v24UXEzrmfvE6iM-p-48QbRMVeWaX0KjxJtezG9cQxzejj8FXzmjiEtnpj8-bJ0xUCfhjKm23mwXLjAhHCo4ooOC5P7U6tDKgGBYQUqmJJYKOmRvO-CuQW65ePU_nLk_Z9oPXC8Hah7A_XxwIh7cBxze3Km2dX8TRHskUEECFhTRETdbdx7iOG-_GG0y99Pz6k-qt0BPeViPND9R1J5hKv3qHfQ0MkhE2KqOahG_y1dVBvErkCezp_4pVISk4kpwtoCQpmbA"
if access_token:
    print("\nUsing access token authentication...")
    client = OphelosClient(access_token=access_token)
else:
    print("\nUsing OAuth2 authentication...")
    client = OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID", "your_client_id"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET", "your_client_secret"),
        audience=os.getenv("OPHELOS_AUDIENCE", "your_audience"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "staging"),
    )

# Test connection
print("Testing connection...")
try:
    if client.test_connection():
        print("✅ Connected to Ophelos API successfully!")

        # Create customer using the model directly
        print("\nCreating customer...")
        created_customer = client.customers.create(customer)

        # Retrieve the created customer
        print("Retrieving customer...")
        retrieved_customer = client.customers.get(created_customer.id)

        print(f"✅ Created and retrieved customer: {retrieved_customer.id} - {retrieved_customer.full_name}")

        # Pretty print the received customer as JSON
        print("\n" + "=" * 60)
        print("📋 RECEIVED CUSTOMER (Pretty JSON)")
        print("=" * 60)

        # Convert customer to JSON and print
        customer_json = (
            retrieved_customer.model_dump_json(indent=2)
            if hasattr(retrieved_customer, "model_dump_json")
            else json.dumps(retrieved_customer.model_dump(), indent=2, default=str)
        )
        print(customer_json)
    else:
        print("❌ Failed to connect to Ophelos API")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"❌ Error Type: {type(e).__name__}")

    # Show detailed response information from OphelosAPIError
    if hasattr(e, "status_code"):
        print(f"❌ HTTP Status Code: {e.status_code}")

    if hasattr(e, "response_data") and e.response_data:
        print(f"❌ Response Data: {json.dumps(e.response_data, indent=2, default=str)}")

        # Extract specific error details
        if isinstance(e.response_data, dict):
            message = e.response_data.get("message")
            if message:
                print(f"❌ API Message: {message}")

            errors = e.response_data.get("errors", [])
            if errors:
                print(f"❌ Validation Errors: {errors}")

            error_code = e.response_data.get("error_code")
            if error_code:
                print(f"❌ Error Code: {error_code}")

    print("\n💡 Make sure to set your authentication credentials:")
    print("   Option 1 - Access Token:")
    print("   export OPHELOS_ACCESS_TOKEN='your_access_token'")
    print("   Option 2 - OAuth2 Credentials:")
    print("   export OPHELOS_CLIENT_ID='your_client_id'")
    print("   export OPHELOS_CLIENT_SECRET='your_client_secret'")
    print("   export OPHELOS_AUDIENCE='your_audience'")
    print("   export OPHELOS_ENVIRONMENT='staging'  # optional")

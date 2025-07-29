import json
from datetime import datetime

from ophelos_sdk import OphelosClient
from ophelos_sdk.models import Customer, Debt

# Create a customer model with ID
customer = Customer(id="cust_123456789", object="customer", kind="individual", first_name="John", last_name="Doe")

debt = Debt(
    id="debt_123",
    object="debt",
    customer=customer,  # Pass customer model - will auto-convert to customer_id
    organisation_id="org_123456789",
    currency="GBP",
    reference_code="DEBT-001",
    kind="purchased",
    created_at=datetime.now(),
    updated_at=datetime.now(),
)

api_body = debt.to_api_body()
print("Generated API body:")
print(json.dumps(api_body, indent=2))

access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjhrUEJSV0dkMi1DS09pVnNLbUIzayJ9.eyJvcGhlbG9zOmFjY2VzcyI6e30sImlzcyI6Imh0dHBzOi8vb3BoZWxvcy1kZXYuZXUuYXV0aDAuY29tLyIsInN1YiI6ImFla0dwTVBYa3hPOFFURUkxMTd1SnoyZmNjNWp1ZnpRQGNsaWVudHMiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjMwMDAiLCJpYXQiOjE3NTA3MTA3MjEsImV4cCI6MTc1MDc5NzEyMSwic2NvcGUiOiJyZWFkOmRlYnQgYWRtaW4iLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJhZWtHcE1QWGt4TzhRVEVJMTE3dUp6MmZjYzVqdWZ6USIsInBlcm1pc3Npb25zIjpbInJlYWQ6ZGVidCIsImFkbWluIl19.ReDXuRGeUxOa9-GC6_vEznnC-4YeHn0oUrXLBYh5V93yYIrBBHARqmFi2jbmd1jRnGz0UzsfHKHvf3v24UXEzrmfvE6iM-p-48QbRMVeWaX0KjxJtezG9cQxzejj8FXzmjiEtnpj8-bJ0xUCfhjKm23mwXLjAhHCo4ooOC5P7U6tDKgGBYQUqmJJYKOmRvO-CuQW65ePU_nLk_Z9oPXC8Hah7A_XxwIh7cBxze3Km2dX8TRHskUEECFhTRETdbdx7iOG-_GG0y99Pz6k-qt0BPeViPND9R1J5hKv3qHfQ0MkhE2KqOahG_y1dVBvErkCezp_4pVISk4kpwtoCQpmbA"

client = OphelosClient(access_token=access_token)

try:
    created_debt = client.debts.create(debt)
    retrieved_debt = client.debts.get(created_debt.id)
    print(f"Created debt: {retrieved_debt.id}")
    print(retrieved_debt.model_dump_json(indent=2))
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, "response_data") and e.response_data:
        print(f"Response: {json.dumps(e.response_data, indent=2, default=str)}")

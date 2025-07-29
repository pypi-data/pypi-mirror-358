#!/usr/bin/env python3
"""
Ophelos SDK - Model to_api_body() Method Usage

This example demonstrates how to use the new to_api_body() method
to control which fields are included in API requests.

Key Features:
- Each model defines which fields can be sent to API
- Automatic exclusion of server-generated fields (id, object, created_at, updated_at)
- Smart handling of nested models and relationships
- Type safety and validation benefits
"""

import json
import os
from datetime import date, datetime

from ophelos_sdk import OphelosClient
from ophelos_sdk.models import (
    ContactDetail,
    ContactDetailType,
    Currency,
    Customer,
    Debt,
    DebtStatus,
    DebtSummary,
    Payment,
    PaymentStatus,
    StatusObject,
)

# Configuration for API calls vs payload preview
API_CALL = False  # Set to True to make actual API calls, False to just show payloads


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"🔧 {title}")
    print(f"{'=' * 60}")


def print_payload(title: str, payload: dict):
    """Print a formatted payload."""
    print(f"\n--- {title} ---")
    print(json.dumps(payload, indent=2, default=str))


def demonstrate_customer_api_body():
    """Demonstrate Customer model to_api_body() method."""
    print_section("CUSTOMER MODEL - to_api_body() Method")

    # Create a customer with all possible fields
    customer = Customer(
        id="cust_temp_123",  # This will be excluded from API body
        object="customer",  # This will be excluded from API body
        kind="individual",
        full_name="John Doe",
        first_name="John",
        last_name="Doe",
        preferred_locale="en-GB",
        date_of_birth=date(1990, 5, 15),
        contact_details=[],  # Will be included as empty list
        debts=None,  # Will be excluded (None value)
        created_at=datetime.now(),  # This will be excluded from API body
        updated_at=datetime.now(),  # This will be excluded from API body
        metadata={"source": "api_body_example", "customer_type": "premium"},
    )

    print(f"Customer model created with ID: {customer.id}")
    print(f"Full model has {len(customer.model_dump())} fields")

    # Generate API body
    api_body = customer.to_api_body()
    print_payload("Customer API Body (for create/update)", api_body)

    print(f"\nAPI body has {len(api_body)} fields")
    print("✅ Server fields (id, object, created_at, updated_at) automatically excluded")
    print("✅ None values excluded by default")
    print("✅ Only writable fields included")

    # Show the difference between full model and API body
    full_model = customer.model_dump()
    excluded_fields = set(full_model.keys()) - set(api_body.keys())
    print(f"\nExcluded from API body: {sorted(excluded_fields)}")


def demonstrate_contact_detail_api_body():
    """Demonstrate ContactDetail model to_api_body() method."""
    print_section("CONTACT DETAIL MODEL - to_api_body() Method")

    # Create contact detail with server fields
    contact = ContactDetail(
        id="cd_temp_456",
        object="contact_detail",
        type=ContactDetailType.EMAIL,
        value="john@example.com",
        primary=True,
        usage="billing",
        source="user_input",
        status="verified",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"verified_date": "2024-01-15"},
    )

    print(f"ContactDetail model created with ID: {contact.id}")

    # Generate API body
    api_body = contact.to_api_body()
    print_payload("ContactDetail API Body", api_body)

    print("\n✅ Only writable fields included:")
    for field in sorted(api_body.keys()):
        print(f"  - {field}: {api_body[field]}")


def demonstrate_debt_api_body():
    """Demonstrate Debt model to_api_body() method."""
    print_section("DEBT MODEL - to_api_body() Method")

    # Create customer and debt models
    customer = Customer(
        id="cust_real_789",  # Real ID - will be converted to reference
        first_name="Jane",
        last_name="Smith",
        preferred_locale="en-US",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create debt with relationships
    debt = Debt(
        id="debt_temp_123",
        object="debt",
        status=StatusObject(
            value=DebtStatus.PREPARED,
            whodunnit="system",
            context="api_creation",
            reason="new_debt",
            updated_at=datetime.now(),
        ),
        kind="credit_card",
        reference_code="CC-2024-001",
        account_number="****1234",
        customer=customer,  # Model instance - will be converted to ID reference
        organisation="org_123",  # Already an ID string
        currency=Currency.USD,
        summary=DebtSummary(amount_total=50000, amount_paid=0, amount_remaining=50000),  # $500.00
        tags=["high_priority", "new_customer"],
        configurations={"payment_reminder": True},
        start_at=date(2024, 1, 15),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"source": "api_import", "batch_id": "batch_001"},
    )

    print("Debt model created with customer relationship")

    # Generate API body
    api_body = debt.to_api_body()
    print_payload("Debt API Body", api_body)

    print("\n🔍 Key features:")
    customer_field = api_body.get("customer")
    print(f"  - customer field type: {type(customer_field)}")
    if isinstance(customer_field, str):
        print(f"  - customer field: {customer_field} (converted to ID reference)")
    else:
        print(
            f"  - customer field: full object with ID {customer_field.get('id', 'no-id') if isinstance(customer_field, dict) else 'unknown'}"
        )
    print(f"  - organisation field: {api_body.get('organisation')} (kept as string)")
    print("  - status object: included as full object")
    print("  - summary object: included as full object")
    print("  - Server fields excluded automatically")


def demonstrate_payment_api_body():
    """Demonstrate Payment model to_api_body() method."""
    print_section("PAYMENT MODEL - to_api_body() Method")

    # Create payment model
    payment = Payment(
        id="pay_temp_456",
        object="payment",
        debt="debt_123",  # String ID - will be kept as-is
        status=PaymentStatus.SUCCEEDED,
        transaction_at=datetime.now(),
        transaction_ref="TXN_789",
        amount=25000,  # $250.00
        currency=Currency.USD,
        payment_provider="stripe",
        payment_plan=None,  # Will be excluded
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"gateway_id": "pi_123456789", "customer_ip": "192.168.1.1"},
    )

    print(f"Payment model created for debt: {payment.debt}")

    # Generate API body
    api_body = payment.to_api_body()
    print_payload("Payment API Body", api_body)

    print("\n✅ Payment-specific API body features:")
    print(f"  - debt field: {api_body.get('debt')} (kept as string)")
    print(f"  - amount: {api_body.get('amount')} cents")
    print(f"  - status: {api_body.get('status')}")
    print("  - payment_plan: excluded (None value)")


def demonstrate_nested_models():
    """Demonstrate how nested models are handled in API bodies."""
    print_section("NESTED MODELS - Smart Handling")

    # Create contact details
    email_contact = ContactDetail(
        id="cd_temp_email",
        type=ContactDetailType.EMAIL,
        value="customer@example.com",
        primary=True,
        usage="communication",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    phone_contact = ContactDetail(
        id="cd_temp_phone",
        type=ContactDetailType.PHONE,
        value="+1-555-0123",
        primary=False,
        usage="verification",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create customer with nested contact details
    customer = Customer(
        id="cust_temp_nested",
        first_name="Alice",
        last_name="Johnson",
        preferred_locale="en-CA",
        contact_details=[email_contact, phone_contact],
        metadata={"account_type": "business"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    print("Customer created with nested ContactDetail models")

    # Generate API body
    api_body = customer.to_api_body()
    print_payload("Customer with Nested Models API Body", api_body)

    print("\n🔍 Nested model handling:")
    print("  - ContactDetail models converted to full objects (not ID references)")
    print("  - Each nested model applies its own _api_body_fields rules")
    print("  - Server fields excluded from nested objects too")


def demonstrate_api_integration():
    """Demonstrate integration with actual API calls."""
    print_section("API INTEGRATION - Using to_api_body()")

    if not API_CALL:
        print("📋 DEMO MODE - Showing payloads only (API_CALL = False)")
        print("💡 Set API_CALL = True to make actual API calls")

        # Create example models
        customer = Customer(
            id="cust_demo_123",
            first_name="Demo",
            last_name="Customer",
            preferred_locale="en-GB",
            metadata={"demo": True},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        debt = Debt(
            id="debt_demo_456",
            status=StatusObject(value=DebtStatus.PREPARED, whodunnit="demo", updated_at=datetime.now()),
            kind="loan",
            reference_code="DEMO-001",
            customer=customer,
            organisation="org_demo",
            currency=Currency.GBP,
            summary=DebtSummary(amount_total=100000),
            metadata={"demo_debt": True},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        print_payload("Customer API Body (would be sent to API)", customer.to_api_body())
        print_payload("Debt API Body (would be sent to API)", debt.to_api_body())

        return

    # Actual API integration
    print("🚀 Making actual API calls...")

    client = OphelosClient(
        client_id=os.getenv("OPHELOS_CLIENT_ID"),
        client_secret=os.getenv("OPHELOS_CLIENT_SECRET"),
        audience=os.getenv("OPHELOS_AUDIENCE"),
        environment=os.getenv("OPHELOS_ENVIRONMENT", "staging"),
    )

    try:
        # Create customer using model instance
        customer = Customer(
            first_name="API",
            last_name="Test",
            preferred_locale="en-GB",
            metadata={"created_via": "to_api_body_example"},
        )

        print("Creating customer using model instance...")
        created_customer = client.customers.create(customer)
        print(f"✅ Customer created: {created_customer.id}")

        # The SDK automatically calls customer.to_api_body() internally
        print("✅ SDK used to_api_body() method automatically")

    except Exception as e:
        print(f"❌ API call failed: {e}")


def demonstrate_field_control():
    """Demonstrate how _api_body_fields controls field inclusion."""
    print_section("FIELD CONTROL - _api_body_fields Configuration")

    # Show Customer model configuration
    print("Customer model API body fields:")
    customer_fields = Customer._get_api_body_fields()
    if customer_fields:
        for field in sorted(customer_fields):
            print(f"  ✅ {field}")
    else:
        print("  (Not defined - uses default exclusion)")

    print("\nCustomer model API exclude fields:")
    exclude_fields = Customer._get_api_exclude_fields()
    for field in sorted(exclude_fields):
        print(f"  ❌ {field}")

    # Show Debt model configuration
    print("\nDebt model API body fields:")
    debt_fields = Debt._get_api_body_fields()
    if debt_fields:
        for field in sorted(debt_fields):
            print(f"  ✅ {field}")
    else:
        print("  (Not defined - uses default exclusion)")

    # Demonstrate customization
    print("\n🔧 Field control customization:")
    print("  - Override __api_body_fields__ in model subclasses")
    print("  - Add to __api_exclude_fields__ for additional exclusions")
    print("  - Use exclude_none=False to include None values")


def main():
    """Run all examples."""
    print("🔧 Ophelos SDK - Model to_api_body() Method Usage")

    if API_CALL:
        required_vars = ["OPHELOS_CLIENT_ID", "OPHELOS_CLIENT_SECRET", "OPHELOS_AUDIENCE"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            print(f"\n❌ Missing required environment variables: {missing_vars}")
            print("💡 Set API_CALL = False to run in demo mode")
            return

    try:
        demonstrate_customer_api_body()
        demonstrate_contact_detail_api_body()
        demonstrate_debt_api_body()
        demonstrate_payment_api_body()
        demonstrate_nested_models()
        demonstrate_field_control()
        demonstrate_api_integration()

        print(f"\n{'=' * 60}")
        print("🎉 All to_api_body() examples completed successfully!")
        print("💡 Each model now controls exactly which fields are sent to the API")
        print(f"{'=' * 60}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

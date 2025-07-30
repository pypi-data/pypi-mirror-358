"""
Example demonstrating the _req_res attribute in Ophelos SDK models.

This shows how every model instance contains complete request/response details
from the HTTP call that created it.
"""

# from ophelos_sdk import OphelosClient
# from ophelos_sdk.models import Customer


def main():
    """Demonstrate _req_res functionality."""

    print("🔍 Request/Response Details Example")
    print("=" * 50)

    # Note: This example shows the structure, but requires valid API credentials to run
    print("📝 Note: This example shows the structure, but requires valid API credentials to run.")
    print()

    print("🎯 Every model instance now contains complete HTTP request/response details!")
    print()

    print("✅ Available Properties on Any Model:")
    print("   • model.request_info    - Dictionary with request details")
    print("   • model.response_info   - Dictionary with response details")
    print("   • model.response_raw    - Full requests.Response object")
    print("   • model._req_res        - Direct access to response object")
    print()

    print("📋 Example Usage:")
    print(
        """
# Initialize client (requires valid credentials)
client = OphelosClient(api_key="your-api-key")

# Create a customer - response details automatically captured
customer = client.customers.create({
    "full_name": "Jane Doe",
    "first_name": "Jane", 
    "last_name": "Doe"
})

# Access request information
print(f"Request Method: {customer.request_info['method']}")
print(f"Request URL: {customer.request_info['url']}")
print(f"Request Headers: {customer.request_info['headers']}")
print(f"Request Body: {customer.request_info['body']}")

# Access response information  
print(f"Status Code: {customer.response_info['status_code']}")
print(f"Response Time: {customer.response_info['elapsed_ms']}ms")
print(f"Response Headers: {customer.response_info['headers']}")
print(f"Response URL: {customer.response_info['url']}")

# Access raw response object for advanced usage
raw_response = customer.response_raw
print(f"Raw Status Code: {raw_response.status_code}")
print(f"Raw Headers: {dict(raw_response.headers)}")
print(f"Request Method: {raw_response.request.method}")

# Direct access to response object
print(f"Direct Access: {customer._req_res.status_code}")
"""
    )

    print("🚀 Works with ALL Operations:")
    print("   • GET:    customer = client.customers.get('cust_123')")
    print("   • POST:   customer = client.customers.create({...})")
    print("   • PUT:    customer = client.customers.update('cust_123', {...})")
    print("   • LIST:   customers = client.customers.list()")
    print("   • SEARCH: customers = client.customers.search('query')")
    print()

    print("📊 List Operations:")
    print("   • Each item in PaginatedResponse.data has _req_res")
    print("   • The PaginatedResponse itself also has _req_res")
    print("   • All items share the same response object from the list request")
    print()

    print("🔧 Practical Use Cases:")
    print("   • 🕐 Performance monitoring (response times)")
    print("   • 🐛 Debugging API calls")
    print("   • 📊 Logging request/response details")
    print("   • 🔍 Analyzing response headers")
    print("   • ��️  Building request replay tools")
    print("   • 📈 Tracking API usage patterns")
    print()

    print("⚡ Example: Monitoring Response Times")
    print(
        """
# Monitor slow API calls
customers = client.customers.list(limit=100)
for customer in customers.data:
    response_time = customer.response_info['elapsed_ms']
    if response_time > 1000:  # Over 1 second
        print(f"Slow request detected: {response_time}ms")
        print(f"URL: {customer.request_info['url']}")
"""
    )

    print("🛡️  Example: Error Analysis")
    print(
        """
try:
    customer = client.customers.get('invalid_id')
except NotFoundError as e:
    # Even error responses can be analyzed if they return data
    if hasattr(e, 'response_data') and '_req_res' in e.response_data:
        response = e.response_data['_req_res']
        print(f"Error response time: {response.elapsed.total_seconds() * 1000}ms")
        print(f"Error headers: {dict(response.headers)}")
"""
    )


if __name__ == "__main__":
    main()

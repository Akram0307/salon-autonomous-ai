import requests
import time
import uuid

# Test script to demonstrate idempotency functionality

def test_idempotency():
    # Base URL for the API (adjust as needed for your environment)
    base_url = "http://localhost:8080"
    
    # Test data
    booking_data = {
        "service_id": "service_123",
        "customer_name": "John Doe",
        "date": "2025-08-07",
        "time": "10:00",
        "notes": "Test booking"
    }
    
    # Generate a unique idempotency key
    idempotency_key = str(uuid.uuid4())
    
    print(f"Testing idempotency with key: {idempotency_key}")
    
    # Send the same request multiple times with the same idempotency key
    headers = {
        "Idempotency-Key": idempotency_key,
        "Content-Type": "application/json"
    }
    
    responses = []
    
    for i in range(3):
        print(f"\nSending request {i+1}...")
        try:
            response = requests.post(f"{base_url}/bookings", json=booking_data, headers=headers)
            responses.append({
                "attempt": i+1,
                "status_code": response.status_code,
                "response": response.json() if response.content else None
            })
            print(f"Status Code: {response.status_code}")
            if response.content:
                print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Wait a bit between requests to simulate real-world usage
        time.sleep(1)
    
    # Check if all responses are the same (idempotency working correctly)
    print("\n=== IDENTITY CHECK ===")
    if len(responses) >= 2:
        first_response = responses[0]
        all_same = True
        
        for response in responses[1:]:
            if (response["status_code"] != first_response["status_code"] or 
                response["response"] != first_response["response"]):
                all_same = False
                break
        
        if all_same:
            print("✓ Idempotency working correctly - all responses identical")
        else:
            print("✗ Idempotency not working - responses differ")
            for resp in responses:
                print(f"  Attempt {resp['attempt']}: {resp['status_code']} - {resp['response']}")
    else:
        print("Not enough responses to verify idempotency")

if __name__ == "__main__":
    test_idempotency()

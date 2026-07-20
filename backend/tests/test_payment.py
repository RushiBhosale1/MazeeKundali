"""
Test Razorpay order creation end-to-end.
"""
import urllib.request, json, sys

BASE = "http://localhost:8000"

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body,
          headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

print("\n=== Payment Flow Test ===\n")

# 1. Create kundali
print("1. Creating kundali...")
k = post("/api/v1/kundalis", {
    "name": "Payment Test", "gender": "male", "dob": "1990-05-15",
    "time_of_birth": "14:30", "time_accuracy": "exact",
    "place_query": "Pune", "latitude": 18.5204,
    "longitude": 73.8567, "tz_iana": "Asia/Kolkata", "rahu_mode": "true_node"
})
kid = k["id"]
resume = k.get("resume_token", "")
print(f"   Kundali ID: {kid}")
print(f"   Resume token: {resume[:20]}...")

# 2. Create Razorpay order
print("\n2. Creating Razorpay order...")
try:
    order = post("/api/v1/orders", {
        "product_type": "kundali",
        "record_id": kid,
        "resume_token": resume
    })
    rzp_id = order.get("razorpay_order_id", "")
    key = order.get("key_id", "")
    amount = order.get("amount_inr", 0)
    print(f"   razorpay_order_id: {rzp_id}")
    print(f"   key_id: {key}")
    print(f"   amount: Rs.{amount}")

    if rzp_id.startswith("order_"):
        print("\n   [PASS] Real Razorpay order created successfully!")
        print("   Razorpay checkout will work in browser.")
    else:
        print(f"\n   [FAIL] Unexpected order ID: {rzp_id}")
        sys.exit(1)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"   [FAIL] HTTP {e.code}: {body}")
    sys.exit(1)

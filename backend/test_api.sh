#!/bin/bash
# Test AgriVisionTalk Backend API

API="http://localhost:8000"
echo "=========================================="
echo "Testing AgriVisionTalk Backend API"
echo "=========================================="
echo ""

# Test 1: Health Check
echo "✓ Test 1: Health Check"
curl -s "$API/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Root Endpoint
echo "✓ Test 2: Root Endpoint"
curl -s "$API/" | python3 -m json.tool
echo ""
echo ""

# Test 3: Register New User
echo "✓ Test 3: Register User"
REGISTER_RESPONSE=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@test.com",
    "password": "test12345",
    "confirm_password": "test12345",
    "full_name": "Test Farmer",
    "location": "California",
    "farm_size": "10 acres"
  }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo ""
echo ""

# Test 4: Login
echo "✓ Test 4: Login"  
LOGIN_RESPONSE=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@test.com",
    "password": "test12345"
  }')
echo "$LOGIN_RESPONSE" | python3 -m json.tool

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
echo ""
echo "Access Token: ${ACCESS_TOKEN:0:50}..."
echo ""
echo ""

if [ -n "$ACCESS_TOKEN" ]; then
  # Test 5: Get Current User
  echo "✓ Test 5: Get Current User (Authenticated)"
  curl -s "$API/api/v1/auth/me" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
  echo ""
  echo ""

  # Test 6: Get User Profile
  echo "✓ Test 6: Get User Profile"
  curl -s "$API/api/v1/users/profile" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
  echo ""
  echo ""

  # Test 7: Get User Statistics
  echo "✓ Test 7: Get User Statistics"
  curl -s "$API/api/v1/users/stats" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
  echo ""
  echo ""

  # Test 8: Get Diagnosis History (Empty)
  echo "✓ Test 8: Get Diagnosis History"
  curl -s "$API/api/v1/diagnosis/history" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
  echo ""
  echo ""

  # Test 9: Get Chat Sessions (Empty)
  echo "✓ Test 9: Get Chat Sessions"
  curl -s "$API/api/v1/chat/sessions" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
  echo ""
  echo ""
fi

# Test 10: Login with Admin
echo "✓ Test 10: Login as Admin"
ADMIN_LOGIN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@agrivision.com",
    "password": "admin123"
  }')
echo "$ADMIN_LOGIN" | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "✅ API Testing Complete!"
echo "=========================================="
echo ""
echo "📖 View API Documentation:"
echo "   Swagger UI: http://localhost:8000/api/docs"
echo "   ReDoc: http://localhost:8000/api/redoc"
echo ""

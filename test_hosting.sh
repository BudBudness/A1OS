#!/bin/bash
echo "=== TESTING A1OS HOSTING FEATURES ==="

echo ""
echo "1. Dashboard..."
curl -s http://localhost:3011/dashboard | head -20

echo ""
echo "2. Health Check..."
curl -s http://localhost:3011/v1/health

echo ""
echo "3. Background Job..."
curl -s -X POST http://localhost:3011/job -H "Content-Type: application/json" -d '{"type":"test","data":{"message":"hello"}}'

echo ""
echo "4. Tenant Support..."
curl -s -X POST http://localhost:3011/tenant -H "Content-Type: application/json" -d '{"tenant_id":"test_tenant","data":{"key":"value"}}'

echo ""
echo "=== ALL TESTS COMPLETE ==="

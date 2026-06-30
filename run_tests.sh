#!/usr/bin/env bash
echo "=== TESTING WHATSAPP ENDPOINT ==="
curl -X POST http://localhost:8086/api/v1/webhooks/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"from":"256700000000","text":{"body":"Status report verification"}}],"messaging_product":"whatsapp"}}]}]}'

echo -e "\n\n=== TESTING PESAPAL IPN ENDPOINT ==="
curl -X POST http://localhost:8086/api/v1/payments/pesapal \
  -H "Content-Type: application/json" \
  -d '{"OrderTrackingId":"A1OS-PAY-777","OrderMerchantReference":"REF-009"}'

echo -e "\n\n=== TESTING INGEST ASYNC THREAD ==="
curl -X POST http://localhost:8086/api/v1/ingest/trigger \
  -H "Content-Type: application/json" \
  -d '{"region":"East Africa","depth":"deep_dive"}'
echo ""

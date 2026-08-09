#!/data/data/com.termux/files/usr/bin/bash
# Order an Advanced Certificate covering pos.edge.pyongcity.org (2nd-level
# subdomain) so TLS terminates for it at the Cloudflare edge. Universal SSL
# only covers pyongcity.org + *.pyongcity.org, not pos.edge.pyongcity.org.
#
# Requirements:
#   - Cloudflare API token with Zone (read) + SSL/Certificates (edit) perms
#     for the pyongcity.org zone. Taken from $CLOUDFLARE_API_TOKEN /
#     $CF_API_TOKEN / $CLOUDFLARE_TOKEN (sourced from $HOME/.env or the repo
#     .env if present). Zone ID from $CLOUDFLARE_ZONE_ID / $CF_ZONE_ID, or
#     auto-resolved by zone name.
#   - The DNS record pos.edge.pyongcity.org must exist and be proxied
#     (CNAME to the a1os-prod tunnel). Validation is then automatic via
#     Cloudflare's CNAME delegation (dcv.cloudflare.com).
#
# Usage: ops/a1os-pos-edge-cert.sh [--dry-run]
set -u
export PATH="/data/data/com.termux/files/usr/bin:$PATH"

API="https://api.cloudflare.com/client/v4"
ZONE_NAME="pyongcity.org"
HOSTS='"pyongcity.org","pos.edge.pyongcity.org"'

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

for f in "$HOME/.env" "$HOME/A1OS_RESTORED/.env"; do
    if [ -f "$f" ]; then
        set -a
        . "$f"
        set +a
    fi
done
TOKEN="${CLOUDFLARE_API_TOKEN:-${CF_API_TOKEN:-${CLOUDFLARE_TOKEN:-}}}"
ZONE_ID="${CLOUDFLARE_ZONE_ID:-${CF_ZONE_ID:-}}"

if [ -z "$TOKEN" ]; then
    echo "ERROR: no Cloudflare API token (set CLOUDFLARE_API_TOKEN in .env or shell)" >&2
    exit 1
fi

if [ -z "$ZONE_ID" ]; then
    ZONE_ID="$(curl -fsS --max-time 15 -H "Authorization: Bearer $TOKEN" \
        "$API/zones?name=$ZONE_NAME" | python3 -c \
        'import sys,json;print(json.load(sys.stdin)["result"][0]["id"])' 2>/dev/null)" \
        || { echo "ERROR: could not resolve zone id for $ZONE_NAME" >&2; exit 1; }
fi
echo "zone: $ZONE_NAME ($ZONE_ID)"

PROXIED="$(curl -fsS --max-time 15 -H "Authorization: Bearer $TOKEN" \
    "$API/zones/$ZONE_ID/dns_records?name=pos.edge.$ZONE_NAME" | python3 -c \
    'import sys,json;r=json.load(sys.stdin)["result"];print(r[0]["proxied"] if r else "")' 2>/dev/null || true)"
if [ "$PROXIED" != "True" ]; then
    echo "WARNING: pos.edge.$ZONE_NAME DNS record missing or not proxied."
    echo "  Fix first: cloudflared tunnel route dns a1os-prod pos.edge.$ZONE_NAME"
fi

if [ "$DRY_RUN" = 1 ]; then
    echo "dry-run: would POST $API/zones/$ZONE_ID/ssl/certificate_packs/order"
    echo "  hosts=[$HOSTS] type=advanced validation=txt validity_days=90"
    exit 0
fi

echo "ordering advanced certificate pack (hosts: [$HOSTS])..."
RESP="$(curl -sS --max-time 30 -X POST \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"certificate_authority\":\"lets_encrypt\",\"hosts\":[$HOSTS],\"type\":\"advanced\",\"validation_method\":\"txt\",\"validity_days\":90}" \
    "$API/zones/$ZONE_ID/ssl/certificate_packs/order")"

PACK_ID="$(echo "$RESP" | python3 -c \
    'import sys,json
d=json.load(sys.stdin)
print(d.get("result",{}).get("id",""))' 2>/dev/null || true)"

if [ -z "$PACK_ID" ]; then
    echo "ERROR: order failed:" >&2
    echo "$RESP"
    exit 1
fi
echo "pack ordered: $PACK_ID"

echo "polling until active (validation is automatic via DCV delegation)..."
for i in $(seq 1 12); do
    ST="$(curl -fsS --max-time 15 -H "Authorization: Bearer $TOKEN" \
        "$API/zones/$ZONE_ID/ssl/certificate_packs?status=all" | python3 -c \
        "import sys,json
d=json.load(sys.stdin)
print(next((p['status'] for p in d['result'] if p.get('id')=='$PACK_ID'), 'unknown'))" 2>/dev/null || echo unknown)"
    echo "  status: $ST"
    case "$ST" in
        active)
            echo "DONE: TLS now covers pos.edge.$ZONE_NAME"
            exit 0
            ;;
        validation_timed_out | issuance_timed_out | deployment_timed_out)
            echo "FAIL: $ST — inspect the pack in the Cloudflare dashboard" >&2
            exit 1
            ;;
        pending_validation) echo "  waiting for domain validation (up to ~5 min)..." ;;
        pending_issuance | pending_deployment) echo "  issuing/deploying..." ;;
    esac
    sleep 30
done
echo "TIMEOUT: not active yet. Check https://dash.cloudflare.com SSL/TLS > Edge Certificates"
echo "  (may need the _acme-challenge.pos.edge CNAME delegation records)."
exit 1

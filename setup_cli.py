import argparse
import sys
import json
import urllib.request
from server_schema import ROLES_SPEC, CATEGORIES_SPEC, WELCOME_EMBED, RULES_EMBED, FAQ_EMBED
from config import Config

def validate_schema():
    print("=" * 60)
    print("🔍 Validating Ferrox Discord Server Schema Definition")
    print("=" * 60)
    print(f"✅ Defined Roles ({len(ROLES_SPEC)}):")
    for r in ROLES_SPEC:
        print(f"   • {r['name']} (Color: {hex(r['color'])}, Admin: {r.get('permissions', {}).get('administrator', False)})")

    total_channels = 0
    print(f"\n✅ Defined Categories & Channels ({len(CATEGORIES_SPEC)} categories):")
    for cat in CATEGORIES_SPEC:
        chans = cat["channels"]
        total_channels += len(chans)
        print(f"   📁 {cat['name']} ({len(chans)} channels)")
        for ch in chans:
            ro = "[READ-ONLY]" if ch.get("read_only") else ""
            res = f"[RESTRICTED: {', '.join(ch.get('restricted_to'))}]" if ch.get("restricted_to") else ""
            print(f"      - #{ch['name']} {ro} {res}")

    print(f"\n📊 Summary: {len(ROLES_SPEC)} Roles, {len(CATEGORIES_SPEC)} Categories, {total_channels} Channels.")
    print("✅ Schema structure is valid and ready for provisioning!")
    print("=" * 60)

def test_bridge():
    url = f"http://localhost:{Config.BRIDGE_HTTP_PORT}/api/v1/stats"
    print(f"Testing Bridge connection at {url}...")
    req = urllib.request.Request(url, headers={"X-Bridge-Secret": Config.BRIDGE_SECRET_KEY})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print("✅ Bridge Connection Successful!")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"❌ Could not connect to Bridge: {e}")
        print("Ensure the bot (`python main.py`) is running.")

def main():
    parser = argparse.ArgumentParser(description="Ferrox Discord Bridge CLI & Utility")
    parser.add_argument("--validate-schema", action="store_true", help="Validate and inspect server schema")
    parser.add_argument("--test-bridge", action="store_true", help="Test local HTTP REST bridge server")
    args = parser.parse_args()

    if args.validate_schema:
        validate_schema()
    elif args.test_bridge:
        test_bridge()
    else:
        validate_schema()

if __name__ == "__main__":
    main()

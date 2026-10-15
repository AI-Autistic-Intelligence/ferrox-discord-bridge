#!/usr/bin/env python3
"""
Unit and integration test runner for ferrox-discord-bridge.
Tests trade alerts, Sentinel threat alerts, and polyglot mesh status endpoints.
"""

import asyncio
import sys
from aiohttp import web, ClientSession
from config import Config
from cogs.bridge import BridgeCog

class MockBot:
    guilds = []
    latency = 0.0042

async def run_tests():
    print("====================================================================")
    print("       TESTING FERROX DISCORD BRIDGE (TELEMETRY & ALERTS)           ")
    print("====================================================================")
    
    # 1. Start Bridge in headless mode on test port 8999
    Config.BRIDGE_HTTP_PORT = 8999
    mock_bot = MockBot()
    cog = BridgeCog(mock_bot)
    await cog.cog_load()
    print("  -> Bridge HTTP server started on port 8999.")

    base_url = "http://127.0.0.1:8999"
    headers = {
        "X-Bridge-Secret": Config.BRIDGE_SECRET_KEY,
        "Content-Type": "application/json"
    }

    try:
        async with ClientSession() as session:
            # Test 1: Trade Alert
            print("[Test 1/4] Sending Large Trade Execution Event from ferrox-match...")
            trade_payload = {
                "trade_id": "tr-match-9901",
                "symbol": "BTC/USDT",
                "side": "BUY",
                "price": 68450.0,
                "amount": 1.5,
                "volume_usd": 102675.0,
                "execution_time_ns": 320,
                "channel": "trading-feed"
            }
            async with session.post(f"{base_url}/api/v1/trade-alert", json=trade_payload, headers=headers) as resp:
                assert resp.status == 200, f"Expected 200, got {resp.status}"
                data = await resp.json()
                assert data["status"] == "success"
                assert data["volume_usd"] == 102675.0
                print(f"  -> PASS: Trade alert processed: {data}")

            # Test 2: Sentinel Threat Alert (Entropy H(X) > 4.8)
            print("[Test 2/4] Sending Sentinel Threat Engine Alert (H(X) = 5.12)...")
            sentinel_payload = {
                "alert_id": "sec-sentinel-entropy-99",
                "threat_type": "SHANNON_ENTROPY_ANOMALY",
                "shannon_entropy": 5.12,
                "threshold": 4.80,
                "source_ip": "203.0.113.19",
                "target_endpoint": "/api/v1/rust/orders",
                "action_taken": "BLOCKED & QUARANTINED (403)",
                "payload_sample": "UNION SELECT 1, null, benchmark(10000000,MD5(1))--",
                "channel": "security-alerts"
            }
            async with session.post(f"{base_url}/api/v1/sentinel-alert", json=sentinel_payload, headers=headers) as resp:
                assert resp.status == 200, f"Expected 200, got {resp.status}"
                data = await resp.json()
                assert data["status"] == "success"
                assert data["entropy"] == 5.12
                print(f"  -> PASS: Sentinel threat alert processed: {data}")

            # Test 3: Polyglot Mesh Health Status
            print("[Test 3/4] Fetching Polyglot Mesh Health Status (7 Runtimes)...")
            async with session.get(f"{base_url}/api/v1/mesh-status") as resp:
                assert resp.status == 200, f"Expected 200, got {resp.status}"
                data = await resp.json()
                assert data["status"] == "HEALTHY"
                assert data["services_count"] == 8
                print(f"  -> PASS: Mesh status reported {data['services_count']} runtimes with docs link: {data['docs_url']}")

            # Test 4: Unauthorized Access Rejection
            print("[Test 4/4] Verifying Authentication Barrier...")
            async with session.post(f"{base_url}/api/v1/trade-alert", json={}, headers={"X-Bridge-Secret": "invalid_key"}) as resp:
                assert resp.status == 401, f"Expected 401, got {resp.status}"
                print("  -> PASS: Unauthorized request rejected with 401.")

        print("====================================================================")
        print(">>> ALL 4 DISCORD BRIDGE EVENT TESTS PASSED (100% SUCCESS) <<<")
        print("====================================================================")
        return 0
    finally:
        await cog.cog_unload()

if __name__ == "__main__":
    sys.exit(asyncio.run(run_tests()))

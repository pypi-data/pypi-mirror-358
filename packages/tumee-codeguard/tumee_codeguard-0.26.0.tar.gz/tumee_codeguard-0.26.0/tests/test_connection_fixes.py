#!/usr/bin/env python3
"""
Test script for LLM proxy connection pool fixes.

This script demonstrates the improved connection handling, circuit breaker,
and adaptive timeout features.
"""

import asyncio
import json
import time
from typing import Any, Dict

import aiohttp


async def test_connection_stats(proxy_url: str = "http://localhost:9000") -> Dict[str, Any]:
    """Test the new connection statistics endpoint."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{proxy_url}/connections") as response:
                if response.status == 200:
                    stats = await response.json()
                    print("=== Connection Statistics ===")
                    print(f"Session Active: {stats.get('session_active', 'Unknown')}")
                    print(f"Session Age: {stats.get('session_age_seconds', 0):.1f}s")

                    if "connection_pool" in stats:
                        pool = stats["connection_pool"]
                        print(
                            f"Connection Pool: {pool.get('total_connections', 0)}/{pool.get('limit', 0)} "
                            f"({pool.get('utilization_percent', 0)}% utilized)"
                        )
                        print(f"Per-host limit: {pool.get('limit_per_host', 0)}")

                    if "circuit_breaker" in stats:
                        cb = stats["circuit_breaker"]
                        print(f"Circuit Breaker: {'OPEN' if cb.get('open') else 'CLOSED'}")
                        print(
                            f"Connection Errors: {cb.get('connection_errors', 0)}/{cb.get('max_errors_threshold', 0)}"
                        )

                    if "adaptive_timeout" in stats:
                        timeout = stats["adaptive_timeout"]
                        print(
                            f"Adaptive Timeout: {timeout.get('current_timeout', 0):.1f}s "
                            f"(base: {timeout.get('base_timeout', 0)}s)"
                        )

                    print(
                        f"Active SSE Connections: {stats.get('sse_connections', {}).get('active_count', 0)}"
                    )
                    return stats
                else:
                    print(f"Failed to get connection stats: HTTP {response.status}")
                    return {}
        except Exception as e:
            print(f"Error getting connection stats: {e}")
            return {}


async def test_connection_reset(proxy_url: str = "http://localhost:9000") -> bool:
    """Test the connection reset endpoint."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{proxy_url}/connections/reset") as response:
                if response.status == 200:
                    result = await response.json()
                    print("=== Connection Reset ===")
                    print(f"Status: {result.get('status', 'unknown')}")
                    print(f"Message: {result.get('message', 'no message')}")
                    return True
                else:
                    print(f"Failed to reset connections: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"Error resetting connections: {e}")
            return False


async def simulate_load_test(proxy_url: str = "http://localhost:9000", num_requests: int = 10):
    """Simulate load to test connection pool behavior."""
    print(f"=== Simulating {num_requests} concurrent requests ===")

    async def make_request(session: aiohttp.ClientSession, request_id: int):
        try:
            # Simulate a request to the proxy (this will fail if no upstream is configured, but that's OK)
            async with session.post(
                f"{proxy_url}/v1/messages",
                json={
                    "model": "claude-3-sonnet-20240229",
                    "messages": [{"role": "user", "content": "test"}],
                },
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                print(f"Request {request_id}: HTTP {response.status}")
                return response.status
        except asyncio.TimeoutError:
            print(f"Request {request_id}: Timeout")
            return "timeout"
        except Exception as e:
            print(f"Request {request_id}: Error - {type(e).__name__}")
            return "error"

    # Before load test
    print("\n--- Before Load Test ---")
    await test_connection_stats(proxy_url)

    # Execute concurrent requests
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        tasks = [make_request(session, i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time

        print(f"\nCompleted {num_requests} requests in {elapsed:.2f}s")
        print(f"Average: {elapsed/num_requests:.3f}s per request")

    # After load test
    print("\n--- After Load Test ---")
    await test_connection_stats(proxy_url)


async def main():
    """Main test function."""
    proxy_url = "http://localhost:9001"  # Adjust if your proxy runs on a different port

    print("LLM Proxy Connection Pool Fixes Test")
    print("====================================")

    # Test 1: Get initial connection stats
    print("\n1. Testing connection statistics endpoint...")
    await test_connection_stats(proxy_url)

    # Test 2: Simulate some load
    print("\n2. Simulating load to test connection pool...")
    await simulate_load_test(proxy_url, num_requests=5)

    # Test 3: Test connection reset
    print("\n3. Testing connection reset...")
    await test_connection_reset(proxy_url)

    # Test 4: Check stats after reset
    print("\n4. Checking stats after reset...")
    await test_connection_stats(proxy_url)

    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(main())

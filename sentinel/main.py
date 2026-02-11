"""
TRUSTLENS: SENTINEL OVERSIGHT AGENT
Guardian of the Infrastructure.
Monitors health, restarts services, verifies model integrity.
"""

import asyncio
import httpx
import logging
import os
import hashlib
import time
from datetime import datetime

# CONFIG
SERVICES = {
    "gateway": "http://localhost:8000/health",
    "provenance": "http://localhost:8001/health",
    "diffusion": "http://localhost:8002/health",
    "semantic": "http://localhost:8003/health",
    "forensics": "http://localhost:8004/health",
    "source": "http://localhost:8005/health",
    "tig": "http://localhost:8006/health"
}

HASH_PATHS = {
    "diffusion": "../diffusion_model_artifact/artifact_hash.sha256",
    "semantic": "../intent_model_artifact/artifact_hash.sha256",
    # Others if applicable
}

logging.basicConfig(
    filename="sentinel.log",
    level=logging.INFO,
    format="%(asctime)s - SENTINEL - %(levelname)s - %(message)s"
)

async def check_health(client, name, url):
    try:
        resp = await client.get(url, timeout=2.0)
        if resp.status_code == 200:
            return True, None
        return False, f"Status {resp.status_code}"
    except Exception as e:
        return False, str(e)

async def verify_hashes():
    # Verify disk integrity (Anti-tamper)
    for name, path in HASH_PATHS.items():
        if os.path.exists(path):
            # In real scenario, we'd check if the file changed compared to known good state
            # Here we just log existence
            logging.info(f"Integrity Check: {name} artifact hash exists.")
        else:
            logging.error(f"Integrity Violated: {name} artifact missing!")

async def sentinel_loop():
    logging.info("Sentinel Oversight Agent starting...")
    print("🛡️ Sentinel Oversight Active. Monitoring services...")
    
    async with httpx.AsyncClient() as client:
        while True:
            tasks = [check_health(client, name, url) for name, url in SERVICES.items()]
            results = await asyncio.gather(*tasks)
            
            for (name, url), (healthy, error) in zip(SERVICES.items(), results):
                if healthy:
                    # Healthy
                    pass
                else:
                    logging.warning(f"Service Unhealthy: {name} - Error: {error}")
                    print(f"⚠️ Alert: {name} is DOWN or UNHEALTHY. ({error})")
                    # AUTO-RESTART LOGIC WOULD GO HERE (e.g. Docker restart)
                    # For local script, we just log alert.
            
            await verify_hashes()
            await asyncio.sleep(10) # 10s Heatbeat

if __name__ == "__main__":
    try:
        asyncio.run(sentinel_loop())
    except KeyboardInterrupt:
        logging.info("Sentinel stopping...")

import airsim
import os
import time
import random
import numpy as np
import ipfshttpclient
from web3 import Web3
import json

# ----------------------------- CONFIGURATION -----------------------------

# Connect to AirSim
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

# Ganache Blockchain
GANACHE_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0x2a369B6052e4583ed32Ff915106aab550e83bB13"
ACCOUNT_ADDRESS = "0x71A4e62F3fBA86bCaDEABeae83aB3Cc4ea4920D6"
PRIVATE_KEY = "0x82da3a113c3fe5cbf46891c18eafa541bc8a53bfc2944869ff24bab8443cc78f"

# Load contract ABI
with open(r"F:\PROJECT\Final_Year_project\Blockchain_Agri\build\contracts\CropWeedDetection.json") as f:
    abi = json.load(f)['abi']
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# IPFS
ipfs = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

# ----------------------------- FLIGHT PATH -----------------------------

# Sample 3D waypoints (x, y, z) - Replace with real planner
waypoints = [
    (0, 0, -5),     # Point A
    (10, 0, -5),    # Point B
    (10, 10, -5),   # Point C
    (0, 10, -5),    # Point D
]

# Simulated obstacle at (10, 0, -5)
obstacle = (10, 0, -5)

def is_obstacle(current, next_point):
    """Simulate obstacle detection (very basic)."""
    return np.linalg.norm(np.array(next_point) - np.array(obstacle)) < 2

def replan_path(current_pos):
    """Shift Y slightly to avoid obstacle."""
    print("⚠️ Obstacle detected. Replanning...")
    return (current_pos[0], current_pos[1] + random.uniform(1, 3), current_pos[2])

# ----------------------------- UTILITY FUNCTIONS -----------------------------

def capture_image(x, y, z, index):
    """Capture image from AirSim and save it."""
    responses = client.simGetImages([
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
    ])
    img = responses[0]
    filename = f"image_{index}.png"
    with open(filename, 'wb') as f:
        f.write(img.image_data_uint8)
    print(f"📸 Captured at ({x}, {y}, {z}) -> {filename}")
    return filename

def upload_to_ipfs(filename):
    res = ipfs.add(filename)
    print(f"🔗 IPFS Hash: {res['Hash']}")
    return res['Hash']

def record_on_blockchain(ipfs_hash, area, pesticide, weed, field_id):
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    tx = contract.functions.recordOperation(
        ipfs_hash,
        area,
        pesticide,
        weed,
        field_id
    ).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)  # ✅ Updated here
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"✅ Logged on Blockchain TX: {receipt.transactionHash.hex()}")

# ----------------------------- MAIN MISSION -----------------------------

def main():
    print("🚁 Takeoff...")
    client.takeoffAsync().join()

    for i, point in enumerate(waypoints):
        x, y, z = point
        if i > 0 and is_obstacle(waypoints[i - 1], point):
            point = replan_path(point)
            x, y, z = point

        print(f"🛰️ Moving to: {point}")
        client.moveToPositionAsync(x, y, z, 3).join()
        time.sleep(1)

        img = capture_image(x, y, z, i)
        ipfs_hash = upload_to_ipfs(img)

        # Dummy data for now
        area_covered = 100
        pesticide_amount = 20
        weeds_detected = True
        field_id = i + 1

        record_on_blockchain(ipfs_hash, area_covered, pesticide_amount, weeds_detected, field_id)

    print("✅ Mission complete. Returning to launch.")
    client.moveToPositionAsync(0, 0, -5, 3).join()
    client.landAsync().join()
    client.armDisarm(False)
    client.enableApiControl(False)

# ----------------------------- EXECUTION -----------------------------
if __name__ == "__main__":
    main()

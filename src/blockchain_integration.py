from web3 import Web3
import json
from ipfshttpclient import connect

# Initialize Web3 with Ganache local instance (replace with your Ganache RPC URL)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Ensure connection to Ethereum node
if not w3.isConnected():
    raise Exception("Ethereum connection failed!")

# Your contract ABI and address (use actual values from your contract deployment)
contract_abi = json.loads([
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "operationId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "imageHash",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "areaCovered",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "pesticideAmount",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "bool",
				"name": "weedDetected",
				"type": "bool"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "fieldId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "OperationRecorded",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "operationId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "pesticideAmount",
				"type": "uint256"
			}
		],
		"name": "PesticideSprayTriggered",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "imageHash",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "areaCovered",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "pesticideAmount",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "weedDetected",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "fieldId",
				"type": "uint256"
			}
		],
		"name": "recordOperation",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "operationId",
				"type": "uint256"
			}
		],
		"name": "sprayPesticide",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getMyOperations",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "operationId",
				"type": "uint256"
			}
		],
		"name": "getOperationDetails",
		"outputs": [
			{
				"internalType": "string",
				"name": "imageHash",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "areaCovered",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "pesticideAmount",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "weedDetected",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "fieldId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "operationCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "operations",
		"outputs": [
			{
				"internalType": "string",
				"name": "imageHash",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "areaCovered",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "pesticideAmount",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "weedDetected",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "fieldId",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
])  # Replace with your contract ABI
contract_address = "0xcEC515d02eb053ddDbEDD5e3EF584d995edFb3c9"  # Replace with your contract address

# Set up contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set up your wallet/account for transactions (ensure you have a private key)
my_account = "0x71A4e62F3fBA86bCaDEABeae83aB3Cc4ea4920D6"  # Replace with your wallet address from Ganache
private_key = "0x82da3a113c3fe5cbf46891c18eafa541bc8a53bfc2944869ff24bab8443cc78f"  # Replace with your private key (same account as above)

# Function to send a transaction to the blockchain
def store_detection_data_on_blockchain(ipfs_hash, weed_detected):
    try:
        nonce = w3.eth.getTransactionCount(my_account)
        
        # Estimate gas for the transaction
        gas_estimate = contract.functions.storeDetectionData(ipfs_hash, weed_detected).estimateGas({
            'from': my_account
        })
        
        # Prepare transaction
        transaction = contract.functions.storeDetectionData(ipfs_hash, weed_detected).buildTransaction({
            'chainId': 1337,  # Ganache uses 1337 as chainId (replace if different)
            'gas': gas_estimate + 100000,  # Adding a buffer to the gas estimate
            'gasPrice': w3.toWei('20', 'gwei'),
            'nonce': nonce,
        })
        
        # Sign the transaction
        signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        txn_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
        print(f"Transaction sent. Hash: {txn_hash.hex()}")
        
        # Wait for the transaction receipt
        txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
        print(f"Transaction receipt: {txn_receipt}")
    
    except Exception as e:
        print(f"Error during blockchain transaction: {str(e)}")

# Example Usage
ipfs_hash = "QmSuNur8UsB8Yvz3siRDXdTuu53U29uaQEz6ixpmsGApnH"  # Example IPFS hash
weed_detected = True  # Example result from weed detection

store_detection_data_on_blockchain(ipfs_hash, weed_detected)

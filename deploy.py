import os
from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile Our solidity

install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
with open("compile_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

## for connecting to ganache
# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
# chain_id = 1337
# my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
# private_key = os.getenv("SOLIDITY_PRIVATE_KEY")

# for connecting to rinkeby
w3 = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/761ecf1b9d02423b99f3814bf812e3fa")
)
chain_id = 4
my_address = "0x10dB5444fF21f043DD96f9ec8473c8D2018156e9"
private_key = os.getenv("SOLIDITY_PRIVATE_KEY")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send this signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Deploying contract...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract deployed!")

# Working with contract, you always need
# Contract Address
# Contract ABI

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> not make state change
# Transact -> make state change


print(simple_storage.functions.retrieve().call())
nonce = w3.eth.getTransactionCount(my_address)
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("Updating contract...")
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Contract updated!")
print(simple_storage.functions.retrieve().call())

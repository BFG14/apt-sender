from dotenv import load_dotenv
import os
import asyncio

from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
from aptos_sdk.bcs import Serializer
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.type_tag import StructTag, TypeTag

load_dotenv()

# Specify your target wallet address
TARGET_WALLET_ADDRESS = "0x2f9b85e4bfdc5f047d0242f7a5cff210a5bf39b35f7ccf83db0cf6873b19914d"
# Specify the contract address for WETH
WETH_CONTRACT_ADDRESS = '0x1::coin::CoinStore<0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::WETH>'

TARGET_WALLET_ADDRESS = os.getenv('TARGET_WALLET_ADDRESS')
WETH_CONTRACT_ADDRESS = os.getenv('COIN_CONTRACT_ADDRESS')
NODE_URL = os.getenv('NODE_URL')

async def send_weth(private_key):
    try:
        rest_client = RestClient(NODE_URL)

        # Load account using the provided private key
        account = Account.load_key(private_key)

        # Get the WETH balance
        resource = await rest_client.account_resource(account.address(), WETH_CONTRACT_ADDRESS)
        balance = int(resource["data"]["coin"]["value"])
        print(f"coin balance for {account.address()}: {balance}")

        # Transfer all WETH to the target wallet


        payload = {
            "function": "0x1::aptos_account::transfer_coins",
            "type_arguments": [
                WETH_CONTRACT_ADDRESS
            ],
            "arguments": [
                TARGET_WALLET_ADDRESS,
                str(balance)
            ],
            "type": "entry_function_payload"
            }
        txn_hash = await rest_client.submit_transaction(account, payload)
        await rest_client.wait_for_transaction(txn_hash)

        print(f"All coins transferred from {account.address()} to {TARGET_WALLET_ADDRESS}")

        await rest_client.close()
    except Exception as e:
        with open('error_log.txt', 'a') as file:
            file.write(f"{account.address()}: {str(e)}\n")  # Write the error in the desired format
        print(f"Error occurred for {account.address()}: {str(e)}")

async def main():
    # Read private keys from the file
    with open("private_keys.txt", "r") as f:
        private_keys = f.read().splitlines()

    tasks = [send_weth(private_key) for private_key in private_keys]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
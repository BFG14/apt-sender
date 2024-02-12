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
from dotenv import load_dotenv

load_dotenv()


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
        ticker = WETH_CONTRACT_ADDRESS.split("::")[2].split("<")[0]
        print(f"{ticker} balance for {account.address()}: {balance}")

        # Transfer all WETH to the target wallet


        payload = {
            "function": "0x1::aptos_account::transfer_coins",
            "type_arguments": [
                f'0x1::coin::CoinStore<{WETH_CONTRACT_ADDRESS}>'
            ],
            "arguments": [
                TARGET_WALLET_ADDRESS,
                str(balance)
            ],
            "type": "entry_function_payload"
            }
        txn_hash = await rest_client.submit_transaction(account, payload)
        await rest_client.wait_for_transaction(txn_hash)

        load_dotenv()

        print(f"All {ticker} transferred from {account.address()} to {TARGET_WALLET_ADDRESS}")

        await rest_client.close()
    except Exception as e:
        with open('error_log.txt', 'a') as file:
            error_message = f"Error occurred for {account.address()}: {str(e)}"
            error_type = type(e).__name__
            file.write(f"{account.address()}: {error_type} - {error_message}\n")  # Write the error in the desired format
        print(f"Error occurred for {account.address()}: {error_type} - {str(e)}")

async def main():
    # Read private keys from the file
    with open("private_keys.txt", "r") as f:
        private_keys = f.read().splitlines()

    tasks = [send_weth(private_key) for private_key in private_keys]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
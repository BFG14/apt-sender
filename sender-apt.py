import asyncio
from dotenv import load_dotenv
import os

from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient

load_dotenv()

# Specify your target wallet address
TARGET_WALLET_ADDRESS = os.getenv('TARGET_WALLET_ADDRESS')
NODE_URL = os.getenv('NODE_URL')
GAS = os.getenv('APT_GAS')

async def send_apt(private_key):
    try:
        rest_client = RestClient(NODE_URL)

        # Load account using the provided private key
        account = Account.load_key(private_key)

        # Get the account balance
        balance = await rest_client.account_balance(account.address())
        print(f"Balance for {account.address()}: {balance}")

        # Transfer all APT to the target wallet
        txn_hash = await rest_client.transfer(account, TARGET_WALLET_ADDRESS, balance-int(GAS))
        await rest_client.wait_for_transaction(txn_hash)

        print(f"All APT transferred from {account.address()} to {TARGET_WALLET_ADDRESS}")

        await rest_client.close()
    except Exception as e:
        with open('error_log.txt', 'a') as file:
            file.write(f"{account.address()}: {str(e)}\n")  # Write the error in the desired format
        print(f"Error occurred for {account.address()}: {str(e)}")


async def main():
    # Read private keys from the file
    with open("private_keys.txt", "r") as f:
        private_keys = f.read().splitlines()

    tasks = [send_apt(private_key) for private_key in private_keys]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
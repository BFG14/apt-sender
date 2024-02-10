import asyncio
from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient

# Define your variables
NODE_URL = "https://your_node_url_here"
receiving_wallet_address = "your_receiving_wallet_address"
seed_phrases = [
    "code derive broken onion recipe biology elbow return grid around return canvas",
    "mobile salute seed all joke need abandon find angry gather panel embody",
]

async def main():
    rest_client = RestClient(NODE_URL)

    async def transfer_apt(sender, receiver_address, amount):
        txn_hash = await rest_client.transfer(sender, receiver_address, amount)
        await rest_client.wait_for_transaction(txn_hash)

    async def process_seed_phrase(seed_phrase):
        sender = Account.from_seed(seed_phrase)
        balance = await rest_client.account_balance(sender.address())
        if balance > 0:
            print(f"Transferring {balance} APT from {sender.address()} to {receiving_wallet_address}")
            await transfer_apt(sender, receiving_wallet_address, balance)
        else:
            print(f"No APT balance found for {sender.address()}")

    tasks = [process_seed_phrase(seed_phrase) for seed_phrase in seed_phrases]
    await asyncio.gather(*tasks)

    await rest_client.close()

if __name__ == "__main__":
    asyncio.run(main())
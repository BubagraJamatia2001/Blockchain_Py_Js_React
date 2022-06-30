import requests
import time

from backend.wallet.wallet import Wallet

BASE_URL = 'http://127.0.0.1:5000'

def get_blockchain():
    return requests.get(f'{BASE_URL}/blockchain').json()

def get_blockchain_mine():
    return requests.get(f'{BASE_URL}/blockchain/mine').json()

def post_wallet_transact(recipient, amount):
    return requests.post(
        f'{BASE_URL}/wallet/transact',
        json = {
            "recipient": recipient, 
            "amount": amount
            }
    ).json()

def get_wallet_info():
    return requests.get(f'{BASE_URL}/wallet/info').json()

startBlockchain = get_blockchain()
print(f'start_blockchain: {startBlockchain}')

recipient = Wallet().address

post_wallet_transact_1 = post_wallet_transact(recipient, 21)
print(f'\n-- post_wallet_transact_1: {post_wallet_transact_1}')

time.sleep(1)

post_wallet_transact_2 = post_wallet_transact(recipient, 120)
print(f'\n-- post_wallet_transact_2: {post_wallet_transact_2}')

time.sleep(1)

mined_block = get_blockchain_mine()
print(f'\n mined_blocks: {mined_block}')

walletInfo = get_wallet_info()
print(f'\n-- wallet_info: {walletInfo}')


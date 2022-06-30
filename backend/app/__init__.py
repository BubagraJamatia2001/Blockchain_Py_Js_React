import os
import requests
import random
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS  #middle ware to avoid CORS

from backend.blockchain.blockchain import Blockchain
from backend.pubsub import PubSub
from backend.wallet.transaction import Transaction
from backend.wallet.wallet import Wallet
from backend.wallet.transaction_pool import TransactionPool

args = dict([arg.split('=', maxsplit=1) for arg in sys.argv[1:]])

app = Flask(__name__)
CORS(app, resources={ r'/*': {'origins': 'http://localhost:3000'}})
blockchain = Blockchain()
wallet = Wallet(blockchain)
transactionPool = TransactionPool()
pubsub = PubSub(blockchain, transactionPool)

# for i in range(3):
#     blockchain.add_block(i)

@app.route('/')
def route_default():
    return 'Welcome to the Blockchain'

@app.route('/blockchain')
def route_blockchain():
    return jsonify(blockchain.to_json())

@app.route('/blockchain/range')
def route_blockchain_range():
    start = int(request.args.get('start'))
    end = int(request.args.get('end'))

    return jsonify(blockchain.to_json()[::-1][start:end])

@app.route('/blockchain/length')
def route_blockchain_length():
    return jsonify(len(blockchain.chain))

@app.route('/blockchain/mine')
def route_blockchain_mine():
    # transactionData = 'stubbedTransactionData'
    transactionData = transactionPool.transaction_data()
    transactionData.append(Transaction.reward_transaction(wallet).to_json())

    blockchain.add_block(transactionData)
    block = blockchain.chain[-1]
    pubsub.broadcast_block(block)
    
    transactionPool.clear_blockchain_transactions(blockchain)

    return jsonify(block.to_json())

@app.route('/wallet/transact', methods=['POST'])
def route_wallet_transact():
    # {'recipient}: 'foo', 'amount' : 15}
    transaction_data = request.get_json()
    transaction = transactionPool.existing_transaction(wallet.address)
    
    if transaction:
        transaction.update(
            wallet, 
            transaction_data['recipient'], 
            transaction_data['amount']
            )
    else:
        transaction = Transaction(
            wallet,
            transaction_data['recipient'],
            transaction_data['amount']  
        )
    
    pubsub.broadcast_transaction(transaction)
    # print(f'{transaction.to_json()}')
    return jsonify(transaction.to_json())

@app.route('/wallet/info')
def route_wallet_info():
    return jsonify({'address': wallet.address, 'balance': wallet.balance})

@app.route('/known-addresses')
def route_known_addresses():
    known_addresses = set()

    for block in blockchain.chain:
        for transaction in block.data:
            known_addresses.update(transaction['output'].keys())

    return jsonify(list(known_addresses))

@app.route('/transactions')
def route_transactions():
    return  jsonify(transactionPool.transaction_data())

ROOT_PORT = 5000
PORT = ROOT_PORT

# if os.environ.get('PEER') == 'True':
if args.get('PEER') == 'True':
    PORT = random.randint(5001, 6000)
    result = requests.get(f'http://localhost:{ROOT_PORT}/blockchain')
    print(f'result.json(): {result.json()}')

    result_blockchain = Blockchain.from_json(result.json())
    
    try:
        blockchain.replace_chain(result_blockchain.chain)
        print(f'\n-- Successfully synchronized the local chain')
    except Exception as e:
        print(f'\n-- Error Synchronizing: {e}')

if args.get('SEED') == 'True':
    for i in range(10):
        blockchain.add_block([
            Transaction(Wallet(), Wallet().address, random.randint(2,150)).to_json(),
            Transaction(Wallet(), Wallet().address, random.randint(2,150)).to_json()
        ])
    
    for i in range(3):
        transactionPool.set_transaction(
            Transaction(Wallet(), Wallet().address, random.randint(2, 50))
        )
app.run(port = PORT)
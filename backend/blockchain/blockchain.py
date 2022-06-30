from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
from backend.config import MINING_REWARD_INPUT, MINING_REWARD
from backend.wallet.wallet import Wallet

class Blockchain:
    """
    Blockchain: a public ledger of transactions.
    Implemented as a list of blocks - data sets of transactions
    """
    def __init__(self):
        self.chain = [Block.genesis()]
    
    def add_block(self, data):
        lastBlock = self.chain[-1]
        self.chain.append(Block.mine_block(lastBlock, data))

    def __repr__(self):
        return f'BlockChain : {self.chain}'

    def replace_chain(self, newChain):
        """
        Replace the local chain with th incomming one if the following rules apply:
            - The incoming chain is longer than the local one.
            - The incoming chain is formatted properly.
        """
        if len(newChain) <= len(self.chain):
            raise Exception('Cannot Replace. The incomming chain must be longer.')

        try:
            Blockchain.is_valid_chain(newChain)
        except Exception as e:
            raise Exception(f'Cannot Replace. The incomming chain is invalid: {e}')
        
        self.chain = newChain

    def to_json(self):
        """
        Serialize the blockchain into a list of blocks
        """
        # serialized_chain = []
        # for block in self.chain:
        #     serialized_chain.append(block.to_json())

        # return serialized_chain
        return list(map(lambda block: block.to_json(), self.chain))

    @staticmethod
    def from_json(chain_json):
        '''
        Deserialize a list of serialized blocks into a blockchain instance
        The result will contain a chain list of block instances
        '''
        blockchain = Blockchain()
        blockchain.chain = list(map(lambda block_json: Block.from_json(block_json), chain_json))
        return blockchain

    @staticmethod
    def is_valid_chain(chain):
        """
        validate the incoming chain
        Enforce the following rules of blockchain:
            - The chain must start withg the genesis block
            - blocks must be formatted correctly
        """
        if chain[0] != Block.genesis():
            raise Exception('The genesis block must be valid')

        for i in range(1, len(chain)):
            block = chain[i]
            lastBlock = chain[i - 1]
            Block.is_valid_block(lastBlock, block)
        
        Blockchain.is_valid_transaction_chain(chain)
    
    @staticmethod
    def is_valid_transaction_chain(chain):
        '''
        Enforce the rules of a chain composed of blocks of transactions.
            - Each transactions must only appear once in the chain
            - There can only be one mining reward per block
            - Each transaction must be valid
        '''
        transaction_ids = set()
        for i in range(len(chain)):
            block = chain[i]
            has_mining_reward = False
            for transaction_json in block.data:
                transaction = Transaction.from_json(transaction_json)

                if transaction.id in transaction_ids:
                    raise Exception(f'Transaction {transaction.id} is not unique.')
                
                transaction_ids.add(transaction.id)

                if transaction.input == MINING_REWARD_INPUT:
                    if has_mining_reward:
                        raise Exception(\
                            f'There can only be one mining reward per block. '\
                            f'Check block with hash: {block.hash}'
                            )
                    has_mining_reward = True
                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[0:i]
                    historic_balance = Wallet.calculate_balance(
                        historic_blockchain,
                        transaction.input['address']
                    )
                    if historic_balance != transaction.input['amount']:
                        raise Exception(
                            f'Transaction {transaction.id}'
                            f'has an invalid input amount'
                            )

                Transaction.is_valid_transaction(transaction)

        


def main():
    blockchain1 = Blockchain()
    blockchain1.add_block('one')
    blockchain2 = Blockchain()
    blockchain2.add_block('one')
    blockchain2.add_block('two')
    print(blockchain1.replaceChain(blockchain2.chain))


if __name__ == '__main__':
    main()


import time

from backend.util.crypto_hash import crypto_hash
from backend.util.hex_to_binary import hex_to_binary
from backend.config import MINE_RATE

GENESIS_DATA = {
    'timestamp': 1,
    'lastHash': 'genesis_last_hash',
    'hash': 'genesis_hash',
    'data': [],
    'difficulty': 3,
    'nonce': 'genesis_nonce'
}

class Block:
    """
    Block: a unit of storage
    Stores transactions in a blockchain that supports cryptocurrency.
    """
    def __init__(self, timestamp, lastHash, hash, data, difficulty, nonce):
        self.data = data
        self.timestamp = timestamp
        self.lastHash = lastHash
        self.hash = hash
        self.difficulty = difficulty
        self.nonce = nonce


    def __repr__(self):
        return (
            'Block('
            f'timestamp: {self.timestamp}, '
            f'lastHash: {self.lastHash}, '
            f'hash: {self.hash}, '
            f'data: {self.data}, '
            f'difficulty: {self.difficulty}, '
            f'nonce: {self.nonce} )'
            )

    @staticmethod
    def mine_block(lastBlock, data):
        """
        Mine a block based on teh given lastBlock and data, until a block hash is found that meets the leading 0's proof of work requirement
        """
        timestamp = time.time_ns()
        lastHash = lastBlock.hash
        difficulty = Block.adjust_difficulty(lastBlock, timestamp)
        nonce = 0
        hash = crypto_hash(timestamp, lastHash, data, difficulty, nonce)
        
        while hex_to_binary(hash)[0:difficulty] != '0'*difficulty:
            nonce +=1
            timestamp = time.time_ns()
            difficulty = Block.adjust_difficulty(lastBlock, timestamp)
            hash = crypto_hash(timestamp, lastHash, data, difficulty, nonce)
        
        return Block(timestamp, lastHash, hash, data, difficulty, nonce)

    def to_json(self):
        """
        Serialize the block into a dictionary of its attributes
        """
        return self.__dict__

    @staticmethod
    def genesis():
        """
        Generate the genesis block
        """
        return Block(**GENESIS_DATA)

    @staticmethod
    def from_json(block_json):
        '''
        Deserializes a block's json into a block instance
        '''
        return Block(**block_json)

    
    @staticmethod
    def adjust_difficulty(lastBlock, newTimeStamp):
        """
        This will calculate the adjusted difficulty based on the MINE_RATE.
        Increase the difficulty for quickly mined blocks and 
        Decrease the difficulty for slowly mined blocks.
        """

        if(newTimeStamp - lastBlock.timestamp) < MINE_RATE:
            return lastBlock.difficulty + 1
        
        if(lastBlock.difficulty - 1) > 0:
            return lastBlock.difficulty - 1
        
        return 1
        
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @staticmethod
    def is_valid_block(lastBlock, block):
        """
        Validate the block by enforcing the following rules:
            - the block must have the proper lastHash reference
            - the block must meet the proof of work requirement
            - the difficulty must only adjust by 1
            - the block hash must be a valid combination of the block fields 
        """
        # print(block.lastHash == lastBlock.hash)
        if block.lastHash != lastBlock.hash:
        # if lastBlock.lastHash != block.hash:
            raise Exception(f'1. The Block lastHash must be correct. {block.hash} {lastBlock.hash} {block.lastHash} {lastBlock.lastHash}')
        
        if hex_to_binary(block.hash)[0:block.difficulty] != '0' * block.difficulty:
            raise Exception('2. The proof of work requirement is not met.')
        
        if abs(lastBlock.difficulty - block.difficulty)> 1:
            raise Exception('3. The block difficulty must only be adjusted by 1.')
        
        reconstructedHash = crypto_hash(
            block.timestamp, 
            block.lastHash, 
            block.data, 
            block.difficulty, 
            block.nonce
        )

        if reconstructedHash != block.hash:
            raise Exception(f'4. The block hash must be correct.')


def main():
    genesis_block = Block.genesis()
    # print(genesis_block)
    block = Block.mine_block(genesis_block, 'foo')
    # print(block)
    try:
        Block.is_valid_block(genesis_block, block)
    except Exception as e:
        print(f'isValidBlock: {e}')


if __name__ == '__main__':
    main() 
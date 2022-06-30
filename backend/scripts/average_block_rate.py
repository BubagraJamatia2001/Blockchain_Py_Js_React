from backend.blockchain.blockchain import Blockchain
from backend.config import SECONDS
import time

blockchain = Blockchain()
times = []
blockchain.add_block(0)
for i in range(1,1000):
    # startTime = time.time_ns()
    startTime = blockchain.chain[-1].timestamp
    blockchain.add_block(i)
    # endTime = time.time_ns()
    endTime = blockchain.chain[-1].timestamp

    timeToMine = (endTime - startTime) / SECONDS
    times.append(timeToMine)

    averageTime = sum(times)/len(times)

    print(f'New Block Difficulty {blockchain.chain[-1].data}: {blockchain.chain[-1].difficulty} ')
    print(f'Time to mine New Block: {timeToMine}s ')
    print(f'Average Time to add Blocks: {averageTime}s \n')
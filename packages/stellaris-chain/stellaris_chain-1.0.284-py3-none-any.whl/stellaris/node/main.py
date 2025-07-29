import random
from asyncio import gather
from collections import deque
import os
from dotenv import dotenv_values
import re
import json
from decimal import Decimal
from datetime import datetime 

from asyncpg import UniqueViolationError
from fastapi import FastAPI, Body, Query
from fastapi.responses import RedirectResponse, Response

from httpx import TimeoutException
#from icecream import ic
from starlette.background import BackgroundTasks, BackgroundTask
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from stellaris.utils.general import timestamp, sha256, transaction_to_json
from stellaris.manager import create_block, get_difficulty, Manager, get_transactions_merkle_tree, \
    split_block_content, calculate_difficulty, clear_pending_transactions, block_to_bytes, get_transactions_merkle_tree_ordered
from stellaris.node.nodes_manager import NodesManager, NodeInterface
from stellaris.node.utils import ip_is_local
from stellaris.transactions import Transaction, CoinbaseTransaction
from stellaris.database import Database
from stellaris.constants import VERSION, ENDIAN


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
db: Database = None
NodesManager.init()
started = False
is_syncing = False
self_url = None

#print = ic

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

config = dotenv_values(".env")

async def propagate(path: str, args: dict, ignore_url=None, nodes: list = None):
    global self_url
    self_node = NodeInterface(self_url or '')
    ignore_node = NodeInterface(ignore_url or '')
    aws = []
    for node_url in nodes or NodesManager.get_propagate_nodes():
        node_interface = NodeInterface(node_url)
        if node_interface.base_url == self_node.base_url or node_interface.base_url == ignore_node.base_url:
            continue
        aws.append(node_interface.request(path, args, self_node.url))
    for response in await gather(*aws, return_exceptions=True):
        print('node response: ', response)


async def create_blocks(blocks: list):
    _, last_block = await calculate_difficulty()
    last_block['id'] = last_block['id'] if last_block != {} else 0
    last_block['hash'] = last_block['hash'] if 'hash' in last_block else (30_06_2005).to_bytes(32, ENDIAN).hex()
    i = last_block['id'] + 1
    for block_info in blocks:
        block = block_info['block']
        txs_hex = block_info['transactions']
        txs = [await Transaction.from_hex(tx) for tx in txs_hex]
        #txs = [await Transaction.from_hex(tx, set_timestamp=True) for tx in txs_hex]
        for tx in txs:
            if isinstance(tx, CoinbaseTransaction):
                txs.remove(tx)
                break
        hex_txs = [tx.hex() for tx in txs]
        block['merkle_tree'] = get_transactions_merkle_tree(hex_txs) if i > 22500 else get_transactions_merkle_tree_ordered(hex_txs)
        block_content = block.get('content') or block_to_bytes(last_block['hash'], block)

        if i <= 22500 and sha256(block_content) != block['hash'] and i != 17972:
            from itertools import permutations
            for l in permutations(hex_txs):
                _hex_txs = list(l)
                block['merkle_tree'] = get_transactions_merkle_tree_ordered(_hex_txs)
                block_content = block_to_bytes(last_block['hash'], block)
                if sha256(block_content) == block['hash']:
                    break
        elif 131309 < i < 150000 and sha256(block_content) != block['hash']:
            for diff in range(0, 100):
                block['difficulty'] = diff / 10
                block_content = block_to_bytes(last_block['hash'], block)
                if sha256(block_content) == block['hash']:
                    break
        assert i == block['id']
        if not await create_block(block_content.hex() if isinstance(block_content, bytes) else block_content, txs, last_block):
            return False
        last_block = block
        i += 1
    return True


async def _sync_blockchain(node_url: str = None):
    print('sync blockchain')
    if not node_url:
        nodes = NodesManager.get_recent_nodes()
        if not nodes:
            return
        node_url = random.choice(nodes)
    node_url = node_url.strip('/')
    _, last_block = await calculate_difficulty()
    starting_from = i = await db.get_next_block_id()
    node_interface = NodeInterface(node_url)
    local_cache = None
    if last_block != {} and last_block['id'] > 500:
        remote_last_block = (await node_interface.get_block(i-1))['block']
        if remote_last_block['hash'] != last_block['hash']:
            print(remote_last_block['hash'])
            offset, limit = i - 500, 500
            remote_blocks = await node_interface.get_blocks(offset, limit)
            local_blocks = await db.get_blocks(offset, limit)
            local_blocks = local_blocks[:len(remote_blocks)]
            local_blocks.reverse()
            remote_blocks.reverse()
            print(len(remote_blocks), len(local_blocks))
            for n, local_block in enumerate(local_blocks):
                if local_block['block']['hash'] == remote_blocks[n]['block']['hash']:
                    print(local_block, remote_blocks[n])
                    last_common_block = local_block['block']['id']
                    local_cache = local_blocks[:n]
                    local_cache.reverse()
                    await db.remove_blocks(last_common_block + 1)
                    break

    #return
    limit = 1000
    while True:
        i = await db.get_next_block_id()
        try:
            blocks = await node_interface.get_blocks(i, limit)
        except Exception as e:
            print(e)
            #NodesManager.get_nodes().remove(node_url)
            NodesManager.sync()
            break
        try:
            _, last_block = await calculate_difficulty()
            if not blocks:
                print('syncing complete')
                if last_block['id'] > starting_from:
                    NodesManager.update_last_message(node_url)
                    if timestamp() - last_block['timestamp'] < 86400:
                        # if last block is from less than a day ago, propagate it
                        txs_hashes = await db.get_block_transaction_hashes(last_block['hash'])
                        await propagate('push_block', {'block_content': last_block['content'], 'txs': txs_hashes, 'block_no': last_block['id']}, node_url)
                break
            assert await create_blocks(blocks)
        except Exception as e:
            print(e)
            if local_cache is not None:
                print('sync failed, reverting back to previous chain')
                await db.delete_blocks(last_common_block)
                await create_blocks(local_cache)
            return


async def sync_blockchain(node_url: str = None):
    try:
        await _sync_blockchain(node_url)
    except Exception as e:
        print(e)
        return


@app.on_event("startup")
async def startup():
    global db
    global config
    db = await Database.create(
        user=config['STELLARIS_DATABASE_USER'] if 'STELLARIS_DATABASE_USER' in config else "stellaris" ,
        password=config['STELLARIS_DATABASE_PASSWORD'] if 'STELLARIS_DATABASE_PASSWORD' in config else 'stellaris',
        database=config['STELLARIS_DATABASE_NAME'] if 'STELLARIS_DATABASE_NAME' in config else "stellaris",
        host=config['STELLARIS_DATABASE_HOST'] if 'STELLARIS_DATABASE_HOST' in config else None
    )


@app.get("/")
async def root():
    return {"version": VERSION, "unspent_outputs_hash": await db.get_unspent_outputs_hash()}


async def propagate_old_transactions(propagate_txs):
    await db.update_pending_transactions_propagation_time([sha256(tx_hex) for tx_hex in propagate_txs])
    for tx_hex in propagate_txs:
        await propagate('push_tx', {'tx_hex': tx_hex})


@app.middleware("http")
async def middleware(request: Request, call_next):
    global started, self_url
    nodes = NodesManager.get_recent_nodes()
    hostname = request.base_url.hostname

    # Normalize the URL path by removing extra slashes
    normalized_path = re.sub('/+', '/', request.scope['path'])
    if normalized_path != request.scope['path']:
        url = request.url
        new_url = str(url).replace(request.scope['path'], normalized_path)
        #Redirect to normalized URL
        return RedirectResponse(new_url)

    if 'Sender-Node' in request.headers:
        NodesManager.add_node(request.headers['Sender-Node'])

    if nodes and not started or (ip_is_local(hostname) or hostname == 'localhost'):
        try:
            node_url = nodes[0]
            #requests.get(f'{node_url}/add_node', {'url': })
            j = await NodesManager.request(f'{node_url}/get_nodes')
            nodes.extend(j['result'])
            NodesManager.sync()
        except:
            pass

        if not (ip_is_local(hostname) or hostname == 'localhost'):
            started = True

            self_url = str(request.base_url).strip('/')
            try:
                nodes.remove(self_url)
            except ValueError:
                pass
            try:
                nodes.remove(self_url.replace("http://", "https://"))
            except ValueError:
                pass

            NodesManager.sync()

            try:
                await propagate('add_node', {'url': self_url})
                cousin_nodes = sum(await NodeInterface(url).get_nodes() for url in nodes)
                await propagate('add_node', {'url': self_url}, nodes=cousin_nodes)
            except:
                pass
    propagate_txs = await db.get_need_propagate_transactions()
    try:
        response = await call_next(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        if propagate_txs:
            response.background = BackgroundTask(propagate_old_transactions, propagate_txs)
        return response
    except:
        raise
        return {'ok': False, 'error': 'Internal error'}


@app.exception_handler(Exception)
async def exception_handler(request: Request, e: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": f"Uncaught {type(e).__name__} exception"},
    )

transactions_cache = deque(maxlen=100)


@app.get("/push_tx")
@app.post("/push_tx")
async def push_tx(request: Request, background_tasks: BackgroundTasks, tx_hex: str = None, body=Body(False)):
    if body and tx_hex is None:
        tx_hex = body['tx_hex']
    tx = await Transaction.from_hex(tx_hex)
    if tx.hash() in transactions_cache:
        return {'ok': False, 'error': 'Transaction just added'}
    try:
        if await db.add_pending_transaction(tx):
            if 'Sender-Node' in request.headers:
                NodesManager.update_last_message(request.headers['Sender-Node'])
            background_tasks.add_task(propagate, 'push_tx', {'tx_hex': tx_hex})
            transactions_cache.append(tx.hash())
            return {'ok': True, 'result': 'Transaction has been accepted'}
        else:
            return {'ok': False, 'error': 'Transaction has not been added'}
    except UniqueViolationError:
        return {'ok': False, 'error': 'Transaction already present'}


@app.post("/push_block")
@app.get("/push_block")
async def push_block(request: Request, background_tasks: BackgroundTasks, block_content: str = '', txs='', block_no: int = None, body=Body(False)):
    if is_syncing:
        return {'ok': False, 'error': 'Node is already syncing'}
    if body:
        txs = body['txs']
        if 'block_content' in body:
            block_content = body['block_content']
        if 'id' in body:
            block_no = body['id']
        if 'block_no' in body:
            block_no = body['block_no']
    if isinstance(txs, str):
        txs = txs.split(',')
        if txs == ['']:
            txs = []
    previous_hash = split_block_content(block_content)[0]
    next_block_id = await db.get_next_block_id()
    if block_no is None:
        previous_block = await db.get_block(previous_hash)
        if previous_block is None:
            if 'Sender-Node' in request.headers:
                background_tasks.add_task(sync_blockchain, request.headers['Sender-Node'])
                return {'ok': False,
                        'error': 'Previous hash not found, had to sync according to sender node, block may have been accepted'}
            else:
                return {'ok': False, 'error': 'Previous hash not found'}
        block_no = previous_block['id'] + 1
    if next_block_id < block_no:
        background_tasks.add_task(sync_blockchain, request.headers['Sender-Node'] if 'Sender-Node' in request.headers else None)
        return {'ok': False, 'error': 'Blocks missing, had to sync according to sender node, block may have been accepted'}
    if next_block_id > block_no:
        return {'ok': False, 'error': 'Too old block'}
    final_transactions = []
    hashes = []
    for tx_hex in txs:
        if len(tx_hex) == 64:  # it's an hash
            hashes.append(tx_hex)
        else:
            final_transactions.append(await Transaction.from_hex(tx_hex))
    if hashes:
        pending_transactions = await db.get_pending_transactions_by_hash(hashes)
        if len(pending_transactions) < len(hashes):  # one or more tx not found
            if 'Sender-Node' in request.headers:
                background_tasks.add_task(sync_blockchain, request.headers['Sender-Node'])
                return {'ok': False,
                        'error': 'Transaction hash not found, had to sync according to sender node, block may have been accepted'}
            else:
                return {'ok': False, 'error': 'Transaction hash not found'}
        final_transactions.extend(pending_transactions)
    if not await create_block(block_content, final_transactions):
        return {'ok': False}

    if 'Sender-Node' in request.headers:
        NodesManager.update_last_message(request.headers['Sender-Node'])

    background_tasks.add_task(propagate, 'push_block', {
        'block_content': block_content,
        'txs': [tx.hex() for tx in final_transactions] if len(final_transactions) < 10 else txs,
        'block_no': block_no
    })
    return {'ok': True}


@app.get("/sync_blockchain")
@limiter.limit("10/minute")
async def sync(request: Request, node_url: str = None):
    global is_syncing
    if is_syncing:
        return {'ok': False, 'error': 'Node is already syncing'}
    is_syncing = True
    await sync_blockchain(node_url)
    is_syncing = False


async def sync_pending_transactions():
    """Sync pending transactions from other nodes if we have none"""
    if await db.get_pending_transactions_limit(1, hex_only=True):
        return  # We already have pending transactions
    
    nodes = NodesManager.get_recent_nodes()
    for node_url in nodes:
        try:
            node_interface = NodeInterface(node_url)
            response = await node_interface.request('get_pending_transactions', {})
            if response.get('ok') and response.get('result'):
                remote_txs = response['result'][:10]  # Get up to 10 transactions
                for tx_hex in remote_txs:
                    try:
                        tx = await Transaction.from_hex(tx_hex)
                        await db.add_pending_transaction(tx)
                        print(f"Synced transaction from {node_url}: {tx.hash()}")
                    except Exception as e:
                        print(f"Failed to sync transaction {tx_hex[:16]}...: {e}")
                if remote_txs:
                    print(f"Synced {len(remote_txs)} pending transactions from {node_url}")
                    break  # Stop after successfully syncing from one node
        except Exception as e:
            print(f"Failed to sync pending transactions from {node_url}: {e}")


LAST_PENDING_TRANSACTIONS_CLEAN = [0]
LAST_PENDING_SYNC = [0]


@app.get("/get_mining_info")
async def get_mining_info(background_tasks: BackgroundTasks, pretty: bool = False):
    Manager.difficulty = None
    difficulty, last_block = await get_difficulty()
    
    # Sync pending transactions if we have none and it's been a while
    if LAST_PENDING_SYNC[0] < timestamp() - 30:  # Sync every 30 seconds
        LAST_PENDING_SYNC[0] = timestamp()
        background_tasks.add_task(sync_pending_transactions)
    
    pending_transactions = await db.get_pending_transactions_limit(hex_only=True)
    pending_transactions = sorted(pending_transactions)
    if LAST_PENDING_TRANSACTIONS_CLEAN[0] < timestamp() - 600:
        print(LAST_PENDING_TRANSACTIONS_CLEAN[0])
        LAST_PENDING_TRANSACTIONS_CLEAN[0] = timestamp()
        background_tasks.add_task(clear_pending_transactions, pending_transactions)
    result = {'ok': True, 'result': {
        'difficulty': difficulty,
        'last_block': last_block,
        'pending_transactions': pending_transactions[:10],
        'pending_transactions_hashes': [sha256(tx) for tx in pending_transactions[:10]],
        'merkle_root': get_transactions_merkle_tree(pending_transactions[:10])
    }}
    return Response(content=json.dumps(result, indent=4, cls=CustomJSONEncoder), media_type="application/json") if pretty else result


@app.get("/get_address_info")
@limiter.limit("8/second")
async def get_address_info(request: Request, address: str, transactions_count_limit: int = Query(default=5, le=50), page: int = Query(default=1, ge=1), show_pending: bool = False, verify: bool = False, pretty: bool = False):    
    outputs = await db.get_spendable_outputs(address)
    balance = sum(output.amount for output in outputs)
    
     # Calculate offset for pagination
    offset = (page - 1) * transactions_count_limit
    
    # Fetch transactions with pagination
    transactions = await db.get_address_transactions(address, limit=transactions_count_limit, offset=offset, check_signatures=True) if transactions_count_limit > 0 else []

    result = {'ok': True, 'result': {
        'balance': "{:f}".format(balance),
        'spendable_outputs': [{'amount': "{:f}".format(output.amount), 'tx_hash': output.tx_hash, 'index': output.index} for output in outputs],
        'transactions': [await db.get_nice_transaction(tx.hash(), address if verify else None) for tx in transactions],
        #'transactions': [await db.get_nice_transaction(tx.hash(), address if verify else None) for tx in await db.get_address_transactions(address, limit=transactions_count_limit, check_signatures=True)] if transactions_count_limit > 0 else [],
        'pending_transactions': [await db.get_nice_transaction(tx.hash(), address if verify else None) for tx in await db.get_address_pending_transactions(address, True)] if show_pending else None,
        'pending_spent_outputs': await db.get_address_pending_spent_outputs(address) if show_pending else None
    }}
    return Response(content=json.dumps(result, indent=4, cls=CustomJSONEncoder), media_type="application/json") if pretty else result


@app.get("/add_node")
@limiter.limit("10/minute")
async def add_node(request: Request, url: str, background_tasks: BackgroundTasks):
    nodes = NodesManager.get_nodes()
    url = url.strip('/')
    if url == self_url:
        return {'ok': False, 'error': 'Recursively adding node'}
    if url in nodes:
        return {'ok': False, 'error': 'Node already present'}
    else:
        try:
            assert await NodesManager.is_node_working(url)
            background_tasks.add_task(propagate, 'add_node', {'url': url}, url)
            NodesManager.add_node(url)
            return {'ok': True, 'result': 'Node added'}
        except Exception as e:
            print(e)
            return {'ok': False, 'error': 'Could not add node'}


@app.get("/get_nodes")
async def get_nodes(pretty: bool = False):
    result = {'ok': True, 'result': NodesManager.get_recent_nodes()[:100]}
    return Response(content=json.dumps(result, indent=4, cls=CustomJSONEncoder), media_type="application/json") if pretty else result


@app.get("/get_pending_transactions")
async def get_pending_transactions(pretty: bool = False):
    result = {'ok': True, 'result': [tx.hex() for tx in await db.get_pending_transactions_limit(1000)]}
    return Response(content=json.dumps(result, indent=4, cls=CustomJSONEncoder), media_type="application/json") if pretty else result


@app.get("/get_transaction")
@limiter.limit("8/second")
async def get_transaction(request: Request, tx_hash: str, verify: bool = False, pretty: bool = False):
    tx = await db.get_nice_transaction(tx_hash)
    if tx is None:
        result = {'ok': False, 'error': 'Transaction not found'}
    else:
        result = {'ok': True, 'result': tx}
    return Response(content=json.dumps(result, indent=4, cls=CustomJSONEncoder), media_type="application/json") if pretty else result


@app.get("/get_block")
@limiter.limit("30/minute")
async def get_block(request: Request, block: str, full_transactions: bool = False, pretty: bool = False):
    if block.isdecimal():
        block_info = await db.get_block_by_id(int(block))
        if block_info is not None:
            block_hash = block_info['hash']
        else:
            result = {'ok': False, 'error': 'Block not found'}
    else:
        block_hash = block
        block_info = await db.get_block(block_hash)
    if block_info:
        result = {'ok': True, 'result': {
            'block': block_info,
            'transactions': await db.get_block_transactions(block_hash, hex_only=True) if not full_transactions else None,
            'full_transactions': await db.get_block_nice_transactions(block_hash) if full_transactions else None
        }}
    else:
        result = {'ok': False, 'error': 'Block not found'}
    return Response(content=json.dumps(result, indent=4, cls=CustomJSONEncoder), media_type="application/json") if pretty else result


@app.get("/get_blocks")
@limiter.limit("10/minute")
async def get_blocks(request: Request, offset: int, limit: int = Query(default=..., le=1000), pretty: bool = False):
    blocks = await db.get_blocks(offset, limit)
    result = {'ok': True, 'result': blocks}
    return Response(content=json.dumps(result, indent=4, cls=CustomJSONEncoder), media_type="application/json") if pretty else result

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (Decimal, datetime)):
            return str(o)  # Convert types to string to prevent serialization errors
        return super().default(o)
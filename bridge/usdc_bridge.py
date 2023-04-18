import json
import time
from web3 import Web3
from web3.auto import w3

# enter slippage as shown => 1 = 0.1%, 5 = 0.5%, 10 = 1%
SLIPPAGE = 5

# RPCs
polygon_rpc_url = 'https://polygon-rpc.com/'
fantom_rpc_url = 'https://rpc.ftm.tools/'

polygon_w3 = Web3(Web3.HTTPProvider(polygon_rpc_url))
fantom_w3 = Web3(Web3.HTTPProvider(fantom_rpc_url))

# Stargate Router
stargate_polygon_address = w3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
stargate_fantom_address = w3.to_checksum_address('0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6')

# ABIs
stargate_abi = json.load(open('./abis/router_abi.json'))
usdc_abi = json.load(open('./abis/usdc_abi.json'))

# USDC contracts
usdc_polygon_address = w3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
usdc_fantom_address = w3.to_checksum_address('0x04068DA6C83AFCFA0e13ba15A6696662335D5B75')

# Init contracts
stargate_polygon_contract = polygon_w3.eth.contract(address=stargate_polygon_address, abi=stargate_abi)
stargate_fantom_contract = fantom_w3.eth.contract(address=stargate_fantom_address, abi=stargate_abi)
usdc_polygon_contract = polygon_w3.eth.contract(address=usdc_polygon_address, abi=usdc_abi)
usdc_fantom_contract = fantom_w3.eth.contract(address=usdc_fantom_address, abi=usdc_abi)


# Polygon -> Fantom USDC Bridge


def get_balance_usdc_polygon(address):
    return usdc_polygon_contract.functions.balanceOf(address).call()


def get_balance_usdc_fantom(address):
    return usdc_fantom_contract.functions.balanceOf(address).call()


def swap_usdc_polygon_to_fantom(account, amount):
    address = w3.to_checksum_address(account.address)
    nonce = polygon_w3.eth.get_transaction_count(address)
    gas_price = polygon_w3.eth.gas_price
    fees = stargate_fantom_contract.functions.quoteLayerZeroFee(112,
                                                                1,
                                                                "0x0000000000000000000000000000000000001010",
                                                                "0x",
                                                                [0, 0, "0x0000000000000000000000000000000000000001"]
                                                                ).call()
    fee = fees[0]

    # Check allowance
    allowance = usdc_polygon_contract.functions.allowance(address, stargate_polygon_address).call()
    if allowance < amount:
        approve_txn = usdc_polygon_contract.functions.approve(stargate_polygon_address, amount).build_transaction({
            'from': address,
            'gas': 150000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        signed_approve_txn = polygon_w3.eth.account.sign_transaction(approve_txn, account.key)
        approve_txn_hash = polygon_w3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)

        print(f"POLYGON | USDT APPROVED https://polygonscan.com/tx/{approve_txn_hash.hex()}")
        nonce += 1

        time.sleep(10)

    # Stargate Swap
    chainId = 112
    source_pool_id = 1
    dest_pool_id = 1
    refund_address = account.address
    amountIn = amount
    amountOutMin = amount - (amount * SLIPPAGE) // 1000
    lzTxObj = [0, 0, '0x0000000000000000000000000000000000000001']
    to = account.address
    data = '0x'

    swap_txn = stargate_polygon_contract.functions.swap(
        chainId, source_pool_id, dest_pool_id, refund_address, amountIn, amountOutMin, lzTxObj, to, data
    ).build_transaction({
        'from': address,
        'value': fee,
        'gas': 2000000,
        'gasPrice': polygon_w3.eth.gas_price,
        'nonce': polygon_w3.eth.get_transaction_count(address),
    })

    signed_swap_txn = polygon_w3.eth.account.sign_transaction(swap_txn, account.key)
    swap_txn_hash = polygon_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash


# Fantom -> Polygon USDC
def swap_usdc_fantom_to_polygon(account, amount):
    address = w3.to_checksum_address(account.address)
    nonce = fantom_w3.eth.get_transaction_count(address)
    gas_price = fantom_w3.eth.gas_price
    fees = stargate_fantom_contract.functions.quoteLayerZeroFee(109,
                                                       1,
                                                       "0x0000000000000000000000000000000000000001",
                                                       "0x",
                                                       [0, 0, "0x0000000000000000000000000000000000000001"]
                                                       ).call()
    fee = fees[0]

    # Check Allowance
    allowance = usdc_fantom_contract.functions.allowance(address, stargate_fantom_address).call()
    if allowance < amount:
        approve_txn = usdc_fantom_contract.functions.approve(stargate_fantom_address, amount).build_transaction({
            'from': address,
            'gas': 150000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        signed_approve_txn = fantom_w3.eth.account.sign_transaction(approve_txn, account.key)
        approve_txn_hash = fantom_w3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)

        print(f"FANTOM | USDC APPROVED | https://ftmscan.com/tx/{approve_txn_hash.hex()} ")
        nonce += 1

        time.sleep(10)

    # Stargate Swap
    chainId = 109
    source_pool_id = 1
    dest_pool_id = 1
    refund_address = account.address
    amountIn = amount
    amountOutMin = amount - (amount * SLIPPAGE) // 1000
    lzTxObj = [0, 0, '0x0000000000000000000000000000000000000001']
    to = account.address
    data = '0x'

    swap_txn = stargate_polygon_contract.functions.swap(
        chainId, source_pool_id, dest_pool_id, refund_address, amountIn, amountOutMin, lzTxObj, to, data
    ).build_transaction({
        'from': address,
        'value': fee,
        'gas': 2000000,
        'gasPrice': fantom_w3.eth.gas_price,
        'nonce': fantom_w3.eth.get_transaction_count(address),
    })

    signed_swap_txn = fantom_w3.eth.account.sign_transaction(swap_txn, account.key)
    swap_txn_hash = fantom_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash

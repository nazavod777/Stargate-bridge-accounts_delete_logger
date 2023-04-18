import json
import time
from web3 import Web3
from web3.auto import w3

# enter slippage as shown => 1 = 0.1%, 5 = 0.5%, 10 = 1%
SLIPPAGE = 5

# RPCs
arbitrum_rpc_url = 'https://rpc.ankr.com/arbitrum'
optimism_rpc_url = 'https://1rpc.io/op'

arbitrum_w3 = Web3(Web3.HTTPProvider(arbitrum_rpc_url))
optimism_w3 = Web3(Web3.HTTPProvider(optimism_rpc_url))

# Stargate Router
stargate_arbitrum_address = w3.to_checksum_address('0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614')
stargate_optimism_address = w3.to_checksum_address('0xB0D502E938ed5f4df2E681fE6E419ff29631d62b')

# Stargate ETH Router
stargate_arbitrum_eth_address = w3.to_checksum_address('0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40')
stargate_optimism_eth_address = w3.to_checksum_address('0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b')

# ABIs
router_abi = json.load(open('./abis/router_abi.json'))
router_eth_abi = json.load(open('./abis/router_eth_abi.json'))

# Init contracts
stargate_arbitrum_router_contract = arbitrum_w3.eth.contract(address=stargate_arbitrum_address, abi=router_abi)
stargate_optimism_router_contract = optimism_w3.eth.contract(address=stargate_optimism_address, abi=router_abi)

stargate_arbitrum_router_eth_contract = arbitrum_w3.eth.contract(address=stargate_arbitrum_eth_address,
                                                                 abi=router_eth_abi)
stargate_optimism_router_eth_contract = optimism_w3.eth.contract(address=stargate_optimism_eth_address,
                                                                 abi=router_eth_abi)


def get_balance_eth_arbitrum(address):
    return arbitrum_w3.eth.get_balance(address)


def get_balance_eth_optimism(address):
    return optimism_w3.eth.get_balance(address)


def swap_eth_arbitrum_optimism(account, amount):
    address = w3.to_checksum_address(account.address)
    nonce = arbitrum_w3.eth.get_transaction_count(address)
    gas_price = arbitrum_w3.eth.gas_price
    fees = stargate_arbitrum_router_contract.functions.quoteLayerZeroFee(111,
                                                                         1,
                                                                         address,
                                                                         "0x",
                                                                         [0, 0, address]
                                                                         ).call()
    fee = fees[0]

    amountOutMin = amount - (amount * SLIPPAGE) // 1000

    swap_txn = stargate_arbitrum_router_eth_contract.functions.swapETH(
        111, address, address, amount, amountOutMin
    ).build_transaction({
        'from': address,
        'value': amount + fee,
        'gas': 2000000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    signed_swap_txn = arbitrum_w3.eth.account.sign_transaction(swap_txn, account.key)
    swap_txn_hash = arbitrum_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash


def swap_eth_optimism_arbitrum(account, amount):
    address = w3.to_checksum_address(account.address)
    nonce = optimism_w3.eth.get_transaction_count(address)
    gas_price = optimism_w3.eth.gas_price
    fees = stargate_optimism_router_contract.functions.quoteLayerZeroFee(110,
                                                                         1,
                                                                         address,
                                                                         "0x",
                                                                         [0, 0, address]
                                                                         ).call()
    fee = fees[0]

    amountOutMin = amount - (amount * SLIPPAGE) // 1000

    swap_txn = stargate_optimism_router_eth_contract.functions.swapETH(
        110, address, address, amount, amountOutMin
    ).build_transaction({
        'from': address,
        'value': amount + fee,
        'gas': 2000000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    signed_swap_txn = optimism_w3.eth.account.sign_transaction(swap_txn, account.key)
    swap_txn_hash = optimism_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash

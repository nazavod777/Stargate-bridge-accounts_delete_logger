import time

from web3 import Account
from bridge.usdc_bridge import swap_usdc_fantom_to_polygon, swap_usdc_polygon_to_fantom, get_balance_usdc_fantom, get_balance_usdc_polygon


def main(tr):
    with open('keys.txt', 'r') as keys_file:
        accounts = [Account.from_key(line.replace("\n", "")) for line in keys_file.readlines()]
        for _ in range(0, tr):
            for account in accounts:

                try:
                    fantom_balance = get_balance_usdc_fantom(account.address)
                    polygon_balance = get_balance_usdc_polygon(account.address)

                    if fantom_balance + polygon_balance < 1 * (10 ** 6):
                        continue

                    if fantom_balance > polygon_balance:
                        print("Swapping USDC from Fantom to Polygon...")
                        fantom_to_polygon_txn_hash = swap_usdc_fantom_to_polygon(account=account, amount=fantom_balance)
                        print("Waiting for the swap to complete...")
                        time.sleep(20)
                        print(f"Transaction: https://ftmscan.com/tx/{fantom_to_polygon_txn_hash.hex()}")
                    else:
                        print("Swapping USDC from Polygon to Fantom...")
                        polygon_to_fantom_txn_hash = swap_usdc_polygon_to_fantom(account=account, amount=polygon_balance)
                        print("Waiting for the swap to complete...")
                        time.sleep(20)
                        print(f"Transaction: https://polygonscan.com/tx/{polygon_to_fantom_txn_hash.hex()}")

                    print("Sleeping 60 seconds for the next account")
                    time.sleep(60)
                except:
                    pass

            print("Sleeping 1200 seconds for the next cycle")
            time.sleep(1200)


if __name__ == '__main__':
    total_rounds = 10
    main(total_rounds)

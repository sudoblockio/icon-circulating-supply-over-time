import requests
import json
from datetime import datetime
import csv


def post_rpc(payload: dict):
    r = requests.post("https://api.icon.community/api/v3", data=json.dumps(payload))
    if r.status_code == 200:
        return r
    else:
        raise Exception(r)


def get_total_supply_block_height(height: int):
    payload = {
        "jsonrpc": "2.0",
        "id": 1234,
        "method": "icx_getTotalSupply",
        "params": {
            "height": hex(height)
        },
    }

    return post_rpc(payload).json()['result']


def get_burn_balance_block_height(height: int):
    payload = {
        "jsonrpc": "2.0",
        "id": 1234,
        "method": "icx_getBalance",
        "params": {
            "height": hex(height),
            "address": "hx1000000000000000000000000000000000000000"
        },
    }

    return post_rpc(payload).json()['result']


def get_block_from_timestamp(timestamp: int):
    r = requests.get(
        "https://tracker.icon.community" + f'/api/v1/blocks/timestamp/{str(timestamp)}')
    if r.status_code == 200:
        response = r.json()
        return response['number'] + 1
    else:
        raise Exception(r)


def get_total_supply_over_time(days_back: int):
    total_supplies = []
    current_timestamp = datetime.now().timestamp() * 1e6

    for i in range(0, days_back):
        timestamp = current_timestamp - i * 86400 * 1e6
        block_height = get_block_from_timestamp(int(timestamp))
        total_supply = int(get_total_supply_block_height(block_height), 16) / 1e18

        burn_balance = int(get_burn_balance_block_height(block_height), 16) / 1e18

        total_supplies.append(
            {
                "block_height": block_height,
                "total_supply": total_supply,
                "burn_balance": burn_balance, 
                "circulating_supply": total_supply - burn_balance, 
                "date": str(datetime.fromtimestamp(timestamp / 1e6))
            }
        )

    return total_supplies


def write_to_csv(time_series: list, file_name: str):
    keys = time_series[0].keys()

    with open(file_name, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(time_series)


if __name__ == '__main__':
    time_series = get_total_supply_over_time(180)
    write_to_csv(time_series, 'output.csv')

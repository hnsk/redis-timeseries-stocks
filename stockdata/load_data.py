#!/usr/bin/env python

import csv
import os
from datetime import datetime
from pathlib import Path
from timeit import default_timer as timer

import redis
from redis.commands.search.suggestion import Suggestion

REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = int(os.environ.get('REDIS_PORT') or '6379')

SYMBOLS_MAP_NYSE = os.environ.get('SYMBOLS_MAP') or 'nyse-listed_csv.csv'
SYMBOLS_MAP_NASDAQ = os.environ.get('SYMBOLS_MAP_NASDAQ') or 'nasdaqlisted.txt'

# Create synchronous connection pool for Redis
rpool = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def load_data(path: str, exchange: str):
    total_start = timer()
    num_files = len(list(Path(path).glob('*.csv')))
    count = 0
    for file in Path(path).glob('*.csv'):
        start = timer()
        with file.open() as csvfile:
            data = csv.DictReader(csvfile)
            pipe = rpool.pipeline()
            for row in data:
                eod = {}
                eod['symbol'] = row['Symbol']
                eod['timestamp'] = int(datetime.timestamp(datetime.strptime(row['Date'], "%d-%b-%Y"))) * 1000
                eod['open'] = float(row['Open'])
                eod['close'] = float(row['Close'])
                eod['low'] = float(row['Low'])
                eod['high'] = float(row['High'])
                eod['volume'] = int(row['Volume'])
                eod['exchange'] = exchange
                
                for value in [
                    'open',
                    'close',
                    'low',
                    'high',
                    'volume'
                ]:

                    pipe.ts().add(
                        key=f"rates:{exchange}:{eod['symbol']}:{value}",
                        timestamp=eod['timestamp'],
                        value=eod[value],
                        labels={
                            "symbol": eod['symbol'],
                            "exchange": exchange,
                            "type": value
                        }
                    )
            pipe.execute()
            count += 1
            print(f"Processed {count}/{num_files}: {file.name} {timer() - start:.2f}s (Total: {timer() - total_start:.2f}s)")

def main():
    load_data("./nyse", "nyse")
    load_data("./nasdaq", "nasdaq")

if __name__ == '__main__':
    main()

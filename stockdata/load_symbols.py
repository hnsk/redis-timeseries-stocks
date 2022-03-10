#!/usr/bin/env python

import csv
import os
from typing import List, Tuple

import redis
from redis.commands.search.field import TextField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType


REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = int(os.environ.get('REDIS_PORT') or '6379')

SYMBOLS_MAP_NYSE = os.environ.get('SYMBOLS_MAP') or 'nyse-listed_csv.csv'
SYMBOLS_MAP_NASDAQ = os.environ.get('SYMBOLS_MAP_NASDAQ') or 'nasdaqlisted.txt'

# FT.CREATE symbolsIdx ON JSON PREFIX 1 symbols: SCHEMA $.symbol AS symbol TAG $.company_name AS company_name TEXT NOSTEM $.exchange AS exchange TAG

LOG_SCHEMA = (
    TagField("$.symbol", as_name="symbol"),
    TagField("$.exchange", as_name="exchange"),
    TextField("$.company_name", as_name="company_name", no_stem=True)
)
LOG_IDX = "symbolsIdx"
LOG_PREFIX = ["symbols:"]

# Create synchronous connection pool for Redis
rpool = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def create_index(
    idx_schema: Tuple = LOG_SCHEMA,
    idx_prefix: List = LOG_PREFIX
    ):
    """ Create index if it doesn't exist. """
    ftclient = rpool.ft(index_name=LOG_IDX)

    definition = IndexDefinition(
        prefix=idx_prefix,
        index_type=IndexType.JSON
        )
    try:
        ftclient.info()
    except redis.exceptions.ResponseError:
        ftclient.create_index(idx_schema, definition=definition)

def load_symbols_nyse(symbols_map: str = SYMBOLS_MAP_NYSE):
    symbols_list = []
    with open(symbols_map, 'r') as symbols_csv:
        symbols = csv.DictReader(symbols_csv)
        for symbol in symbols:
            symbols_list.append({
                "symbol": symbol['ACT Symbol'],
                "company_name": symbol['Company Name'],
                "exchange": "nyse"
            })
    return symbols_list

def load_symbols_nasdaq(symbols_map: str = SYMBOLS_MAP_NASDAQ):
    symbols_list = []
    with open(symbols_map, 'r') as symbols_csv:
        symbols = csv.DictReader(symbols_csv, delimiter='|')
        for symbol in symbols:
            symbols_list.append({
                "symbol": symbol['Symbol'],
                "company_name": symbol['Security Name'],
                "exchange": "nasdaq"
            })
    return symbols_list

def save_symbols_to_redis(symbols_list: list, exchange: str):
    pipe = rpool.pipeline()
    for symbol in symbols_list:
        pipe.json().set(f"symbols:{exchange}:{symbol['symbol']}", "$", symbol)
    pipe.execute()

def main():
    create_index()
    symbols = load_symbols_nyse()
    save_symbols_to_redis(symbols, "nyse")
    symbols = load_symbols_nasdaq()
    save_symbols_to_redis(symbols, "nasdaq")

    

if __name__ == '__main__':
    main()

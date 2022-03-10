#!/usr/bin/env python

import json
from os import environ
from typing import Any, List, Union
from pydantic import BaseModel

import redis
from redis.commands.search.commands import Query

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

REDIS_HOST = environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = int(environ.get('REDIS_PORT') or 6379)

rpool = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def get_company_name(symbol: str, exchange: str):
    ftclient = rpool.ft(index_name="symbolsIdx")
    query = (
        Query(f"@symbol:{{{symbol}}} @exchange:{{{exchange}}}")
        .return_fields("company_name")
    )
    res = ftclient.search(query)
    return res.docs[0].company_name

def search_symbols(querystr: str, start: int = 0, limit: int = 100, sortby_field: str = "symbol", sort_asc: bool = False):
    ftclient = rpool.ft(index_name="symbolsIdx")
    query = (
        Query(querystr)
        .sort_by(sortby_field, asc=sort_asc)
        .paging(start, limit)
        .highlight()
        .return_fields(
            "symbol",
            "company_name",
            "exchange"
        )
    )
    res = ftclient.search(query)
    return res

def get_mrange(
        from_time: Union[int, str],
        to_time: Union[int, str],
        filters: List[str],
    ) -> List:
    """ Get TS.MRANGE """

    res = rpool.ts().mrange(
        from_time=from_time,
        to_time=to_time,
        filters=filters,
        with_labels=True,
    )

    result = []
    for series in res:
        for _, data in series.items():
            series = {
                'name': data[0]['type'],
                'exchange': data[0]['exchange'],
                'symbol': data[0]['symbol'],
                'company_name': get_company_name(
                    symbol=data[0]['symbol'],
                    exchange=data[0]['exchange']
                ),
                'data': []
            }
            for entry in data[1]:
                series['data'].append({
                    'x': entry[0],
                    'y': entry[1]
                })
            result.append(series)
    return result

### FastAPI

app = FastAPI()

class TimeSeriesMrangeQuery(BaseModel):
    """ TS.MRANGE query definition. """
    from_time: Any = "-"
    to_time: Any = "+"
    filters: List[str] = ["type!=volume"]

@app.post("/api/timeseries/mrange", response_class=JSONResponse)
def timeseries_mrange(query: TimeSeriesMrangeQuery):
    """ Get TS.MRANGE results. """
    result = get_mrange(
        from_time=query.from_time,
        to_time=query.to_time,
        filters=query.filters
    )

    return result

class SearchQuery(BaseModel):
    """ Search query definition. Accepted parameters are a query string. """
    query: str
    start: int = 0
    limit: int = 10
    sortby: str = "symbol"
    sort_asc: bool = False

@app.post("/api/search", response_class=JSONResponse)
def search_string(query: SearchQuery):
    """ Search string from logs and return results and information. """

    results = {}
    results['total'] = 0
    results['duration'] = 0
    results['results'] = []
    results['error'] = ""
    try:
        res = search_symbols(
            querystr=query.query,
            start=query.start,
            limit=query.limit,
            sortby_field=query.sortby,
            sort_asc=query.sort_asc)

        results['total'] = res.total
        results['duration'] += res.duration
        for doc in res.docs:
            results['results'].append({
                "id": doc.id,
                "symbol": doc.symbol,
                "company_name": doc.company_name,
                "exchange": doc.exchange
            })
    except redis.exceptions.ResponseError:
        print(f"invalid query {query.query}")
        results['error'] = f"Invalid query {query.query}"
    results['duration'] = f"{results['duration']:.2f}"
    results['numresults'] = len(results['results'])
    return JSONResponse(results)

def main():
    """Main. """
    res = get_mrange(
        from_time="-",
        to_time="+",
        filters=[
            #"type!=volume",
            "exchange=nasdaq",
            "symbol=AAPL"
        ]
    )
    print(json.dumps(res))

if __name__ == '__main__':
    main()
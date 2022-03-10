# redis-timeseries-stocks
Redis TimeSeries demo with Stock EOD data

## Running
Copy dump of the stock data to `./redis/data/dump.rdb`

```
docker-compose up
```

Alternatively change image to `redislabs/redismod:latest` for redis container in `docker-compose.yml`

Find CSV EOD data for Nasdaq/NYSE and put it to `./stockdata/nasdaq` and `./stockdata/nyse`.

Format for csv files:
```
Symbol,Date,Open,High,Low,Close,Volume
```

Then load the data (this will take quite some time):
```
cd stockdata
REDIS_HOST=127.0.0.1 python load_symbols.py
REDIS_HOST=127.0.0.1 python load_data.py
```

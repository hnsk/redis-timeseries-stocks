#!/bin/bash
docker create --name redismod -p 6379:6379 redislabs/redismod
docker cp redis/data/dump.rdb redismod:/data
docker start redismod


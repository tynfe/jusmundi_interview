#!/bin/bash

echo 'create topic'
docker exec -it kafka1 /usr/bin/kafka-topics --bootstrap-server kafka2:9092,kafka1:9093 --create --topic numberingestion --replication-factor 1 --partitions 12


echo 'stream number'
for x in {1..1000};
do
  id=$x
  value=$((1 + $RANDOM % 10))
  echo "$value";
  sleep .1;
done \
  | docker exec -i kafka1 \
      /usr/bin/kafka-console-producer \
      --bootstrap-server kafka1:9093,kafka2:9092 \
      --topic numberingestion

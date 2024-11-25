# Project
This project is an ELT pipeline designed to perform multiple actions:

Data Ingestion: Extract and load data from Kafka into an Iceberg table in the RAW schema, partitioned by hour.<br/>
Data Transformation: Transform the ingested data (numbers) from RAW and store it in the SILVER schema, partitioned by day.<br/>
The ingestion and transformation runners are independent, allowing the transformation pipeline to be restarted without impacting the Kafka ingestion process.

We leverage S3 for the data lake and Iceberg as the table format. Data is stored in Parquet files compressed with Snappy for optimal storage and performance.

The ELT pipeline is built using the following components:

Spark v3.5.3 for distributed data processing.
Trino v443 for querying data with scalability and simplicity.
Hive Metastore v3.3.1 for metadata management.
MariaDB v10.5.8 for managing the Hive Metastore.
Kafka v3.8.0 for real-time data ingestion.
For monitoring and observability, the stack includes:

Telegraf for collecting metrics.
Grafana for visualizing metrics.
Prometheus for storing and querying metrics.
StatsD for metric aggregation and alerting.
When the extraction runner is active, you can monitor the number of processed events in Grafana and set up alerts for thresholds to ensure smooth pipeline operation.

S3 was chosen for its cost-effective storage and scalability.
Iceberg is used as the table format for its support for schema evolution, time travel, and partitioning.
Trino allows us to easily query Iceberg tables and scale horizontally if required. Both RAW and SILVER schemas are available for querying in the database.

So when the runner extract is running we can monitor in grafana how much event were processed and set up alarms if the number
of events is reaching a threshold 

## Project Structure 
```
jusmundi_interview/
│── infra/                 # Pipeline infra 
├── src/
│   ├── commons/           # Contains common method used in both extract/transform module
│   ├── extract/           # Handle extract of data from kafka and load into Iceberg
│   └── transform/         # Handle transform logic 
│
├── tests/                 # Unit tests for the project
```

# Deployment 

To deploy you just need to run: <br/>
docker compose -f docker-compose.yml up -d <br/>
To monitor one of the specific service you can run: <br/>
docker logs -f <service> <br/>
To generate fake number in the topic you can run:
sh generate_number.sh 

# Endpoint

grafana => http://0.0.0.0:3000/login    admin password<br/>
trino => http://0.0.0.0:8090/           no user<br/>
spark => http://0.0.0.0:8080/           no user<br/>
kafka_manager => http://0.0.0.0:9000    no user <br/>
mariadb => jdbc:mysql://0.0.0.0:3306    user password <br/>


# Command 

- sh generate_number.sh

- docker exec -it kafka1 /usr/bin/kafka-console-consumer 
--bootstrap-server kafka1:9093,kafka2:9092 
--topic number_ingestion  
--from-beginning 

- docker exec -it commons /opt/spark/bin/spark-submit --conf spark.pyspark.python=/opt/spark/elt/deps/venv/bin/python3.12 --archives /opt/spark/elt/deps/my_env.tar.gz#environment --master spark://commons:7077 --packages org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.3.1,org.apache.hadoop:hadoop-aws:3.3.3,mysql:mysql-connector-java:8.0.13,org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.3,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 --executor-memory 3g --conf spark.hadoop.fs.s3a.access.key=$AWS_ACCESS_KEY_ID --conf spark.hadoop.fs.s3a.secret.key=$AWS_SECRET_ACCESS_KEY /opt/spark/elt/src/main.py --runner extract

- docker exec -it trino trino --server http://trino:8080 --catalog lakehouse --schema raw  --user tyron.ferreira 


# chat gpt 
I used it various time during this project but mostly when the infra was not working as it was supposed to. 
I also used it to create the test suite to be sure that my quick implem of number_to_french was working 
and I used multiple articles and tool I'm using every day to make this infra 

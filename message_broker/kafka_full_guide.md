
# 🦄 Apache Kafka Full Guide

## 🔧 What is Apache Kafka?
**Apache Kafka** is a **distributed event streaming platform** used for building **real-time data pipelines** and **streaming applications**. It is highly scalable, fault-tolerant, and designed for high-throughput, low-latency messaging.

Kafka is used by companies like LinkedIn, Netflix, Uber, and Airbnb for stream processing, log aggregation, real-time analytics, and event sourcing.

---

## 🧱 Core Concepts

| Concept        | Description |
|----------------|-------------|
| **Producer**   | Publishes messages to Kafka topics |
| **Consumer**   | Subscribes and reads messages from topics |
| **Topic**      | A category/feed name to which messages are published |
| **Partition**  | Topics are split into partitions for scalability |
| **Offset**     | Unique ID of a message within a partition |
| **Broker**     | Kafka server that stores and serves data |
| **Consumer Group** | Set of consumers sharing the same group ID for parallel consumption |
| **ZooKeeper**  | Manages Kafka cluster metadata (Kafka newer versions can run without it) |

---

## 📦 Kafka Architecture Overview

- **Producers** send messages to **topics**
- Topics are split into **partitions**
- **Consumers** read from partitions
- Kafka **brokers** manage partitions and message storage
- Kafka is designed to **persist messages** for a configurable period

---

## ✅ What You Can Do with Kafka

### 1. Event Streaming Between Microservices

**Example Use Case**: An order service emits an `order_created` event. Inventory and billing services consume the event and react accordingly.

```bash
Topic: orders
Event: {"order_id": 123, "status": "created", "user_id": 1}
```

- Order Service (Producer)
- Inventory Service (Consumer Group A)
- Billing Service (Consumer Group B)

---

### 2. Log Aggregation

Kafka can be used to collect logs from multiple services and store them in a central place for processing or monitoring.

```bash
Topic: logs_backend, logs_frontend
Each message: {"level": "INFO", "message": "User logged in", "timestamp": "..."}
```

---

### 3. Real-Time Analytics

**Example**: A food delivery platform wants to show current delivery statuses of all riders in real-time.

- Riders push location every 5 seconds to Kafka topic: `rider_location`
- Consumer reads from this topic and updates real-time map dashboard

---

### 4. Stream Processing (with Kafka Streams / ksqlDB)

Kafka supports processing streams of data in real-time.

**Example**: Count how many orders were placed in the last 10 minutes.

```sql
SELECT COUNT(*) FROM orders_windowed WINDOW TUMBLING (SIZE 10 MINUTES);
```

---

### 5. ETL Pipelines

Kafka can ingest data from different sources and pipe it into data lakes or warehouses (via Kafka Connect).

- Source: MySQL, MongoDB
- Sink: Hadoop, PostgreSQL, S3

---

### 6. User Activity Tracking

Web apps can push user activity data (clicks, page views) into Kafka for real-time recommendation engines or analytics.

```json
{ "user_id": 1, "event": "click", "page": "home", "timestamp": "..." }
```

---

### 7. Messaging System Alternative

Kafka can replace traditional brokers like RabbitMQ when you need message durability, scalability, and replayability.

---

## 🧑‍💻 Real-Time Example: Order Processing System

### Architecture:
- **Producer**: Order service emits `order_placed` events
- **Topic**: `orders`
- **Consumers**:
  - Inventory Service: checks stock
  - Billing Service: generates invoice
  - Notification Service: sends confirmation

```bash
Topic: orders
Message: {"order_id": 789, "user_id": 5, "status": "placed"}
```

Consumers are in different groups, so each one receives a copy of the event.

---

## ⚙️ Kafka Retention and Replay

Kafka **retains messages** for a specified time (e.g., 7 days), and consumers can **re-read** data from any offset. This makes Kafka great for:

- Reprocessing historical data
- Recovering from consumer failure
- Auditing and debugging

---

## 🛠️ Basic Kafka Commands

### Create Topic
```bash
kafka-topics.sh --create --topic my_topic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Produce Messages
```bash
kafka-console-producer.sh --topic my_topic --bootstrap-server localhost:9092
```

### Consume Messages
```bash
kafka-console-consumer.sh --topic my_topic --from-beginning --bootstrap-server localhost:9092
```

---

## 🐳 Kafka + Docker Example

```bash
docker-compose up -d
```

```yaml
# docker-compose.yml
version: '2'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
  kafka:
    image: confluentinc/cp-kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

---

## 🧠 Next Steps to Learn Kafka

1. Learn Kafka CLI tools
2. Use Kafka with Python (`confluent_kafka`, `kafka-python`)
3. Explore Kafka Streams or ksqlDB
4. Build projects:
   - Real-time dashboards
   - Stream processing with filtering and aggregation
   - Event-driven architecture for microservices
5. Try Kafka Connect for database-to-stream integration

---

## ❌ When Not to Use Kafka

- You need simple queues with no need for retention or scale → use Redis or RabbitMQ
- You want low-latency messaging under 1 ms → Kafka adds some overhead
- Your workload is light and doesn’t need streaming

---

## ✅ When to Use Kafka

- Real-time event streaming
- Stream processing at scale
- Event sourcing and audit logs
- Decoupled communication between microservices


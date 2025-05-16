
# 🐇 RabbitMQ Full Guide

## 🔧 What is RabbitMQ?
**RabbitMQ** is a **message broker** that enables applications, services, and systems to communicate with each other using **asynchronous messaging**.

It implements the **Advanced Message Queuing Protocol (AMQP)** and supports **message queues**, **publish/subscribe**, **routing**, **load balancing**, and more.

---

## 🧱 Core Concepts

| Concept          | Description |
|------------------|-------------|
| **Producer**     | Sends messages |
| **Queue**        | Stores messages |
| **Consumer**     | Receives messages |
| **Exchange**     | Routes messages to queues |
| **Binding**      | Links exchanges to queues |
| **Routing Key**  | Used to determine how messages are routed |
| **Channel**      | Virtual connection inside a connection |
| **Ack/Nack**     | Message acknowledgment and rejection |

---

## 📦 Types of Exchanges

| Exchange Type | Description | Use Case |
|---------------|-------------|----------|
| **Direct**    | Route by exact routing key | Task queue |
| **Fanout**    | Broadcast to all bound queues | Event broadcasting |
| **Topic**     | Route based on wildcard matching | Logging |
| **Headers**   | Route based on message headers | Complex routing |

---

## ✅ What You Can Do with RabbitMQ

### 1. Task Queue (Work Queue)

Producers send tasks; consumers (workers) process them asynchronously.

```python
# Python Producer Example (using pika)
import pika
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
channel.basic_publish(exchange='', routing_key='task_queue', body='Hello')
connection.close()
```

```python
# Python Consumer Example
def callback(ch, method, properties, body):
    print("Received", body)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()
```

---

### 2. Pub/Sub with Fanout Exchange

All queues bound to the exchange receive all messages.

```python
channel.exchange_declare(exchange='logs', exchange_type='fanout')
channel.basic_publish(exchange='logs', routing_key='', body='Broadcast Message')
```

---

### 3. Topic Routing

Routes based on patterns (`*.error`, `user.#`).

```bash
exchange = 'topic_logs'
routing_key = 'user.login'
channel.exchange_declare(exchange=exchange, exchange_type='topic')
channel.basic_publish(exchange=exchange, routing_key=routing_key, body='User login')
```

---

### 4. Delayed Messaging
Use plugins or dead-letter exchanges to implement delayed retries or scheduled messages.

---

### 5. Priority Queue

Define queue with `x-max-priority`, and set message priority.

---

### 6. Dead Letter Queue (DLQ)

Handles failed or expired messages separately for monitoring or reprocessing.

---

## 🧑‍💻 Real-Time Example: Email Sending System

**Architecture:**
- Producer pushes to `email_queue`
- Worker (Consumer) processes email sending
- Retry mechanism on failure

```python
# Producer
channel.basic_publish(exchange='', routing_key='email_queue', body=json.dumps({"to": "user@example.com"}))
```

```python
# Consumer with Retry
try:
    send_email(email)
    channel.basic_ack(delivery_tag=method.delivery_tag)
except Exception:
    # optionally requeue or send to DLQ
    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

---

## 🛡️ When to Use RabbitMQ
- Decoupled microservices
- Asynchronous task processing
- Retry mechanisms
- Message durability and acknowledgments

## ❌ When Not to Use RabbitMQ
- Real-time chat with low latency (use Redis or WebSocket)
- Lightweight in-memory queue (use Redis Lists/Streams)

---

## 🧠 Next Steps to Learn RabbitMQ

1. Install RabbitMQ via Docker or locally
2. Learn pika (Python), amqplib (Node), or Spring AMQP (Java)
3. Use the Management UI (`http://localhost:15672`)
4. Build projects:
   - Task queue
   - Retry system with DLQ
   - Event-driven microservices
5. Explore plugins (delayed messaging, metrics)

---

## 🐳 Docker Run Example
```bash
docker run -d --hostname my-rabbit --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

Access the UI at `http://localhost:15672` (default user/pass: guest/guest)


# 📘 Redis Full Guide

## 🔧 What is Redis?
**Redis (REmote DIctionary Server)** is an **in-memory data structure store**, often used as:
- **Database**
- **Cache**
- **Message broker**
- **Queue system**

Redis is **open-source**, **very fast**, and supports **persistence**.

---

## 🧱 Core Redis Data Structures

| Data Type     | Description                          | Example Use Case            |
|---------------|--------------------------------------|-----------------------------|
| **String**    | Simple key-value pair                | Caching user profiles       |
| **List**      | Ordered collection (linked list)     | Message queues              |
| **Set**       | Unordered unique collection          | Track unique visitors       |
| **Sorted Set**| Set with scores                      | Leaderboards                |
| **Hash**      | Key-value map within a key           | User object (name, age)     |
| **Bitmap**    | Bit-level data storage               | User online status          |
| **HyperLogLog**| Approximate cardinality             | Unique user counting        |
| **Streams**   | Log-like structure for real-time data| Event sourcing, chat system |

---

## ✅ What You Can Do with Redis

### 1. Caching
```python
redis.set("user:123", json.dumps(user_data), ex=3600)
```

### 2. Session Storage

### 3. Pub/Sub Messaging
```bash
SUBSCRIBE channel1
PUBLISH channel1 "Hello"
```

### 4. Queues

#### List-based Queue (FIFO)
```python
redis.lpush("task_queue", json.dumps({"user_id": 1, "action": "send_email"}))
task = redis.rpop("task_queue")
```

#### Redis Streams
Supports consumer groups, IDs, and ACKs.

---

### 5. Leaderboards with Sorted Sets
```bash
ZADD game_scores 100 "user1"
ZRANGE game_scores 0 -1 WITHSCORES
```

### 6. Rate Limiting
```python
key = f"rate:{user_id}"
if redis.incr(key) == 1:
    redis.expire(key, 60)
```

### 7. Real-Time Analytics

---

## 🧑‍💻 Real-Time Example: Email Sending Queue System

```python
# Producer
redis.lpush("email_queue", json.dumps({"to": "user@example.com", "body": "Welcome!"}))

# Worker
while True:
    task = redis.rpop("email_queue")
    if task:
        send_email(json.loads(task))
```

---

## ⚙️ Persistence and Durability
- RDB (Snapshot)
- AOF (Append-only file)

---

## 🛡️ When Not to Use Redis
- Need for strong consistency
- Large datasets beyond RAM
- Complex relational queries

---

## 🧠 Next Steps to Learn Redis

1. Use Redis CLI
2. Install Redis via Docker
3. Use Redis with Python
4. Build Projects
5. Explore Redis Modules


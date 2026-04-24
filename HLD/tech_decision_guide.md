# Technology Selection Guide: When to Use What
## Making Informed Architectural Decisions for HLD Interviews

---

## Message Queue Technologies

### RabbitMQ vs Redis vs Kafka

#### RabbitMQ
**Use When:**
- Complex routing requirements (exchanges, routing keys)
- Need guaranteed message delivery (AMQP protocol)
- Enterprise features required (clustering, management UI)
- Message priorities and TTL are important
- Team familiar with traditional message brokers

**Don't Use When:**
- Need extremely high throughput (>100K msgs/sec)
- Simple pub/sub is sufficient
- Team lacks RabbitMQ expertise
- Cost-sensitive (requires dedicated infrastructure)

**Real-World Scenarios:**
```
✅ E-commerce order processing with complex workflows
✅ Banking systems requiring guaranteed transactions
✅ Healthcare systems with regulatory compliance
❌ Real-time analytics (use Kafka)
❌ Simple notification systems (use Redis)
```

#### Redis Pub/Sub
**Use When:**
- Simple, fast pub/sub needed
- Already using Redis for caching
- Real-time notifications (chat, live updates)
- Low latency is critical (<1ms)
- Temporary/ephemeral messaging

**Don't Use When:**
- Need message persistence
- Guaranteed delivery required
- Complex routing patterns needed
- High availability critical (single point of failure)

**Real-World Scenarios:**
```
✅ Live chat applications
✅ Real-time gaming leaderboards
✅ Stock price updates
❌ Financial transaction processing
❌ Email queue systems
```

#### Apache Kafka
**Use When:**
- High throughput (*typically refers to a need for processing a large volume of data, requests, or transactions in a short period of time*) required (>100K msgs/sec)
- Event streaming and log aggregation
- Multiple consumers need same messages
- Message replay capability needed
- Building event-driven architecture

**Don't Use When:**
- Simple request-response patterns
- Low message volume (<1K msgs/sec)
- Complex routing required
- Team lacks Kafka expertise
- Quick prototyping needed

**Real-World Scenarios:**
```
✅ IoT sensor data collection
✅ User activity tracking
✅ Log aggregation systems
✅ Real-time analytics pipelines
❌ Simple job queues
❌ Email notifications
```

### Decision Matrix
| Requirement | RabbitMQ | Redis | Kafka |
|-------------|----------|-------|-------|
| Throughput | Medium | Low | Very High |
| Latency | Low | Very Low | Medium |
| Persistence | Yes | No | Yes |
| Complex Routing | Excellent | No | Limited |
| Learning Curve | Medium | Low | High |
| Operational Complexity | Medium | Low | High |

---

## Database Selection: SQL vs NoSQL

### When to Use SQL Databases

#### PostgreSQL
**Use When:**
- Complex queries and joins required
- ACID transactions essential
- Structured, relational data
- Strong consistency needed
- Rich ecosystem and tooling important

**Real-World Scenarios:**
```
✅ Financial systems (banking, payments)
✅ E-commerce platforms (orders, inventory)
✅ CRM systems
✅ Analytics with complex queries
```

#### MySQL
**Use When:**
- Web applications with moderate complexity
- Read-heavy workloads
- Team familiar with MySQL
- Cost-effective solution needed
- Proven at scale (Facebook, Twitter early days)

**Real-World Scenarios:**
```
✅ Content management systems
✅ Social media platforms (read-heavy)
✅ E-commerce websites
✅ Blog platforms
```

### When to Use NoSQL Databases

#### MongoDB (Document Store)
**Use When:**
- Flexible, evolving schema
- Rapid application development
- Document-based data model fits naturally
- Horizontal scaling needed
- JSON-like data structures

**Don't Use When:**
- Complex multi-document transactions
- Strong consistency critical
- Heavy relational queries
- Team lacks NoSQL experience

**Real-World Scenarios:**
```
✅ Content management systems
✅ Product catalogs
✅ User profiles and preferences
✅ IoT data collection
❌ Banking transactions
❌ Inventory management with complex relationships
```

#### Cassandra (Wide Column)
**Use When:**
- Massive write-heavy workloads
- Time-series data
- Global distribution needed
- High availability critical
- Linear scalability required

**Don't Use When:**
- Complex queries needed
- Small datasets (<1TB)
- Strong consistency required
- Limited operational expertise

**Real-World Scenarios:**
```
✅ IoT sensor data (Netflix, Uber)
✅ Time-series analytics
✅ Messaging systems (WhatsApp)
✅ Logging and monitoring
❌ E-commerce transactions
❌ User authentication systems
```

#### DynamoDB (Key-Value)
**Use When:**
- AWS ecosystem
- Predictable performance needed
- Serverless architecture
- Minimal operational overhead
- Pay-per-use model fits

**Don't Use When:**
- Complex queries required
- Cost predictability needed
- Multi-cloud strategy
- Heavy analytical workloads

**Real-World Scenarios:**
```
✅ Session storage
✅ Gaming leaderboards
✅ Mobile app backends
✅ IoT device management
❌ Reporting and analytics
❌ Complex business logic
```

#### Redis (In-Memory)
**Use When:**
- Sub-millisecond latency required
- Caching layer
- Session storage
- Real-time analytics
- Temporary data storage

**Don't Use When:**
- Primary data storage
- Large datasets (>RAM capacity)
- Complex queries needed
- Data durability critical

**Real-World Scenarios:**
```
✅ Application caching
✅ Session management
✅ Real-time leaderboards
✅ Rate limiting
❌ Primary user data storage
❌ Long-term data retention
```

### Database Decision Framework

#### Choose SQL When:
- **Data Relationships**: Complex relationships between entities
- **Consistency**: ACID transactions required
- **Query Complexity**: JOIN operations, aggregations, complex WHERE clauses
- **Mature Ecosystem**: Need for ORMs, tools, and expertise
- **Compliance**: Regulatory requirements for data integrity

#### Choose NoSQL When:
- **Scale**: Horizontal scaling requirements
- **Flexibility**: Schema changes frequent
- **Performance**: Specific performance characteristics (high writes, low latency)
- **Data Model**: Non-relational data fits better
- **Development Speed**: Rapid prototyping needed

---

## Caching Technologies

### Redis vs Memcached vs Application Cache

#### Redis
**Use When:**
- Data structures beyond key-value (lists, sets, hashes)
- Persistence required
- Pub/Sub messaging needed
- Lua scripting capabilities required
- Single-threaded consistency important

**Real-World Scenarios:**
```
✅ Session storage with complex data
✅ Real-time analytics
✅ Queuing systems
✅ Social media feeds
```

#### Memcached
**Use When:**
- Simple key-value caching
- Multi-threaded performance needed
- Memory efficiency critical
- Distributed caching across nodes
- LRU eviction is sufficient

**Real-World Scenarios:**
```
✅ Database query result caching
✅ Web page fragment caching
✅ API response caching
✅ Large-scale read-heavy applications
```

#### Application-Level Cache (In-Memory)
**Use When:**
- Single server deployment
- Extremely low latency required
- No network overhead acceptable
- Simple use cases
- Development/testing environments

---

## Load Balancer Selection

### NGINX vs HAProxy vs AWS ALB/NLB

#### NGINX
**Use When:**
- Web server + load balancer combo needed
- Static content serving required
- SSL termination needed
- Reverse proxy capabilities important
- Cost-effective solution required

**Configuration Example:**
```nginx
upstream backend {
    least_conn;
    server web1.example.com weight=3;
    server web2.example.com weight=1;
    server web3.example.com:8080 backup;
}

server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://backend;
        health_check;
    }
}
```

#### HAProxy
**Use When:**
- Pure load balancing needed
- Advanced health checks required
- Complex routing rules
- High connection rates
- Detailed statistics and monitoring important

**Real-World Scenarios:**
```
✅ High-traffic web applications
✅ API gateways
✅ Database connection pooling
✅ TCP load balancing
```

#### AWS Application Load Balancer (ALB)
**Use When:**
- AWS ecosystem
- HTTP/HTTPS traffic
- Container-based applications
- Path-based routing needed
- Managed solution preferred

#### AWS Network Load Balancer (NLB)
**Use When:**
- TCP/UDP traffic
- Ultra-high performance needed (millions of requests/sec)
- Static IP addresses required
- Extreme low latency critical

---

## Search Technologies

### Elasticsearch vs Solr vs Database Full-Text Search

#### Elasticsearch
**Use When:**
- Real-time search and analytics
- Log aggregation (ELK stack)
- Complex search queries
- Distributed search needed
- RESTful API preferred

**Real-World Scenarios:**
```
✅ E-commerce product search
✅ Log analysis and monitoring
✅ Content discovery platforms
✅ Business intelligence dashboards
```

#### Apache Solr
**Use When:**
- Enterprise search requirements
- Document management systems
- Traditional, mature search needs
- XML configuration acceptable
- JVM-based stack

#### Database Full-Text Search
**Use When:**
- Simple search requirements
- Small datasets (<1M records)
- Existing database expertise
- Minimal additional infrastructure
- Cost constraints

---

## Storage Solutions

### File Storage vs Object Storage vs Block Storage

#### File Storage (NFS, EFS)
**Use When:**
- Shared file access needed
- POSIX compliance required
- Legacy application compatibility
- Content management systems

#### Object Storage (S3, GCS)
**Use When:**
- Static web content
- Backup and archival
- Content distribution
- Unlimited scalability needed
- RESTful API access preferred

#### Block Storage (EBS, Persistent Disks)
**Use When:**
- Database storage
- File systems
- High IOPS required
- Low latency critical

---

## API Technologies

### REST vs GraphQL vs gRPC

#### REST APIs
**Use When:**
- Simple, stateless operations (*Stateless operations are operations that do not rely on or modify any stored state or context from previous operations. Each request is independent and self-contained, meaning it carries all the information needed to complete the task.*)
- Wide client compatibility needed
- Caching important
- Standard HTTP methods sufficient
- Team familiar with REST

**Real-World Scenarios:**
```
✅ Public APIs
✅ CRUD operations
✅ Mobile app backends
✅ Microservices communication
```

#### GraphQL
**Use When:**
- Frontend needs flexible data fetching
- Multiple clients with different data needs
- Over-fetching/under-fetching problems exist
- Real-time subscriptions needed
- Rapid frontend development required

**Real-World Scenarios:**
```
✅ Social media platforms
✅ E-commerce product catalogs
✅ Content management systems
✅ Mobile apps with limited bandwidth
```

#### gRPC
**Use When:**
- High-performance communication needed
- Type safety important
- Bi-directional streaming required
- Microservices internal communication
- Language-agnostic RPC needed

**Real-World Scenarios:**
```
✅ Microservices communication
✅ Real-time gaming
✅ IoT device communication
✅ High-frequency trading systems
```

---

## Decision-Making Framework

### Key Questions to Ask:

#### Performance Requirements
- **Latency**: How fast must responses be?
- **Throughput**: How many requests per second?
- **Scalability**: Linear scaling needed?

#### Consistency Requirements
- **ACID**: Are transactions critical?
- **Eventual Consistency**: Acceptable delay in consistency?
- **CAP Theorem**: Consistency vs Availability vs Partition Tolerance?

#### Operational Considerations
- **Team Expertise**: What does the team know?
- **Maintenance**: Who will operate this system?
- **Cost**: Budget constraints and TCO?
- **Vendor Lock-in**: Multi-cloud strategy important?

#### Data Characteristics
- **Volume**: How much data?
- **Velocity**: How fast is data changing?
- **Variety**: Structured vs unstructured?
- **Access Patterns**: Read-heavy vs write-heavy?

### Technology Selection Process

1. **Define Requirements Clearly**
   - Performance (latency, throughput)
   - Consistency needs
   - Scalability requirements
   - Operational constraints

2. **Identify Constraints**
   - Budget limitations
   - Team expertise
   - Timeline pressures
   - Compliance requirements

3. **Evaluate Options**
   - Create comparison matrix
   - Consider trade-offs
   - Prototype if uncertain
   - Seek expert opinions

4. **Make Decision**
   - Document reasoning
   - Plan migration strategy
   - Monitor and measure
   - Be ready to evolve

---

## Latest Real-World Decision-Making Scenarios (2024-2025)

### 1. TikTok's Recommendation Engine
**Challenge**: Serve personalized video recommendations to 1B+ users with <100ms latency

**Technology Decisions:**
```
Primary Database: HBase (distributed, handles massive write volume)
Real-time Processing: Apache Flink (stream processing for user interactions)
Feature Store: Redis Cluster (user embeddings, video features)
ML Serving: TensorFlow Serving (model inference)
Message Queue: Kafka (user interaction events)
CDN: ByteDance's own CDN + Cloudflare (video delivery)
```

**Why These Choices:**
- **HBase over PostgreSQL**: Need to store billions of user-video interaction records
- **Flink over Spark**: Real-time processing for immediate recommendation updates
- **Redis Cluster over single Redis**: Distributed caching for global user base
- **Custom CDN**: Video delivery optimization with edge computing

### 2. Spotify's Real-Time Music Streaming
**Challenge**: Stream music to 500M+ users with personalized playlists and social features

**Technology Decisions:**
```
User Data: PostgreSQL (user profiles, subscriptions)
Music Metadata: Cassandra (song info, artist data)
Streaming: Google Cloud Storage + Custom CDN
Real-time Features: Apache Kafka + Apache Storm
Recommendations: Apache Airflow + Spark (batch processing)
Social Features: Redis (friend activity, real-time updates)
Search: Elasticsearch (music discovery)
```

**Decision Rationale:**
- **Cassandra for Music Metadata**: Write-heavy workload (new songs daily), global distribution
- **PostgreSQL for Users**: ACID transactions for billing, complex user relationships
- **Kafka + Storm**: Real-time processing of listening events for social features
- **Separate CDN**: Audio streaming optimization different from video

### 3. Discord's Voice Chat System
**Challenge**: Support millions of concurrent voice connections with <50ms latency

**Technology Decisions:**
```
Voice Infrastructure: Rust-based voice servers (custom)
Message Storage: ScyllaDB (Cassandra-compatible, faster)
Real-time Messaging: Elixir/Phoenix (actor model)
User Data: PostgreSQL (guilds, permissions)
Media Storage: Google Cloud Storage
CDN: Cloudflare (text/image content)
Load Balancing: Custom UDP load balancer
```

**Why These Specific Choices:**
- **Rust for Voice**: Memory safety + performance for real-time audio processing
- **ScyllaDB over Cassandra**: 10x better performance for message history
- **Elixir/Phoenix over Node.js**: Better handling of millions of concurrent connections
- **Custom UDP Load Balancer**: Standard HTTP load balancers don't handle voice traffic well

### 4. Zoom's Video Conferencing Platform
**Challenge**: Scale from 10M to 300M+ daily users during COVID-19 pandemic

**Technology Decisions:**
```
Video Processing: C++ custom codecs
Signaling: WebSocket + custom protocol
Media Routing: Custom media servers (geographically distributed)
User Management: Oracle Database (enterprise features)
Meeting Storage: AWS S3 + custom encryption
Load Balancing: F5 hardware + software load balancers
CDN: Multi-CDN strategy (Akamai, CloudFlare, AWS)
```

**Critical Decisions:**
- **Oracle over PostgreSQL**: Enterprise security features, established vendor relationship
- **Custom Media Servers**: Standard solutions couldn't handle the scale and quality requirements
- **Multi-CDN Strategy**: No single CDN could handle the traffic spike
- **Hardware + Software Load Balancing**: Redundancy for mission-critical infrastructure

### 5. DoorDash's Delivery Optimization
**Challenge**: Real-time matching of orders, drivers, and restaurants with dynamic pricing

**Technology Decisions:**
```
Order Management: PostgreSQL (ACID for money transactions)
Real-time Tracking: Redis Streams + WebSocket
Geospatial Data: PostGIS (location-based queries)
ML Pipeline: Apache Airflow + Spark (ETL + model training)
Event Streaming: Kafka (order lifecycle events)
Search: Elasticsearch (restaurant discovery)
Pricing Engine: Custom Go services + Redis
Time Series: InfluxDB (delivery metrics, driver performance)
```

**Key Decision Factors:**
- **PostGIS over MongoDB**: Complex geospatial queries for delivery optimization
- **Redis Streams over traditional queues**: Ordered event processing for driver tracking
- **InfluxDB for Metrics**: Specialized for time-series data (delivery times, driver ratings)
- **Go for Pricing**: Low latency requirements for dynamic pricing calculations

### 6. Tesla's Autopilot Data Pipeline
**Challenge**: Process petabytes of driving data from millions of vehicles for ML training

**Technology Decisions:**
```
Data Ingestion: Apache Kafka (vehicle telemetry)
Storage: HDFS + Parquet format (columnar storage)
Processing: Apache Spark (distributed computing)
ML Training: NVIDIA DGX clusters + PyTorch
Feature Store: Apache Iceberg (data lakehouse)
Real-time Inference: Edge computing in vehicles
Monitoring: Prometheus + Grafana
```

**Why These Choices:**
- **Parquet over JSON**: 10x storage savings for numerical data
- **Apache Iceberg**: ACID transactions on data lakes, schema evolution
- **Edge Computing**: Can't rely on internet for real-time driving decisions
- **NVIDIA DGX**: Specialized hardware for deep learning training

### 7. Netflix's Content Recommendation at Scale
**Challenge**: Personalize content for 230M+ subscribers across different regions and devices

**Technology Decisions:**
```
User Profiles: Cassandra (global distribution)
Viewing History: Apache Kafka + Apache Samza
Recommendations: Apache Spark + TensorFlow
A/B Testing: Custom platform built on Spark
Content Metadata: MySQL (structured data)
Caching: EVCache (custom Redis fork)
CDN: AWS CloudFront + Open Connect (custom CDN)
```

**Specific Netflix Innovations:**
- **EVCache over Redis**: Netflix's custom distributed cache with better consistency
- **Apache Samza over Storm**: Better integration with Kafka, exactly-once processing
- **Open Connect**: Custom CDN infrastructure inside ISP networks
- **Custom A/B Platform**: Standard tools couldn't handle Netflix's experimentation scale

### 8. Uber's Real-Time Trip Matching
**Challenge**: Match riders with drivers in <3 seconds globally with dynamic pricing

**Technology Decisions:**
```
Trip Data: PostgreSQL (transactions) + Cassandra (trip history)
Real-time Matching: Custom Go services + Redis
Geospatial: Redis with Geospatial commands
Event Streaming: Apache Kafka
Map Data: Custom mapping service + PostgreSQL/PostGIS
Pricing: Real-time ML models on Kubernetes
Notifications: Apple Push + Firebase (FCM)
Analytics: Apache Pinot (real-time OLAP)
```

**Uber's Specific Choices:**
- **Apache Pinot over traditional OLAP**: Real-time analytics for surge pricing
- **Custom Go Services**: Microsecond latency requirements for matching algorithm
- **Redis Geospatial**: Built-in geospatial commands for proximity searches
- **Custom Mapping**: Google Maps API too expensive at Uber's scale

### 9. WhatsApp's Message Delivery System
**Challenge**: Deliver 100B+ messages daily with end-to-end encryption

**Technology Decisions:**
```
Message Routing: Erlang/OTP (fault-tolerant, concurrent)
Message Storage: None (messages not stored on servers)
User Data: FreeBSD + custom storage
Media Storage: Facebook's infrastructure
Load Balancing: Software load balancers
Push Notifications: Custom XMPP-based protocol
Database: Minimal - mostly in-memory structures
```

**WhatsApp's Unique Approach:**
- **Erlang/OTP**: Designed for telecom systems, perfect for messaging
- **No Message Storage**: Privacy-first approach, reduces infrastructure needs
- **Custom XMPP**: Standard protocols modified for mobile optimization
- **Minimal Database**: Everything designed for real-time processing

### 10. GitHub's Code Search and Repository Hosting
**Challenge**: Search through millions of repositories with code-aware search

**Technology Decisions:**
```
Git Storage: Custom Git servers + distributed file systems
Code Search: Elasticsearch + custom indexing
Database: MySQL (user data) + Redis (sessions)
CI/CD: Custom runners on Kubernetes
Package Registry: Different storage per language (npm, Docker, etc.)
Search: GitHub Search (custom Elasticsearch implementation)
CDN: Fastly (for static assets and releases)
```

**GitHub-Specific Decisions:**
- **Custom Git Servers**: Standard Git doesn't scale to GitHub's repository count
- **Language-Specific Storage**: Different optimization strategies per package type
- **Fastly over AWS CloudFront**: Better for developer-focused content delivery
- **Custom Elasticsearch**: Code-aware indexing and ranking algorithms

### 11. Robinhood's Trading Platform
**Challenge**: Execute millions of stock trades with microsecond latency and regulatory compliance

**Technology Decisions:**
```
Order Management: PostgreSQL (ACID critical for money)
Real-time Prices: Redis + WebSocket streams
Market Data: Apache Kafka + Apache Flink
Risk Management: Custom C++ services
Compliance: Immutable audit logs in PostgreSQL
Mobile API: Django REST + PostgreSQL
Cache: Redis (portfolio data, market data)
Analytics: Apache Airflow + Redshift
```

**Financial Services Specific Choices:**
- **PostgreSQL for Everything**: ACID transactions non-negotiable in finance
- **C++ for Risk Systems**: Microsecond latency requirements
- **Immutable Audit Logs**: Regulatory compliance requirements
- **Django**: Rapid development for fintech features

### 12. Shopify's E-commerce Platform
**Challenge**: Handle Black Friday/Cyber Monday traffic spikes (10x normal load)

**Technology Decisions:**
```
Core Platform: Ruby on Rails + MySQL
Product Search: Elasticsearch
Image Processing: ImageMagick + custom CDN
Payment Processing: Custom payment orchestration
Inventory: Redis (real-time stock levels)
Analytics: Apache Kafka + BigQuery
Caching: Memcached + Redis
Autoscaling: Kubernetes + custom metrics
```

**E-commerce Specific Decisions:**
- **MySQL over NoSQL**: Complex e-commerce relationships (orders, products, variants)
- **Custom Payment Orchestration**: Multiple payment providers, complex routing
- **Redis for Inventory**: Real-time stock updates during high-traffic events
- **Custom Scaling Metrics**: Standard CPU/memory metrics insufficient for e-commerce

---

## Industry-Specific Technology Patterns

### FinTech (Stripe, Square, PayPal)
**Common Patterns:**
- **Database**: Always PostgreSQL (ACID transactions)
- **Message Queues**: RabbitMQ (guaranteed delivery)
- **Caching**: Conservative (Redis with persistence)
- **Monitoring**: Extensive (every transaction logged)
- **Security**: Multiple layers (encryption, HSMs, compliance)

### Gaming (Epic Games, Riot, Blizzard)
**Common Patterns:**
- **Real-time**: Custom UDP protocols + C++
- **Player Data**: NoSQL (MongoDB, DynamoDB)
- **Matchmaking**: Redis + custom algorithms
- **Analytics**: Kafka + real-time processing
- **CDN**: Specialized gaming CDNs (AWS GameLift)

### Social Media (Meta, Twitter, LinkedIn)
**Common Patterns:**
- **Timeline Generation**: Kafka + stream processing
- **Graph Data**: Custom graph databases or specialized solutions
- **Image/Video**: Object storage + specialized CDNs
- **Real-time Features**: WebSocket + Redis Pub/Sub
- **Recommendations**: Spark + TensorFlow/PyTorch

### Enterprise SaaS (Salesforce, ServiceNow, Atlassian)
**Common Patterns:**
- **Multi-tenancy**: PostgreSQL with tenant isolation
- **Integration**: REST APIs + webhook systems
- **Workflow**: Custom workflow engines
- **Search**: Elasticsearch with tenant-aware indexing
- **Compliance**: Extensive audit logging

---

## Technology Selection Anti-Patterns to Avoid

### 1. Resume-Driven Development
```
❌ "Let's use Kubernetes because it's trendy"
✅ "Let's use Kubernetes because we need container orchestration at scale"
```

### 2. Premature Optimization
```
❌ "We need Cassandra for eventual scale"
✅ "PostgreSQL fits our current needs; we'll evaluate Cassandra at 1M users"
```

### 3. Technology Maximalism
```
❌ Using 15 different technologies for a simple app
✅ Start simple, add complexity when justified by requirements
```

### 4. Ignoring Team Expertise
```
❌ "Erlang is perfect for this, even though our team only knows Java"
✅ "Java with async frameworks can meet our needs with current team skills"
```

### 5. Vendor Lock-in Blindness
```
❌ "AWS has everything we need"
✅ "AWS fits now, but we'll design for portability where practical"
```

---

## Interview Tips: How to Present Technology Decisions

### 1. Requirements First
```
Interviewer: "How would you build Instagram?"
Good Response: 
- "Let me clarify the requirements first..."
- "What's our expected user base?"
- "What's our read/write ratio?"
- "What are our latency requirements?"
```

### 2. Show Trade-off Thinking
```
"I'm choosing PostgreSQL over MongoDB because:
✅ Complex relationships between users, posts, and comments
✅ ACID transactions for user data integrity
✅ Rich query capabilities for analytics
❌ Trade-off: Harder to scale horizontally initially
❌ Trade-off: Less flexible schema evolution"
```

### 3. Mention Real Examples
```
"Similar to how Instagram uses PostgreSQL for user data and 
Cassandra for photo metadata, we can use a polyglot approach..."
```

### 4. Plan for Evolution
```
"We'll start with PostgreSQL, but as we grow beyond 10M users,
we'll evaluate sharding strategies or migration to distributed databases..."
```

Remember: The best technology choice is the one that fits your specific requirements, team capabilities, and constraints. Always justify your decisions with concrete reasoning, not just popularity or personal preference.
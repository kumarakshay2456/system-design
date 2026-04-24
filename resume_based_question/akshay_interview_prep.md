# Akshay Kumar — FAANG-Level Backend Interview Prep

> **Format**: Each section follows real interview flow.
> Interviewer reads your resume → asks a broad question → you answer → interviewer probes your answer with cross-questions.
> Questions are based only on what's on your resume. Answers draw from your actual implementation.

---

## TABLE OF CONTENTS

1. [Excel Data Processing Pipeline](#1-excel-data-processing-pipeline)
2. [OTP Notification System — SQS + RabbitMQ](#2-otp-notification-system--sqs--rabbitmq)
3. [Staffing Campaign Service](#3-staffing-campaign-service)
4. [Infrastructure Optimization](#4-infrastructure-optimization)
5. [Exotel Integration — Calling System](#5-exotel-integration--calling-system)
6. [Authorization + Microservice Architecture](#6-authorization--microservice-architecture)
7. [Bank Account Verification + Payout](#7-bank-account-verification--payout)
8. [CashMila — Independent Product](#8-cashmila--independent-product)
9. [System Design Deep Dives](#9-system-design-deep-dives)
10. [Behavioral + Ownership Questions](#10-behavioral--ownership-questions)
11. [Rapid-Fire Round](#11-rapid-fire-round)
12. [Weak Point Detection](#12-weak-point-detection)

---

## 1. EXCEL DATA PROCESSING PIPELINE

**Resume line**: *"Developed Excel-based data processing pipelines for upload and download workflows, ensuring data integrity and validation."*

---

### Interview Question 1

**Interviewer**: "Tell me about the Excel processing pipeline you built. What problem were you solving and how did you design it?"

**Your Answer**:
The problem was bulk employee data management — HR teams needed to onboard, update, terminate, or reonboard hundreds of employees at once, and doing it one-by-one through the UI wasn't scalable. We also needed the reverse — exporting employee data in a formatted Excel report.

I built a standalone microservice (FastAPI + Celery) that handles this asynchronously. The flow for upload:
1. HR uploads an Excel file → API validates basic structure and queues a background job
2. A Celery worker picks it up, reads the file row by row, validates each row against a schema, and calls the Employee Management API for each valid record
3. Results — including row-level errors — are stored and accessible for the user to download an error report

For download, the reverse: user requests a report with filters, Celery fetches employee records in batches from the Employee API, writes them to Excel using openpyxl, uploads to S3, and notifies the user the file is ready.

I separated this into its own service because processing large Excel files is CPU and I/O heavy — embedding it in the main API would have degraded latency for real-time requests.

**Cross-Questions**:

1. "Why a separate service for this? Couldn't you just add a Celery worker to your existing Django service?"
   > *Probe*: You need to explain bounded context, resource isolation, and independent scaling. The main staffing API handles real-time HR requests — a 30-minute bulk job running on the same workers would starve those. Separate queues, separate pods, separate scaling rules.

2. "You said you validate each row against a schema. What does that schema look like and where does it live?"
   > *Probe*: Schema is stored in MongoDB as a template document — defines field names, types, required/optional, validation rules. Templates are versioned and org-specific. This is a product design question: who defines the schema, how does it evolve, how do you handle old Excel files after a schema change?

3. "What happens if the processing fails halfway — say, at row 5,000 out of 10,000?"
   > *Probe*: This is the idempotency and crash recovery question. With `acks_late=True` in Celery, if the worker crashes, the task is re-queued and starts over. That means rows 1–5,000 are processed twice. An interviewer wants to hear about checkpoint patterns, idempotency on the Employee API (unique constraint on employee ID + org), and how you surface partial completion to the user.

4. "How does the user know when their upload is done? Do they poll or do you push?"
   > *Probe*: This is the real-time progress question. Answer: WebSocket connection from the browser, with the backend publishing progress updates to a Redis Stream keyed by `org_id`. The WebSocket handler reads from the stream and pushes to the client. Interviewer will then ask: what happens if the WebSocket drops mid-upload? How does the client recover its progress on reconnect? (Answer: XREAD from the last ID the client saw — Redis Streams support replay.)

5. "You mentioned row-level error reporting. How does a user with 200 errors out of 10,000 rows understand what went wrong?"
   > *Probe*: Generate an error report Excel file where each row has the original data + an error message column. Store this in S3, give the user a download link. Interviewer wants to know: is the error file generated inline (blocks the worker) or separately? How do you handle errors that span multiple rows (e.g., duplicate employee IDs in the same upload)?

---

### Interview Question 2

**Interviewer**: "You mentioned data integrity and validation. What does that actually mean in this context — give me a concrete example of a validation that failed in production."

**Your Answer**:
One common failure was schema mismatch — a template expected a date in `YYYY-MM-DD` format but the Excel cell had `DD/MM/YYYY` because that's the default Excel formatting in Indian locale. The validator would reject these rows with a type error, and the error report would show the raw cell value and the expected format.

A more interesting production issue was encoding: Excel files from certain HR tools used Windows-1252 encoding instead of UTF-8. Employee names with regional characters (like names in Kannada or Tamil transliterated) would come through corrupted. We added encoding detection using `chardet` and a fallback normalization step.

**Cross-Questions**:

1. "You mentioned schema validation before processing. How do you handle a file where 9,999 rows are valid and row 10,000 has an encoding error? Do you fail the whole upload?"
   > *Probe*: Design choice: fail-fast (reject entire file) vs. partial processing (process valid rows, report errors). Your dry-run mode is the answer here — user can see all errors before committing. After dry-run passes, the actual run should only encounter errors from race conditions or API-level rejections, not schema errors.

2. "You mentioned a dry-run mode. How do you ensure dry-run results are trustworthy — that if dry-run passes, the actual run will also pass?"
   > *Probe*: The dangerous gap: client-side schema validation won't catch server-side business logic rejections (e.g., "employee ID already exists in another org"). Dry-run tests what you can test locally. For the rest, idempotent APIs and good error surfacing are the defense. Interviewer is testing whether you know the limits of your own system.

3. "What's the largest file size you support and why? What breaks if someone uploads a 500MB Excel file?"
   > *Probe*: Memory — openpyxl loads the entire file into memory by default. For large files, use `read_only=True` mode which streams rows. Also: upload size limits at the API gateway/nginx level, multipart upload to S3 first then process from S3 (so you're not buffering the file in the web server's memory).

---

## 2. OTP NOTIFICATION SYSTEM — SQS + RABBITMQ

**Resume line**: *"Built high-throughput OTP notification system using SQS and RabbitMQ with failure handling mechanisms."*

---

### Interview Question 1

**Interviewer**: "Walk me through how you designed this system. What were the requirements and what choices did you make?"

**Your Answer**:
The requirements were: deliver OTPs via SMS reliably, with low latency (user is waiting), handle vendor outages gracefully, and not lose messages if something crashes mid-processing.

The system is a Go-based notification gateway. Clients publish a `NotificationTask` (protobuf) to an SQS queue. A Go consumer picks up messages, inserts a task record into PostgreSQL, then passes it to what we call a Priority Engine which handles actual delivery.

For OTP specifically: there's a dedicated OTP consumer that validates the OTP expiry timestamp before even attempting delivery. If the OTP has already expired by the time we dequeue it (could happen during traffic spikes), we move it to a dead-letter queue rather than sending a stale OTP. That's a security requirement as much as a functional one.

For failure handling: if the SMS vendor (Gupshup) fails, the message goes to a RabbitMQ delayed queue with a backoff window. RabbitMQ handles the retry scheduling — we use the delayed message plugin to fire retries at 30 seconds, 5 minutes, 30 minutes. After max retries, the task is marked failed and an alert fires.

**Cross-Questions**:

1. "Why SQS *and* RabbitMQ? Why not just SQS with a Dead Letter Queue for retries?"
   > *Probe*: This is the core architecture question. SQS DLQ is for messages that failed permanently — it's not a retry queue with configurable delay. SQS has a max message delay of 15 minutes. If you need retry at 30 minutes or 2 hours (for transient vendor outages), you need something else. RabbitMQ with the delayed message plugin gives you per-message TTL and sophisticated routing — different failure types route to different queues with different retry windows. Firebase throttling has a different retry strategy than a generic network error.

2. "You said you validate OTP expiry before sending. What's the TTL on an OTP in your system?"
   > *Probe*: Typically 5–10 minutes. The TTL is part of the proto message itself (Unix timestamp). The consumer compares current time against the expiry field. This is interesting because the expiry is set by the producer (Staffing API) at publish time, not by the notification hub. If the message sits in SQS for 10 minutes because of a traffic spike, it's expired by the time the consumer sees it. That's the correct behavior — you don't want users receiving an "expired" OTP and being confused.

3. "What happens if Gupshup delivers the SMS successfully but your acknowledgment back to the queue fails? Could you send the OTP twice?"
   > *Probe*: Yes, this is the dual-write problem. The sequence is: receive SQS message → insert into DB → call Gupshup → update DB → delete SQS message. If the process crashes between "Gupshup called" and "SQS deleted", the message is redelivered and Gupshup gets called again. The defense: idempotency key sent to Gupshup (if they support it). If not, the OTP is sent twice — which is annoying but not catastrophic since OTPs are single-use.

4. "You mentioned this is high-throughput. What does high-throughput mean in your case — what's the peak load?"
   > *Probe*: Be specific with numbers — even rough ones. "We see X OTPs/minute during peak login hours, Y during batch operations." Then reason about whether SQS → Go consumers → Gupshup can sustain that rate. The bottleneck is usually the SMS vendor (rate limits per second), not your own infrastructure.

5. "How do you monitor OTP delivery success rate? What do you alert on?"
   > *Probe*: New Relic custom events per delivery channel. Alert on: delivery success rate below 95%, OTP consumer queue depth above threshold (means consumers can't keep up), consecutive Gupshup failures (circuit breaker logic). Also: end-to-end latency alert — OTP should deliver within 10 seconds of being published.

---

### Interview Question 2

**Interviewer**: "You said 'failure handling mechanisms.' Beyond retries, what else did you implement?"

**Your Answer**:
Several layers:

**Rate limiting at the consumer level**: If downstream vendors start throttling us, the consumer detects this and backs off — stops consuming new messages for a period rather than hammering a degraded vendor. This prevents thundering herd when a vendor recovers.

**Separate consumers per message type**: OTP consumer, marketing consumer, and transactional consumer are separate processes. A flood of marketing messages won't delay OTP delivery — they have independent queue depths and scaling.

**Delivery reports**: Vendors like SendGrid and Firebase send webhooks when a message is actually delivered (or bounced, or opened). A separate delivery report consumer ingests these and updates the status in our database. This gives accurate delivery tracking rather than just "we attempted to send."

**Waterfall delivery**: For transactional notifications (not OTP), if email fails we fall back to SMS, then to push. Each channel has a configurable offset so we give the first channel time to succeed before trying the next. OTPs skip the waterfall — we go straight to SMS.

**Cross-Questions**:

1. "Consumer-level rate limiting — how does your consumer know that the vendor is throttling vs. just a transient error?"
   > *Probe*: HTTP 429 from the vendor is the signal. Or a series of consecutive 5xx responses. The rate limiter tracks this and sets a cool-down window. The challenge: you're blocking the consumer thread during cool-down, so messages pile up in SQS. That's fine — SQS is the buffer. The interviewer might ask: what if cool-down is 10 minutes and SQS message visibility timeout is 30 seconds? You'd be re-delivering the same messages to other consumers who are also rate-limited.

2. "Waterfall with time offsets — if Email fails instantly and SMS is the fallback, do you still wait the full offset time before trying SMS?"
   > *Probe*: Design flaw worth acknowledging. If email fails fast (connection refused, not a timeout), you shouldn't wait the full 5-minute offset. The offset is meant to give email a chance to succeed, not to delay SMS when email is clearly broken. Better design: start the offset timer when you *send* email, not when email *fails*.

3. "You have separate consumers for different message types. How do you handle priority within a message type? All transactional messages are equal — but some are urgent."
   > *Probe*: Honest answer: in the current design, within a type it's FIFO (SQS ordering). True priority queuing at the message level would require SQS FIFO queues with message group IDs, or Kafka with priority topic partitions. Acknowledging this limitation shows maturity.

---

## 3. STAFFING CAMPAIGN SERVICE

**Resume line**: *"Designed and developed the Staffing Campaign Service, streamlining manual campaign execution and significantly improving operational efficiency."*

---

### Interview Question 1

**Interviewer**: "What was the manual process before this service existed, and what did you build to replace it?"

**Your Answer**:
Before the service: HR managers were manually creating announcements — important company updates, policy changes, joining instructions — by sending WhatsApp broadcasts or emails directly. Two problems: (1) no tracking of who read or acknowledged the announcement, and (2) it wasn't integrated with the employee system, so they were manually managing lists.

I built a gRPC-based microservice with three core operations: create an announcement (with rich content + targeting), distribute it to employees of an organization, and track per-employee acknowledgment. HR can see in real-time what % of employees have acknowledged a critical policy announcement.

I chose gRPC over REST because the service is consumed exclusively by other backend services (not a browser), binary protobuf is more efficient for the fan-out use case (distributing to 50,000 employees means serializing 50,000 records), and streaming support was useful for the list operations — server-side streaming so the consuming service doesn't have to wait for all records before starting to process.

**Cross-Questions**:

1. "You said you distribute announcements to 50,000 employees. How does that write work — 50,000 individual inserts?"
   > *Probe*: Bulk insert pattern. Django's `bulk_create(batch_size=1000)` — creates 50 database round-trips instead of 50,000. But within a transaction, 50 round-trips is still slow. Alternatively: single `COPY` command via psycopg2 for the fastest PostgreSQL bulk insert. The interviewer wants to hear that you thought about this and didn't do 50K individual inserts.

2. "You chose gRPC. How do frontend teams (if any) consume this service?"
   > *Probe*: Honest answer: gRPC is ideal for backend-to-backend. If a mobile app or browser needs to consume this, you need a gRPC-Web proxy (Envoy) or a REST translation layer. In your case, the Staffing API is the intermediary — it translates between REST (from frontend) and gRPC (to campaign service). Interviewer is testing whether you know the limitations.

3. "How do you handle the case where an announcement is sent to 50,000 employees but the push notification delivery fails for 10,000 of them?"
   > *Probe*: Push notifications are best-effort — fire-and-forget via Celery task calling the notification hub. Failed pushes are logged but don't cause the announcement creation to fail. The announcement is "sent" even if push delivery failed. The user can still see the announcement in-app on next login. This is a design choice: eventual delivery vs. guaranteed delivery for non-critical announcements.

4. "What's the data model for tracking acknowledgment at per-employee granularity?"
   > *Probe*: `employee_announcement` junction table: `(announcement_id, employee_id, acknowledged BOOL, acknowledged_at TIMESTAMP)`. Unique constraint on `(announcement_id, employee_id)`. For an org with 50K employees and 100 announcements, that's 5 million rows. Indexed on `announcement_id` for the "get acknowledgment count" query, and on `employee_id` for "get all unread announcements for employee."

5. "You said this 'significantly improved operational efficiency' — how do you measure that? What's the before/after metric?"
   > *Probe*: A good answer quantifies. Before: HR manually sends WhatsApp to a group, no visibility into reads, manual follow-up. After: automated distribution, real-time acknowledgment rate visible in dashboard, automated reminders to unacknowledged employees. Metric: time-to-100%-acknowledgment for critical announcements went from X days to Y hours.

---

### Interview Question 2

**Interviewer**: "You mentioned gRPC. Why not REST? And what trade-offs did you encounter with gRPC in practice?"

**Your Answer**:
The performance reason: protobuf binary serialization is roughly 3–5x smaller than JSON for the same data, and faster to serialize/deserialize. For a service that serializes thousands of employee records in a single call, this matters.

The type safety reason: protobuf contracts are strict. If a field is missing or has the wrong type, the framework rejects it — no silent failures from mismatched JSON keys. In a microservices system with many services, this prevents integration bugs.

The real trade-off I encountered: debugging is harder. You can't `curl` a gRPC endpoint directly — you need `grpcurl` or a gRPC reflection server. When things go wrong, the binary format makes network-level debugging more involved. Also, gRPC status codes are different from HTTP status codes — mapping your application errors to the right gRPC status code (`INVALID_ARGUMENT`, `NOT_FOUND`, `PERMISSION_DENIED`) requires deliberate design.

Another practical issue: streaming in Django's gRPC implementation (using `django-grpc`) is synchronous under the hood — it blocks a thread per connection. For a server-side streaming endpoint returning 50,000 records, that thread is occupied for the entire stream duration.

**Cross-Questions**:

1. "How do you handle backward compatibility when you need to change the proto schema? For example, adding a required field?"
   > *Probe*: In protobuf 3, all fields are optional by default — adding a new field doesn't break existing clients (they just ignore it). Removing a field or changing field numbers breaks everything. The rule: only add, never remove or renumber. For breaking changes, version the service (`StaffingCampaignServiceV2`). This requires a migration period where both versions run simultaneously.

2. "You mentioned `django-grpc` — Django isn't natively async. How does this affect your gRPC server's throughput under concurrent load?"
   > *Probe*: This is a real bottleneck. Each gRPC connection holds a Python/Django thread from the thread pool. If you have 100 concurrent gRPC connections and your thread pool is 50, the 51st connection blocks. For CPU-bound operations, this is fine — Python's GIL limits true parallelism anyway. For I/O-bound operations (DB queries), you'd want an async framework. The practical answer: you've operated at a scale where this hasn't been the bottleneck, but you're aware of it.

---

## 4. INFRASTRUCTURE OPTIMIZATION

**Resume line**: *"Optimized AJ server infrastructure by decommissioning underutilized VMs and cleaning redundant database records, reducing infrastructure costs."*

---

### Interview Question 1

**Interviewer**: "Walk me through how you identified and safely removed infrastructure. What was your process?"

**Your Answer**:
The trigger was a cost review — our AWS bill was higher than expected. I looked at EC2 instance utilization in CloudWatch over 90 days. Instances with average CPU below 5% and network I/O below a threshold for the entire period were flagged as candidates.

For each candidate, I verified: (1) Is it behind a load balancer? If not, is it receiving direct DNS traffic? (2) Does any other service have a hardcoded reference to its private IP? (3) Are there any cron jobs running on it that would only show CPU spikes once a month?

The decommission process: remove from load balancer → remove DNS entry → keep running in shadow state for 2 weeks → if no complaints from ops or downstream services → snapshot the EBS volume → terminate the instance.

For database cleanup: I identified orphaned records (FK references to deleted parent records), soft-deleted records older than 1 year that were no longer needed for compliance, and duplicate records from data migration issues. I wrote cleanup scripts that ran in batches of 1,000 with a sleep between batches to avoid replication lag and table lock contention.

**Cross-Questions**:

1. "5% CPU over 90 days — a monthly cron job running once would show very low average CPU. How did you rule out low-frequency workloads?"
   > *Probe*: Look at P99 CPU over 90 days, not just average. A cron job shows a spike even if average is low. Also check system logs (`/var/log/cron`, application logs) for the last time the machine did any real work.

2. "You said you delete records in batches with sleep. What batch size and sleep duration? How did you arrive at those numbers?"
   > *Probe*: This depends on your PostgreSQL replication setup. Monitor `pg_stat_replication` lag during the cleanup — if lag starts growing, increase the sleep. A starting point: 1,000 rows per batch, 100ms sleep. For a table with 10M rows, that's 10,000 batches × 100ms = 1000 seconds ≈ 16 minutes. That's acceptable for a background cleanup job.

3. "You said you snapshots EBS before termination. EBS snapshots cost money. What's your retention policy for those snapshots?"
   > *Probe*: Cost-aware answer: keep snapshots for 30 days post-decommission. If nothing breaks in 30 days, delete them. Set up a Lambda function (or AWS Data Lifecycle Manager) to auto-delete old snapshots. This shows you think about the full cost picture, not just the savings.

4. "Cleaning database records — how do you get approval for deleting production data? Who signs off?"
   > *Probe*: This is a process/ownership question. You need a review from the product team (is this data needed for any feature?), legal/compliance sign-off (retention requirements), and an engineering review of the delete logic. Document the cleanup plan, get Slack/email approval, run in staging first. Never delete production data based on your own judgment alone.

5. "What was the actual cost reduction? In dollar terms or percentage?"
   > *Probe*: Be ready with a number even if approximate. "We decommissioned X VMs saving approximately $Y/month. DB cleanup freed Z GB reducing storage costs by W/month." If you don't have exact figures, acknowledge that and explain why (no direct billing access at your level).

---

### Interview Question 2

**Interviewer**: "After the cleanup, how do you prevent this drift from happening again?"

**Your Answer**:
A few mechanisms I put in place:
- CloudWatch billing alarms: alert when monthly cost exceeds a threshold, prompting review
- Tagging policy: every EC2 instance must have `Owner` and `Service` tags. Without tags, a weekly Lambda script flags them for review
- Quarterly infrastructure audit: review CloudWatch utilization reports for all running instances

For database records: added TTL-based soft delete to high-volume tables (notification task history older than 6 months is archived to S3 in Parquet format and deleted from PostgreSQL). This prevents the accumulation problem at the source.

**Cross-Questions**:

1. "You mentioned archiving to S3 in Parquet — how do you query that archived data if someone needs it for an audit?"
   > *Probe*: AWS Athena: schema-on-read SQL queries directly on S3 Parquet files. Define a Glue catalog table pointing to the S3 path, run Athena queries. Cheap for infrequent audit queries. For regular analytics, point a BI tool (Metabase, Superset) at Athena.

2. "Tagging policy with a Lambda enforcement script — what happens if someone deploys a new service without tags? Is it auto-deleted or just flagged?"
   > *Probe*: Auto-deletion is too risky — flag + alert + 24-hour grace period before escalating to the engineer's manager. Service control policies (SCPs) in AWS Organizations can enforce tagging at launch, preventing untagged resources from being created at all. Proactive vs. reactive enforcement.

---

## 5. EXOTEL INTEGRATION — CALLING SYSTEM

**Resume line**: *"Integrated Exotel to confirm the onboarding of candidates, reducing the TAT for the Operations team by 50%."*

---

### Interview Question 1

**Interviewer**: "What was the onboarding confirmation process before Exotel, and what did you build?"

**Your Answer**:
Before: the Operations team manually called candidates on their joining date to confirm they had arrived. With hundreds of joinings per day across multiple clients, this was a full-time activity for several ops agents. Missed calls meant delayed status updates, cascading delays in payroll and compliance.

I integrated Exotel — a cloud telephony platform — to automate this. The system creates a call campaign for all employees joining on a given day, batches them, and initiates automated calls via the Exotel API at a scheduled time (11am). If a call goes unanswered, it retries at 5pm.

Architecturally: a gRPC service handles call campaign creation (storing campaign + per-employee records), and a Celery task handles the actual Exotel API calls in batches. Exotel's webhooks report back call status (answered, unanswered, busy, failed), which updates our records. Operations can now see a real-time dashboard of joining confirmation status instead of tracking it manually.

**Cross-Questions**:

1. "50% TAT reduction — how did you measure that? What was the TAT before and after?"
   > *Probe*: Be specific. TAT was measured from "joining date" to "joining confirmed in system." Before: average 2–3 days (ops team would call, no answer, call next day, etc.). After: average 1 day (automated morning call, retry in evening, escalation next day). The 50% is TAT improvement, not cost reduction — though ops agent hours on manual calls also dropped.

2. "What happens if the automated call goes unanswered even after the retry at 5pm? The manual process at least allowed a human to leave a voicemail."
   > *Probe*: Escalation path: unconfirmed candidates get flagged in the dashboard, an ops agent gets an alert, and they manually follow up. The automation handles the 80% case (candidates who answer), freeing ops agents to focus on the 20% edge cases. This is a better use of human attention than calling everyone.

3. "Exotel has rate limits and concurrent call limits. How did you handle this when batching hundreds of calls?"
   > *Probe*: Exotel API rate limits and concurrent call limits per account. Batch size is set below Exotel's concurrent limit. If you exceed it, Exotel returns an error and the Celery task handles retry with backoff. Monitoring: track how many calls Exotel rejects vs. accepts in each batch.

4. "You're calling candidates on a virtual number — some candidates may not recognize the number and ignore it. How does this affect your 50% TAT improvement claim?"
   > *Probe*: This is a real-world limitation. Mitigation: SMS the candidate a few minutes before the call ("You will receive a call from +91-XXXX to confirm your joining"). Prior notice increases answer rate. Also: caller ID registered to the company name in Exotel settings. Interviewer is testing whether your "50%" claim is robust.

5. "The call campaign is scheduled daily at 11am. What if the Celery Beat scheduler misses a run — say, the pod was being restarted at exactly 11am?"
   > *Probe*: Celery Beat is a single-point-of-failure scheduler. If the Beat pod restarts, it misses the run. Solutions: (1) run Beat with HA (leader election, e.g., celery-redbeat which stores schedule in Redis with distributed locking), (2) have a watchdog that checks if the daily run happened and triggers a catch-up if not, (3) accept the occasional miss and have ops handle it.

---

## 6. AUTHORIZATION + MICROSERVICE ARCHITECTURE

**Resume line**: *"Set up the foundational architecture to extend existing microservices and develop additional ones for Authorization, Staffing-Campaign, Bank Account Verification (including Payout), as well as a report download service from Elasticsearch."*

---

### Interview Question 1

**Interviewer**: "Tell me about the Authorization service you designed. What does it do and why did it need to be its own service?"

**Your Answer**:
The authorization service is a centralized permission store. It exposes two gRPC operations: `GetUserPermission` (given a user ID, return their permissions as a list of `{object, operation}` tuples) and `DeleteUserCacheData` (invalidate the cache for a user when their permissions change).

It's separate because: multiple services (staffing API, campaign service, Excel processor) all need to know "can this user do this action?" If each service had its own permission logic, you'd have divergent implementations and data duplication. Centralizing it means one source of truth, and changes to the permission model propagate consistently.

Redis caching is critical here: permission checks happen on every gRPC request. Without caching, the authorization service would be a hot synchronous dependency on every single API call. With Redis (TTL-based), most permission checks are sub-millisecond cache hits.

**Cross-Questions**:

1. "Redis cache with TTL — if an admin revokes a user's permissions, how quickly does that take effect?"
   > *Probe*: With pure TTL-based caching, revocation doesn't take effect until the TTL expires (could be minutes). That's the `DeleteUserCacheData` RPC — it explicitly invalidates the cache for a user when permissions change. The revocation flow: Admin revokes permission → DB updated → call `DeleteUserCacheData` gRPC → cache evicted → next request fetches fresh permissions.

2. "What's the cache key structure? If a user has permissions in multiple organizations, does a single cache key hold all their permissions?"
   > *Probe*: Cache key: `permissions:{user_id}` → serialized list of all permission tuples. Or more granular: `permissions:{user_id}:{org_id}` if permissions are org-scoped. The tradeoff: fine-grained keys allow selective invalidation; coarse keys reduce cache misses.

3. "This service is a synchronous dependency on every API call. What happens if the authorization service is down?"
   > *Probe*: Critical question. Options: (1) fail open — allow the request if auth service is down (bad for security), (2) fail closed — reject all requests if auth service is down (bad for availability), (3) stale-cache fallback — use the last known cached permissions even if expired (reasonable if TTL recently expired). Your answer should acknowledge this is a hard availability vs. security trade-off.

4. "How do you handle the authorization service itself going through a schema change — for example, adding a new permission type?"
   > *Probe*: Proto backward compatibility: new field in `PermissionResponse` doesn't break existing consumers (they ignore unknown fields). But if you add a new operation type (e.g., `BULK_EXPORT`) that existing services don't check for, those services will silently grant or deny the permission incorrectly. Need to audit all permission check code across services when adding new permission types.

---

### Interview Question 2

**Interviewer**: "You mentioned a report download service from Elasticsearch. Tell me about that."

**Your Answer**:
The staffing service uses Elasticsearch for employee analytics and reporting — aggregations across attendance, salary, and compliance data at org level. But Elasticsearch results need to be exported as downloadable reports (CSV or Excel) for HR teams.

The report service handles async report generation: a user requests a report with filters (org, date range, report type), the request is queued, a worker runs the ES aggregation query, transforms the result into the requested format, uploads to S3, and sends the user a download link via notification.

The key design challenge was large ES result sets — ES has a default 10,000 hit limit for regular queries. For full exports, I used the Scroll API (or PIT + search_after for more recent ES versions), which paginates through all results without loading everything into memory.

**Cross-Questions**:

1. "Elasticsearch Scroll API has a performance impact on the cluster — it keeps a search context open. For large exports, what's the impact and how did you manage it?"
   > *Probe*: Scroll API pins a point-in-time snapshot of the index on each shard — memory overhead proportional to scroll TTL and number of concurrent scrolls. Mitigation: short scroll TTL (1 minute), limit concurrent exports per user, use PIT + search_after in newer ES versions (more efficient). Also: don't run large exports during peak query hours.

2. "A user requests a 1M-row export. How long does this take and what's the user experience?"
   > *Probe*: Realistic timing: Elasticsearch retrieves in batches of 1,000–10,000 rows. At 10,000 rows/batch, 100 batches to get 1M rows. At 200ms per ES request, that's 20 seconds just for data retrieval, plus Excel writing time. Total: minutes. User experience: show "export in progress" with email notification when done. Never block the user on a synchronous response.

---

## 7. BANK ACCOUNT VERIFICATION + PAYOUT

**Resume line**: *"Bank Account Verification (including Payout)"*

---

### Interview Question 1

**Interviewer**: "Tell me about the bank account verification system. What problem does it solve and how does it work technically?"

**Your Answer**:
The problem: before paying salary to an employee, we need to verify their bank account is valid. A wrong account number means the payment fails or, worse, goes to the wrong person. We use a "penny drop" verification: send ₹1 to the account, if it succeeds the account is valid.

Technically: when an employee submits their bank details, we trigger a verification request to Axis Bank via their API. Axis attempts the penny transaction and sends a callback. The callback arrives as a SOAP webhook (Axis's requirement) to our integration service, which decrypts the payload, extracts the verification result, and updates the employee record.

For the payout flow: after verification, salary disbursement calls Axis Bank to initiate the transfer. Axis processes it asynchronously and sends a status callback via the same SOAP reverse-feed mechanism. A SQS consumer in the staffing service picks up these status updates and marks the payslip as paid.

**Cross-Questions**:

1. "Penny drop — if the ₹1 goes to the wrong account (e.g., employee provides someone else's account), you've still "verified" it successfully. How does penny drop actually help?"
   > *Probe*: Penny drop verifies account existence and activity, not ownership. A more complete verification is penny drop + account holder name matching against the employee's name on record. Some bank APIs return the account holder name with the transaction confirmation. If names don't match within a fuzzy threshold, flag for manual review.

2. "The SOAP callback comes from Axis Bank. How do you authenticate that it's genuinely Axis and not a spoofed request?"
   > *Probe*: WS-Security (SOAP-level): username/password in SOAP header, plus timestamp to prevent replay attacks. Additionally: IP whitelisting — only allow SOAP calls from Axis Bank's known IP ranges. TLS for transport encryption. This is defense in depth for a financial transaction.

3. "What happens if Axis Bank's callback never arrives — the payment is in an unknown state?"
   > *Probe*: Reconciliation: run a daily job that fetches transaction status from Axis Bank's inquiry API for all payments in "pending" state older than 1 hour. This catches callbacks that were lost due to network issues. Also: Axis Bank has a retry mechanism for callbacks — if your endpoint is down, they retry. Ensure your endpoint is highly available (multiple pods, health checks).

4. "Salary payout for a company with 10,000 employees — you're initiating 10,000 bank transfers. Does this happen in one big batch or incrementally?"
   > *Probe*: Axis Bank likely has a bulk payment API that accepts a file of transactions, not 10,000 individual API calls. If it's individual calls, you need to rate-limit and batch them. The status callbacks would then arrive asynchronously over hours. Monitoring: track the % of salary payments confirmed vs. pending over time, alert if confirmation rate is below expected threshold by EOD.

---

## 8. CASHMILA — INDEPENDENT PRODUCT

**Resume line**: *"Designed and deployed scalable backend architecture using Django, PostgreSQL, Redis, and AWS. Built event-driven commission and attribution engine using Celery."*

---

### Interview Question 1

**Interviewer**: "Tell me about CashMila. What does it do and what were the interesting technical challenges?"

**Your Answer**:
CashMila is a cashback and coupon platform — users shop through our affiliate links and earn cashback from merchant commissions. The core technical challenge is attribution: tracking that a specific user clicked our affiliate link, made a purchase, and correctly attributing the commission to them.

The attribution engine works like this: when a user clicks an affiliate link, I generate a `click_id` and store the mapping `{click_id → user_id, merchant, timestamp}` in Redis with a 24-hour TTL. The user is redirected to the merchant with the affiliate network's tracking parameters embedded.

When the user purchases, the affiliate network (VCommission or CashKaro) sends a webhook to us with the `click_id` and commission amount. The webhook handler: validates the HMAC signature, looks up the `click_id` in Redis to find the user, creates a `ConversionEvent` in PostgreSQL (idempotent on `order_id`), and fires a Celery task to calculate and credit the user's cashback.

The interesting challenge: affiliate networks have different attribution windows (7 days, 30 days), different commission calculation rules per merchant, and different webhook formats. I built a normalizer layer that maps each network's webhook format to a canonical internal `ConversionEvent` schema.

**Cross-Questions**:

1. "You store click_id in Redis with 24-hour TTL. But if a user clicks on Monday and buys on Wednesday (within the affiliate network's 30-day window), you lose attribution. How do you handle this?"
   > *Probe*: Honest answer: 24-hour TTL is too short for some attribution windows. The fix: use the affiliate network's actual attribution window as the TTL. If VCommission has a 30-day window, set the Redis key to 30 days. Cost implication: Redis memory for a 30-day window × number of daily clicks. At 100K clicks/day × 30 days = 3M keys. Each key is ~200 bytes = 600MB Redis memory. That's manageable.

2. "Webhook with HMAC signature — how do you handle a network that doesn't sign their webhooks?"
   > *Probe*: Secondary verification: IP whitelisting (only accept webhooks from the affiliate network's known IPs). If neither HMAC nor IP whitelist is available, treat it as untrusted: queue for manual review or verify the conversion by querying the affiliate network's API directly before crediting.

3. "You mentioned this is your independent product. How do you handle the operational burden — monitoring, on-call, scaling — as a solo engineer?"
   > *Probe*: Be honest about trade-offs. Cloudflare for DDoS protection and basic WAF. AWS CloudWatch alarms for API error rate and latency. AWS RDS automated backups. For scale: you've prioritized managed services (RDS, ElastiCache, SES) over self-managed to minimize ops burden. Single engineer means: less redundancy, faster decisions, but a single point of failure for knowledge.

4. "Commission reconciliation — how do you verify that what the affiliate network sends matches what they actually pay you?"
   > *Probe*: Reconciliation job: at the end of each payout cycle, compare your internal `ConversionEvent` records against the affiliate network's payout statement (downloaded via their API). Discrepancies fall into: missing conversions (they tracked a sale you didn't), extra conversions (you tracked but they rejected), amount mismatches (different fee deductions). This is business-critical — wrong reconciliation means you either over-pay or under-pay users.

---

## 9. SYSTEM DESIGN DEEP DIVES

---

### Design: High-Throughput Notification System (OTP + Transactional + Marketing)

```
SCALE: 5M notifications/day, 500 OTPs/second peak, < 5 second OTP delivery SLA

┌─────────────────────────────────────────────────────────────────────────┐
│                         NOTIFICATION SYSTEM                              │
│                                                                         │
│  PRODUCERS                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐                   │
│  │ Auth Service│  │Staffing API  │  │Campaign Svc │  ...               │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘                   │
│         │                │                  │                           │
│         └────────────────┼──────────────────┘                          │
│                          │ publish NotificationTask (protobuf)          │
│                          ▼                                              │
│  INGEST                                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  AWS SQS (one queue per message type)                             │  │
│  │  - otp-notifications.fifo  (no delay, 60s visibility)            │  │
│  │  - transactional-notifications  (standard queue)                 │  │
│  │  - marketing-notifications  (standard queue, lower priority)     │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  CONSUME                  │                                             │
│  ┌────────────────────────▼─────────────────────────────────────────┐  │
│  │  Go Consumer Pool (separate deployment per queue type)            │  │
│  │                                                                  │  │
│  │  OTP Consumer:                                                   │  │
│  │    1. Receive (long-poll, WaitTimeSeconds=20)                    │  │
│  │    2. Parse proto (text + base64 fallback)                       │  │
│  │    3. Validate expiry → if expired, push to OTP DLQ              │  │
│  │    4. INSERT into PostgreSQL (task + sms tables)                 │  │
│  │    5. Delete SQS message on DB success                           │  │
│  │    6. Call Priority Engine                                       │  │
│  │                                                                  │  │
│  │  Marketing Consumer:                                             │  │
│  │    + Additional time-window check (don't send 10pm–8am)          │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ROUTING                  │                                             │
│  ┌────────────────────────▼─────────────────────────────────────────┐  │
│  │  Priority Engine                                                  │  │
│  │                                                                  │  │
│  │  OTP           → SMS (Gupshup) → done                           │  │
│  │  TRANSACTIONAL → Email (SendGrid) → [offset] → SMS → Push       │  │
│  │  MARKETING     → Push (Firebase) → [offset] → Email             │  │
│  │                                                                  │  │
│  │  On vendor success: UPDATE task SET status=Done, vendor_id=X    │  │
│  │  On throttle (429): route to RabbitMQ.delayed.firebase           │  │
│  │  On generic fail:   route to RabbitMQ.delayed.common             │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  VENDORS                  │                                             │
│  ┌─────────────┐ ┌────────▼──────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ Gupshup SMS │ │SendGrid Email │ │Firebase Push │ │ WhatsApp API │ │
│  │ (primary)   │ │               │ │              │ │              │ │
│  │ Twilio SMS  │ └───────────────┘ └──────────────┘ └──────────────┘ │
│  │ (fallback)  │                                                       │
│  └─────────────┘                                                       │
│                                                                         │
│  RETRY                                                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  RabbitMQ (3-node HA cluster)                                     │  │
│  │  - delayed.common:   30s → 5min → 30min retry windows            │  │
│  │  - delayed.firebase: 10s → 1min → 10min (firebase-specific)      │  │
│  │  - delayed.marketing: skip if outside time window                 │  │
│  │                                                                  │  │
│  │  RabbitMQ Consumer → Priority Engine (same logic as above)       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  DELIVERY REPORTING                                                     │
│  Vendor webhooks → SQS delivery-reports queue                          │
│  → Delivery Consumer → UPDATE vendor_event table                       │
│                                                                         │
│  QUERY API                                                              │
│  gRPC: GetActivityScore(email) → float64  [email engagement scoring]   │
│  REST: GET /task_status/:id  [task delivery status]                     │
│                                                                         │
│  STORAGE                                                                │
│  PostgreSQL (20 hash partitions on task_id)                            │
│  - task table (main record)                                             │
│  - sms, email, push, whatsapp (per-channel delivery details)           │
│  - vendor_event (delivery callbacks)                                    │
│  - email_score (engagement analytics)                                   │
│                                                                         │
│  MONITORING                                                             │
│  - New Relic: transactions per consumer, delivery rate per channel      │
│  - CloudWatch: SQS queue depth alarm (> 50K → P1)                     │
│  - OTP end-to-end latency: publish → SMS received < 5 seconds SLA     │
│  - Delivery success rate: < 95% OTP success rate → page on-call       │
│                                                                         │
│  SCALING STRATEGY                                                       │
│  - Consumers: HPA on SQS queue depth metric (CloudWatch → KEDA)       │
│  - Priority Engine: stateless, scale with consumers                    │
│  - PostgreSQL: PgBouncer connection pooling, read replicas for queries  │
│  - RabbitMQ: scale workers that consume delayed queues independently   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Design Questions an Interviewer Will Ask:**

1. "Your OTP SLA is 5 seconds. Walk me through every hop and its latency budget."
   > Producer publishes to SQS: ~50ms. SQS long-poll receive: 0ms (message already there) to 20s (worst case, empty queue). Consumer parse + DB insert: ~20ms. Gupshup API call: ~200ms. Gupshup → telecom operator → handset: 2–4 seconds. Total: < 5 seconds if SQS receive is fast. The risk: if all consumer goroutines are busy, a new OTP message waits for a goroutine to free up. Solution: ensure enough consumer replicas to never wait.

2. "At 500 OTPs/second, how many PostgreSQL writes are you doing per second?"
   > At minimum: 2 writes per OTP (INSERT task + INSERT sms). 1,000 writes/second. At 20 hash partitions, that's 50 writes/second per partition. With PgBouncer and connection pooling, PostgreSQL can handle this comfortably. If higher, consider batching the DB inserts (insert 10 at a time) at the cost of slight latency increase.

---

### Design: Staffing Campaign Announcement System

```
SCALE: 200 orgs, max 100K employees per org, 50 announcements/day system-wide

┌────────────────────────────────────────────────────────────────────────┐
│                   STAFFING CAMPAIGN SERVICE                             │
│                                                                        │
│  API LAYER                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  gRPC Server (Django + django-grpc, N pods)                      │  │
│  │                                                                 │  │
│  │  AddAnnouncement(Announcement) → Announcement                   │  │
│  │  ├─ Auth: JWT → user must have ANNOUNCEMENT_CREATE permission   │  │
│  │  ├─ Validate: title, body, org_id required                      │  │
│  │  └─ transaction.atomic():                                       │  │
│  │       INSERT announcement                                        │  │
│  │       bulk_create(EmployeeAnnouncement, batch_size=1000)         │  │
│  │       on_commit → Celery tasks                                  │  │
│  │                                                                 │  │
│  │  ListAnnouncement(org_id) → stream Announcement                 │  │
│  │  └─ Paginated DB query → server-side stream                     │  │
│  │                                                                 │  │
│  │  ListEmployeeAnnouncement(employee_id) → stream                 │  │
│  │  └─ SELECT * FROM employee_announcement WHERE employee_id = X   │  │
│  │     ORDER BY created_at DESC                                    │  │
│  │                                                                 │  │
│  │  EmployeeAcknowledgeAnnouncement → Empty                        │  │
│  │  └─ UPDATE employee_announcement SET ack=true, ack_at=now()     │  │
│  │     WHERE employee_id=X AND announcement_id=Y                   │  │
│  │     (UNIQUE constraint prevents duplicate acks)                  │  │
│  │                                                                 │  │
│  │  GetAcknowledgementCount(announcement_id) → Count               │  │
│  │  └─ SELECT COUNT(*) FROM employee_announcement                  │  │
│  │     WHERE announcement_id=X AND acknowledged=true               │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  DATA LAYER                                                            │
│                                                                        │
│  PostgreSQL                                                            │
│  ┌─────────────────────────┐   ┌───────────────────────────────────┐ │
│  │ announcement             │   │ employee_announcement             │ │
│  │ - id PK                  │   │ - id PK                          │ │
│  │ - org_id (FK, indexed)   │   │ - announcement_id (FK, indexed)  │ │
│  │ - title                  │   │ - employee_id (indexed)          │ │
│  │ - body                   │   │ - acknowledged BOOL DEFAULT false│ │
│  │ - created_at             │   │ - acknowledged_at TIMESTAMP      │ │
│  │ - expires_at             │   │ UNIQUE(announcement_id,          │ │
│  └─────────────────────────┘   │        employee_id)              │ │
│                                 └───────────────────────────────────┘ │
│                                                                        │
│  Elasticsearch                                                         │
│  Index: announcements                                                  │
│  - title, body (full-text, analyzed)                                  │
│  - org_id (keyword, for filtering)                                    │
│  - created_at (date, for sorting)                                     │
│  Consistency: eventual (Celery async indexing, 1-30s lag)             │
│                                                                        │
│  ASYNC LAYER (Celery + RabbitMQ)                                      │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  send_push_notifications(announcement_id)                        │  │
│  │  - fetch employee_announcement rows in pages of 500              │  │
│  │  - for each page: batch call notification-hub gRPC               │  │
│  │  - log push failures, don't propagate (best-effort delivery)    │  │
│  │                                                                 │  │
│  │  index_in_elasticsearch(announcement_id)                         │  │
│  │  - fires only after DB transaction commits (on_commit hook)      │  │
│  │  - if ES down: Celery retry (max 3, exponential backoff)         │  │
│  │  - if max retries: log + alert (reconciliation cron finds it)    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  SCALING STRATEGY                                                      │
│  - gRPC pods: stateless, scale on CPU/memory                          │
│  - Bulk insert 100K rows: Django bulk_create in 100 batches of 1000   │
│    Estimated time: 100 × 10ms = ~1 second                             │
│  - Acknowledgement write: single UPDATE, indexed by (ann_id, emp_id) │
│  - Count query: indexed COUNT, < 10ms for 100K rows                   │
│  - For orgs > 100K employees: consider async distribution (fan-out   │
│    via Celery task rather than in-request bulk_create)                │
│                                                                        │
│  FAILURE HANDLING                                                      │
│  - Transaction atomic: announcement + employee rows = all or nothing  │
│  - Push notification failure: logged, announcement still "sent"       │
│  - ES indexing failure: announcement visible in DB, not in search     │
│    → nightly reconciliation job syncs missing records                 │
│  - Duplicate ack: UNIQUE constraint returns IntegrityError → 200 OK  │
│    (idempotent acknowledgment)                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 10. BEHAVIORAL + OWNERSHIP QUESTIONS

---

**Q1: "Tell me about the most complex production incident you've handled on the staffing backend. Walk me through detection, diagnosis, and resolution."**

Framework (use STAR):
- **Situation**: What was the system state? What was the user impact?
- **Detection**: How did you find out? Alert? User report? Monitoring?
- **Diagnosis**: What tools did you use? (New Relic traces, pg slow query log, CloudWatch logs, kubectl logs)
- **Resolution**: What did you change? Hotfix or rollback?
- **Post-mortem**: What root cause fix and what guardrail did you add?

**What the interviewer is looking for**: Structured thinking under pressure. Ability to trace a problem through distributed systems. Did you have the right observability in place? Did you learn from it?

**Cross-Questions**:
1. "You said you detected it via alert — what was the alert threshold and how did you set it?"
2. "How long was the incident? What was the user-facing impact during that time?"
3. "What would you instrument differently now to detect this faster?"

---

**Q2: "You solely manage the AJ Staffing backend. What happens when you're unavailable — sick, vacation, emergency?"**

**Honest answer structure**:
- Documentation: runbooks for common incidents (DB connection exhaustion, Celery queue backup, SQS consumer lag)
- Monitoring: alerts configured in New Relic/CloudWatch so someone else can see the problem
- Escalation path: other engineers can read logs and restart services even without deep knowledge
- Knowledge transfer: ongoing — you've been adding to a wiki/README as you go
- Acknowledgment of risk: this is a real gap at the team/org level, not something you've fully solved

**What not to say**: "I'm always available" — interviewers at larger companies see this as a red flag (bus factor = 1, and it suggests the org isn't engineered well).

---

**Q3: "You mentioned reducing TAT by 50% with Exotel. How did you measure the impact and how confident are you in that number?"**

**What the interviewer wants**: Rigor in metric definition and measurement.
- What exactly is TAT? Time from joining date to "joining confirmed" status in system?
- How was it measured before automation? Manually tracked in a spreadsheet? Estimated by ops managers?
- Post-automation: query DB for median time between `employee.joining_date` and `employee.joining_confirmed_at`
- Confidence: 50% is the median improvement. P90 might be less impressive. Marketing numbers often use the best case.

---

**Q4: "Tell me about a technical decision you made that you'd make differently today."**

**Good answers draw from your actual projects**:
- `BATCH_SIZE` hardcoded in Excel pipeline — should be configurable per org tier
- Choosing Python for the notification hub's consumer when Go would have been more appropriate (then you did rewrite it in Go — why? What drove that decision?)
- Single-node Celery Beat scheduler for daily calling campaigns — should have used celery-redbeat with Redis-based distributed locking from the start
- Not instrumenting end-to-end latency from day 1 — had to add New Relic tracing retroactively

**What the interviewer wants**: Intellectual honesty. Ability to self-critique. Evidence that you learn from experience.

---

**Q5: "You've been at one company (BetterPlace/AasaanJobs) for 6+ years. How do you know you're not in a local maximum? How have you kept your skills current?"**

**Strong answer components**:
- Independent product (CashMila) forced you to make architectural decisions without organizational constraints — you chose the stack, owned every layer, shipped to production
- System design study (this prep material, the system-design repo you maintain)
- Depth of impact: owned an entire backend stack independently — more engineering surface than most engineers at larger companies who work on one narrow slice

---

## 11. RAPID-FIRE ROUND

### Go

1. **Goroutine vs OS thread?**
   Goroutine: ~2–8KB stack, Go runtime schedules it (M:N model). OS thread: ~1–8MB stack, OS schedules it. Go multiplexes goroutines onto OS threads. You can have 1M goroutines on 8 OS threads.

2. **Buffered vs unbuffered channel?**
   Unbuffered: send blocks until a receiver is ready (synchronous handoff). Buffered: send blocks only when the buffer is full. `make(chan int, 10)` buffers 10 values.

3. **When does `select` use the `default` case?**
   When none of the other cases are ready. Makes the select non-blocking.

4. **What is `sync.WaitGroup` used for?**
   Waiting for N goroutines to complete. `wg.Add(1)` before launch, `wg.Done()` in goroutine, `wg.Wait()` blocks until count reaches 0.

5. **Is reading a nil map safe in Go?**
   Yes, returns the zero value. Writing to a nil map panics.

6. **What is `context.WithTimeout` used for?**
   Propagates a deadline through a call chain. Cancels downstream I/O when deadline passes. Always `defer cancel()` to release resources.

7. **What is a goroutine leak?**
   A goroutine that never terminates (blocked on a channel that nobody writes to, or an infinite loop). Detected with `pprof`. Common cause: forgotten goroutines waiting on a channel that lost all senders.

8. **What does `defer` guarantee about execution order?**
   LIFO — last defer runs first. Defers run even if the function panics.

9. **What is `sync.RWMutex` and when do you prefer it over `sync.Mutex`?**
   Allows multiple concurrent readers OR one exclusive writer. Use when reads greatly outnumber writes — reduces lock contention.

10. **How does Go's GC affect your notification hub service?**
    Stop-the-world pauses of ~1ms — acceptable for async message processing. For latency-sensitive paths, minimize allocations in hot paths (reuse objects with `sync.Pool`).

---

### Kafka / RabbitMQ / SQS

11. **SQS Standard vs FIFO?**
    Standard: at-least-once, best-effort order, near-unlimited throughput. FIFO: exactly-once, strict order, 3,000 msg/sec. Use FIFO when order matters and you can afford lower throughput.

12. **What is SQS visibility timeout and what breaks if it's too short?**
    How long a received message is invisible to other consumers. If processing takes longer than timeout, message reappears — same message processed by two consumers simultaneously. Set to max expected processing time + buffer.

13. **RabbitMQ DLX (Dead Letter Exchange)?**
    When a message expires (TTL), is rejected, or a queue overflows, it's routed to the DLX. Used for: dead-letter queues for failed messages, delayed retry (message TTLs out of a waiting queue into a processing queue).

14. **Why does Kafka retain messages after consumption?**
    Kafka is a log, not a queue. Messages persist for a configurable retention period regardless of consumption. Enables: replay (re-process from offset 0 after a bug fix), multiple independent consumer groups, event sourcing.

15. **What is Kafka consumer lag and why should you alert on it?**
    Difference between the latest offset and the consumer's committed offset. High lag = consumer can't keep up with producers. Alert threshold depends on acceptable processing delay for your SLA.

16. **When would you choose Kafka over SQS for a use case?**
    Kafka: need message replay, ordered processing per key (e.g., all events for user_id X in order), multiple independent consumers reading the same stream, event sourcing, high throughput > 100K msg/sec. SQS: simple task queue, no replay needed, managed service with no operational overhead.

17. **What is RabbitMQ acknowledgment and what happens if a consumer dies before acking?**
    Consumer receives message (marked "unacked"), processes it, sends `basic_ack`. If consumer dies: broker redelivers to another consumer. With `nack(requeue=False)`, message goes to DLX instead of requeuing.

---

### Database Design

18. **What is an index scan vs a sequential scan? When does PostgreSQL prefer sequential?**
    Index scan: follows index B-tree to find row locations, then fetches rows. Sequential scan: reads every row. Postgres prefers sequential when returning a large % of rows (> ~5-10%) because random I/O from index is more expensive than sequential I/O.

19. **Explain MVCC in PostgreSQL in simple terms.**
    Every row has `xmin` (created by transaction) and `xmax` (deleted by transaction). A query only sees rows whose `xmin` <= its transaction ID and `xmax` is either null or newer than its transaction. Result: readers never block writers, writers never block readers. Dead tuples (old versions) are cleaned by VACUUM.

20. **What's the problem with `SELECT FOR UPDATE` in your gRPC handlers?**
    It takes a row-level exclusive lock. If two concurrent gRPC requests lock the same row, one waits. Under high concurrency, this creates a queue of waiting transactions, increasing latency. Use optimistic locking (version field) when contention is low.

21. **N+1 query problem — give a real example from Django.**
    `announcements = Announcement.objects.filter(org_id=1)` then `for a in announcements: print(a.org.name)` — Django fetches the org object for each announcement separately. Fix: `Announcement.objects.filter(org_id=1).select_related('org')` generates one JOIN.

22. **How do you design a leaderboard for 10M users?**
    Redis sorted set (`ZADD leaderboard score user_id`). `ZRANK` for rank lookup — O(log N). `ZRANGE` for top-K — O(log N + K). Persistence: periodically write to PostgreSQL. For real-time leaderboards: Redis is the source of truth; PostgreSQL is the backup.

23. **What's the difference between soft delete and hard delete? What are the trade-offs?**
    Soft delete: set `deleted_at = now()`, filter all queries with `WHERE deleted_at IS NULL`. Hard delete: actual `DELETE`. Soft delete: audit trail, easy undo, but tables grow forever (VACUUM can't reclaim "deleted" rows), and you must remember the filter everywhere. Hard delete: clean tables, but no recovery.

24. **You use both PostgreSQL and MongoDB. How do you decide which to use for a new feature?**
    PostgreSQL: structured data with relations, need ACID transactions, need complex joins (employee → salary → compliance → payment). MongoDB: flexible schema (template definitions with varying fields per org), document-shaped data, no complex joins needed, schema evolution at speed. The Excel service's schema-as-document fits MongoDB naturally. Employee records with FK relationships fit PostgreSQL.

---

### Microservices Patterns

25. **Circuit breaker — what are its three states?**
    CLOSED (normal, requests pass through), OPEN (failing, requests fail fast without calling downstream), HALF-OPEN (one probe request sent; if it succeeds, close; if fails, stay open). Prevents cascading failures.

26. **You have 6 microservices. If service A calls B which calls C which calls D, and D is slow, what happens?**
    Latency cascades: A waits for B, B waits for C, C waits for D. Under load, threads/goroutines in A, B, C all pile up waiting for D. Eventually, thread pools in B and C exhaust and they start failing too — even for requests that don't touch D. Fix: circuit breaker + timeout at each service boundary.

27. **What is the strangler fig pattern?**
    Migrating a monolith to microservices by routing specific endpoints to the new service while the rest continues on the monolith, then gradually "strangling" the monolith. You've used this implicitly — notification hub, campaign service, authorization service extracted from the staffing monolith.

28. **How do you handle distributed transactions across your microservices without 2PC?**
    Saga pattern (choreography): each service completes its local transaction and publishes an event. If a downstream step fails, compensating transactions reverse previous steps. In your Excel pipeline: create job record (step 1) → Celery processes row (step 2) → call Employee API (step 3). If step 3 fails, the compensating action is marking the row as failed in the error report — you don't undo step 2.

29. **What is idempotency and why does it matter for your notification service?**
    Idempotency: calling an operation multiple times produces the same result as calling it once. Critical because SQS delivers at-least-once — the same message can appear twice. Solution: store `task_id` with a UNIQUE constraint. On duplicate delivery, the second INSERT fails with IntegrityError → catch it → treat as "already processed" → still delete the SQS message.

30. **How does Kubernetes handle rolling deploys for your stateful consumers?**
    Rolling deploy replaces pods one at a time. For SQS consumers: the old pod finishes its in-flight message (graceful drain), then terminates. New pod starts and begins consuming. Requires: (1) graceful shutdown signal handling (SIGTERM → stop accepting new messages → drain in-flight), (2) `terminationGracePeriodSeconds` set to max message processing time.

---

## 12. WEAK POINT DETECTION

*These are areas a FAANG-level interviewer will specifically probe. An honest, deep answer is better than a confident shallow one.*

---

### 1. Kafka: On resume, not in any project.

**The probe**: "You list Kafka in your skills. Tell me about a project where you used Kafka and why you chose it over other options."

**Honest answer**:
> "I haven't used Kafka in production — I've studied it deeply and understand the trade-offs. In the notification system, we chose SQS + RabbitMQ because we needed a managed service with no operational overhead (SQS) and sophisticated retry routing (RabbitMQ). Kafka would have been the right choice if we needed event replay (e.g., re-send all notifications from the last hour after a vendor outage), ordered delivery per user, or if we were building an event sourcing architecture. At our scale, SQS was sufficient. I'd choose Kafka for: high-throughput ordered streams, event sourcing, or when multiple independent consumers need to read the same stream."

**What not to say**: List Kafka in your tech skills and then flounder when asked for a concrete use case.

---

### 2. Single-company tenure: 6+ years at one place.

**The probe**: "You've been at one company for 6.5 years. How do you know you can handle a fast-moving, ambiguous environment at a larger company?"

**Strong answer components**:
- Owned and shipped independently within that tenure: 8 different services, an independent product (CashMila)
- Promoted 3 levels (SDE-1 → SDE-3) — evidence of growing scope, not stagnation
- CashMila demonstrates you can operate with zero process: no sprints, no design reviews, ship or die
- You've faced scale challenges (notification hub performance, bulk data processing, distributed systems) that are common at larger companies

---

### 3. Distributed systems theory: may be tested with white-box problems.

**Gaps to prepare**:

**CAP Theorem application**:
- Your PostgreSQL: CP (consistent, partition-tolerant, may sacrifice availability during partition)
- Your SQS: AP (available even during AWS regional partition, eventual consistency)
- Redis: AP by default (can be configured for stronger consistency in cluster mode)
- The real world: most systems are "mostly consistent" and "mostly available" — CAP is a thought exercise, not a binary choice

**Two-Phase Commit (2PC)**:
- You implicitly avoid 2PC across services (Saga pattern instead)
- Know why: 2PC requires a coordinator. If coordinator crashes between "prepare" and "commit", all participants block indefinitely
- Your notification hub: SQS consume → DB insert → SQS delete. This is not 2PC — it's optimistic with at-least-once delivery. The "transaction" is: if DB insert succeeds, delete from SQS. If SQS delete fails, message redelivers and DB insert is idempotent.

**Consensus algorithms** (Raft/Paxos):
- Your RabbitMQ uses quorum queues (Raft-based) for HA
- Know: quorum queues require (N/2 + 1) nodes to acknowledge a write. 3-node cluster: 2 nodes must ack before the producer gets confirmation. This reduces throughput but guarantees no message loss if a node fails.

---

### 4. Security depth: surface coverage in some areas.

**Potential weak areas**:

**JWT best practices**:
- Your services decode JWT locally using a shared secret. Know the alternative: JWT validation against a public key (RS256 instead of HS256). Public key can be distributed; private key only on the auth server. Rotating HS256 shared secrets requires coordinated deploy of all services.

**SQL injection in Django**:
- Django ORM parameterizes queries automatically. But `raw()`, `extra()`, and `RawSQL()` are injection risks. Know which methods are safe and which are not.

**Secret management**:
- How are JWT secrets, AWS credentials, DB passwords stored? `.env` files in development, Kubernetes Secrets in production. Better: AWS Secrets Manager with auto-rotation. Audit trail for secret access.

**mTLS between services**:
- Your gRPC services communicate internally in Kubernetes. Is this traffic encrypted? Default: no TLS on in-cluster traffic. Options: service mesh (Istio/Linkerd) for automatic mTLS, or TLS configured at the gRPC server level. Be ready to answer: "If a bad actor compromises one pod in your cluster, can they call your authorization service directly?"

---

### 5. Go depth: notification-hub written in Go but newer work reverted to Python.

**Questions an interviewer will ask**:

- "How does the Go scheduler work? What is GOMAXPROCS?"
  > GOMAXPROCS controls how many OS threads can execute Go code simultaneously. Default: number of CPUs. The Go scheduler is cooperative + preemptive (Go 1.14+). Goroutines are multiplexed onto OS threads (M:N model). Work-stealing: idle OS threads steal goroutines from busy threads' run queues.

- "How would you profile a Go service that's using too much memory?"
  > `go tool pprof http://localhost:6060/debug/pprof/heap` — shows allocation by function. Look for: large slices not being freed, maps that grow unboundedly, goroutine stacks (each goroutine's stack). Enable pprof: `import _ "net/http/pprof"`.

- "What's the difference between `make([]T, n)` and `make([]T, 0, n)`?"
  > First creates a slice of length n (zero-initialized). Second creates a slice of length 0 with capacity n (pre-allocated, no zero-init cost). Use the second when you'll append up to n items — avoids reallocations.

---

### 6. Academic: GPA 6.43 and 7.42 — some companies screen on this.

**Strategy**: Don't apologize for it. Redirect immediately to project impact.

> "My academic GPA reflects a period where I was focused on building things rather than grades. My M.Tech research at NITK resulted in a published IEEE paper. More importantly, over 6.5 years I've designed and shipped production systems that handle [X notifications/day, Y employees, Z organizations] — let me walk you through the hardest design problem in that work."

Lead with the interview, not the resume filter.

---

### 7. The "what's broken in your current system" question.

**Every senior engineer should be able to critique their own work. Prepare honest answers for**:

- **Batch size hardcoded in Excel pipeline**: Should be configurable per org tier. Small orgs process fine at 10/batch; large orgs with 50K employees and 100ms/call would benefit from 100/batch or parallel calls.

- **No circuit breaker on vendor calls in notification hub**: If Gupshup returns 5xx for 60 consecutive seconds, the system should open the circuit and fail fast rather than accumulating retry debt in RabbitMQ. Currently relies on RabbitMQ backoff.

- **Celery Beat SPOF for campaign calls**: A single Beat pod schedules the daily 11am call campaign. If it's restarting at 11am, the campaign is missed. Should use celery-redbeat (Redis-backed, distributed locking) for HA scheduling.

- **Single-region deployment**: If the AWS region has an outage, the staffing backend is fully down. For the current company size this is acceptable risk. At scale, multi-region active-passive would be the fix.

- **No distributed tracing**: New Relic instrumentation gives per-consumer metrics but not end-to-end request traces across services (staffing API → campaign service → notification hub → Gupshup). OpenTelemetry with Jaeger/Tempo would enable this.

---

## 13. COMPLIANCE CHALLAN PROCESSING TOOL

**Resume line**: *"Built automated Compliance Challan Processing Tool to extract ESIC contribution data from PDFs and update records, reducing manual effort."*

---

### Interview Question 1

**Interviewer**: "Tell me about this tool — what is ESIC challan and what was the manual process you replaced?"

**Your Answer**:
ESIC (Employees' State Insurance Corporation) is a statutory body under the Indian government. Employers must contribute a percentage of each employee's salary toward ESIC monthly. A challan is the payment receipt document that confirms this contribution was made.

The manual process: the finance team would download challan PDFs from the ESIC portal after making payments, then manually read the PDF, extract the contribution amounts per employee, and update those figures in our system to mark employees' compliance records as paid for that month. With thousands of employees across dozens of client organizations, this was hours of manual data entry every month with high error risk.

The tool I built: parses the PDF using a Python library, extracts structured data (employee ESI numbers, contribution amounts, month), and upserts these into the compliance records in PostgreSQL. The tool runs on-demand or as a scheduled job after the monthly payment date.

**Cross-Questions**:

1. "PDF parsing is notoriously fragile — PDFs don't have a standard structure. How did you handle variations in ESIC challan formats across different payroll cycles or portal updates?"
   > *Probe*: The honest answer is that government portal PDFs do change occasionally. The parsing logic uses coordinate-based extraction (positions of text on the page) or pattern-based extraction (regex for ESI numbers, amounts). When the format changes, the extractor breaks silently — data isn't updated. The fix: add validation after extraction. If the extracted employee count doesn't match the expected count for that org's payroll, raise an alert and flag for manual review instead of silently writing wrong data.

2. "How do you validate that the extracted data is correct before writing to the database?"
   > *Probe*: Cross-validation: the total contribution in the PDF should match the sum of individual contributions. Employee count in PDF should match enrolled employees for that period. ESI numbers from the PDF should match registered ESI numbers in your system. Any mismatch → reject and flag. This is more important than raw extraction speed.

3. "What happens if the PDF is password-protected or in an image-based (scanned) format rather than text-based?"
   > *Probe*: Password-protected: need the password, which the finance team provides — store it encrypted, pass at extraction time. Image-based PDF: text extraction libraries (PyPDF2, pdfplumber) won't work. Need OCR — Tesseract or AWS Textract. OCR is significantly less accurate and more expensive. For government portals, the PDF is usually text-based (generated programmatically), so this edge case is rare but real.

4. "This updates compliance records — what's the impact if it writes wrong data? Employee compliance records affect their benefits eligibility."
   > *Probe*: High stakes. An employee incorrectly marked as non-compliant could have ESI benefits denied during a medical emergency. Defense: (1) dry-run mode that shows what would be written without committing, (2) finance team review step before final commit, (3) audit log of every change (which PDF, which field, old value, new value), (4) soft lock — mark records as "pending review" after automated extraction, require a human approval click to finalize.

5. "You said this runs monthly. How do you handle a month where the challan wasn't uploaded — do records remain as 'unpaid' indefinitely?"
   > *Probe*: The system should distinguish between "challan not uploaded yet" and "contribution genuinely not made." A status field: `PENDING`, `UPLOADED_PARSING`, `PARSED_REVIEW`, `CONFIRMED`, `MISSED`. If the 10th of the following month arrives and the challan for the previous month is still `PENDING`, send an alert to the compliance team. Don't let records silently remain unpaid.

---

### Interview Question 2

**Interviewer**: "Walk me through your PDF extraction approach technically — what library, what logic?"

**Your Answer**:
For text-based PDFs, I used `pdfplumber` (Python) which gives you text with positional coordinates. ESIC challans have a tabular structure — rows of employee data with columns for ESI number, name, wages, employer contribution, employee contribution.

The extraction approach:
```python
import pdfplumber

def extract_challan_data(pdf_path: str) -> list[dict]:
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table from page
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if is_employee_row(row):  # filter header/footer rows
                        records.append({
                            "esi_number": clean_esi(row[0]),
                            "employee_name": row[1].strip(),
                            "wages": parse_amount(row[3]),
                            "employer_contribution": parse_amount(row[4]),
                            "employee_contribution": parse_amount(row[5]),
                        })
    return records

def is_employee_row(row):
    # ESI numbers follow a specific format: XX-XX-XXXXXX-XXX-XXXX
    return row[0] and re.match(r'\d{2}-\d{2}-\d{6}-\d{3}-\d{4}', row[0].strip())
```

After extraction, validate totals match the PDF summary section, then bulk-upsert into PostgreSQL using `ON CONFLICT (esi_number, period_month) DO UPDATE SET contribution = EXCLUDED.contribution`.

**Cross-Questions**:

1. "pdfplumber's table extraction relies on PDF line elements. What if the challan PDF doesn't have explicit table borders — just whitespace-separated columns?"
   > *Probe*: pdfplumber has a `snap_tolerance` parameter for column detection based on text alignment rather than explicit lines. Alternatively, use coordinate-based extraction: text at x-coordinate 0–100 is column 1, 100–200 is column 2, etc. This requires calibrating coordinates from a sample PDF — it breaks when the portal changes layout.

2. "You do a bulk upsert. What's the idempotency guarantee — if the same challan PDF is uploaded twice, what happens?"
   > *Probe*: `ON CONFLICT (esi_number, period_month) DO UPDATE` — the second upload overwrites with the same values. Net effect: idempotent. But you should log a warning: "Challan for period X already exists, re-processing." If values differ on re-upload, that's a data integrity concern — log and alert.

---

## 14. GOOGLE DOCS API — ONBOARDING/OFFBOARDING LETTER AUTOMATION

**Resume line**: *"Automated the creation of all template-based onboarding and offboarding letters using the Google Docs API, significantly reducing manual generation for the onboarding team."*

---

### Interview Question 1

**Interviewer**: "What was the manual process for generating these letters and what did you build to replace it?"

**Your Answer**:
Before: the HR/onboarding team had Word document templates for offer letters, appointment letters, relieving letters, experience certificates, etc. For each new joiner or exit, they'd manually open the template, find-and-replace placeholders (`{{employee_name}}`, `{{date_of_joining}}`, `{{salary}}`), save it as a PDF, and email it to the employee. With hundreds of joinings per month across multiple clients, this was hours of repetitive work daily.

I automated this using the Google Docs API. The flow: HR creates a master template document in Google Drive with placeholders. When an employee is onboarded in the system, a Celery task is triggered that:
1. Makes a copy of the template document in a designated Drive folder
2. Calls the Google Docs API's `batchUpdate` to replace all placeholders with actual employee data
3. Exports the document as a PDF via the Drive API
4. Uploads the PDF to S3
5. Sends the PDF to the employee via the notification hub and stores it in their document record

**Cross-Questions**:

1. "Why Google Docs API over simpler alternatives like python-docx or Jinja2 + HTML → PDF?"
   > *Probe*: The HR team already lives in Google Workspace — they own and edit the templates directly in Google Docs without needing engineering help. If we used python-docx (Word templates) or Jinja2 (HTML templates), every template change would require a developer to update the template file in code. With Google Docs, HR edits the template directly. The tradeoff: Google API rate limits, dependency on Google services uptime, and OAuth token management.

2. "Google Docs API has rate limits — 300 requests per minute per project. At 500 joinings per day, each needing 3 API calls (copy, batchUpdate, export), that's 1,500 calls. How do you stay within rate limits?"
   > *Probe*: 1,500 calls/day is ~1 call per minute — well within limits. The issue is burst: if 200 employees join on the first day of the month (batch joining), that's 600 API calls nearly simultaneously. Solution: Celery task rate limiting (`@task(rate_limit='50/m')`) or a dedicated queue with concurrency=1 for document generation. Also: exponential backoff on `429` responses from Google.

3. "Google OAuth token management — how do you handle token refresh for a service account?"
   > *Probe*: Use a Google Service Account (not user OAuth). Service accounts have long-lived credentials (JSON key file) that don't expire. The `google-auth` library handles token refresh automatically. The key file is stored as a Kubernetes Secret. Rotation: generate a new key, deploy, then revoke the old key — brief window of dual keys during rotation.

4. "What happens if a placeholder in the template has a typo (`{{emplpyee_name}}` instead of `{{employee_name}}`) — the letter goes out with an unfilled placeholder?"
   > *Probe*: Validation step before export: after `batchUpdate`, call the Docs API to read back the document content and check for any remaining `{{...}}` patterns. If found, fail the task and alert — don't generate the PDF with unfilled placeholders. This is important because letters are legal documents.

5. "Offer letters include salary, designation, and terms — sensitive legal documents. What's your access control model on the generated PDFs?"
   > *Probe*: Generated PDFs in S3 use signed URLs with short TTL (15 minutes) for employee access — not public URLs. Only the relevant employee and their HR manager can access their document. The Drive copy of the document is in a restricted folder (HR-only access), then deleted after export to PDF. No long-term sensitive data in Google Drive.

---

### Interview Question 2

**Interviewer**: "You said 'significantly reducing manual generation.' What was the actual time saving and how did you measure it?"

**Your Answer**:
Before: each letter took approximately 5–10 minutes of manual HR time (open template, fill placeholders, review, export PDF, email). With 200 joinings per month across clients, that's 1,000–2,000 minutes (16–33 hours) of HR time per month just on letter generation.

After: zero HR time for standard letters. The system generates and delivers the letter automatically within 2 minutes of the employee being created in the system. HR time saved: ~95% for standard letters. The remaining 5% is custom cases (executives, special terms) that still need manual handling.

Measurement: tracked via a "letter generation time" field added to the employee document record — timestamp when HR was notified (before) vs. timestamp when letter was auto-generated (after). Also tracked ops team headcount change — the team that previously had a dedicated "letter generation" function was reallocated to higher-value work.

**Cross-Questions**:

1. "95% automation — what are the 5% custom cases and why can't they be automated?"
   > *Probe*: Custom cases: negotiated terms that differ from the standard template (stock options, special allowances, non-compete clauses), letters for CXO-level employees where every word is reviewed by legal, letters in regional languages (Kannada, Tamil) where the template itself is different. These require a human in the loop — the system flags these for manual handling rather than attempting automation.

2. "Offer letters are generated at offer stage, before the employee is in the system. How do you handle this — the employee record doesn't exist yet?"
   > *Probe*: Pre-creation flow: the offer letter is generated from a candidate/applicant record, not an employee record. The letter contains offer details (proposed salary, designation, start date). Employee record is created only after the candidate accepts and completes joining formalities. The system must handle two entity types: `Candidate` (pre-joining) and `Employee` (post-joining).

---

## 15. DJANGO + PYTHON DEEP DIVE

*Questions an interviewer will ask when they see Django on your resume for 6+ years.*

---

**Q1: "You've used Django for 6 years. What are Django's biggest limitations for a high-scale backend?"**

**Your Answer**:
1. **Synchronous ORM**: Django's ORM is synchronous. Every database query blocks the thread. Django 4.1+ added `sync_to_async` and async ORM support, but it's not fully mature. Under high concurrency with many DB queries, threads pile up waiting.
2. **GIL (Global Interpreter Lock)**: Python's GIL prevents true CPU parallelism. For CPU-bound tasks (PDF parsing, Excel generation), multiple threads don't help — you need multiple processes (Celery workers, Gunicorn workers).
3. **Django Admin at scale**: Django Admin runs queries without pagination optimizations. On tables with millions of rows, admin list views can cause full table scans.
4. **Migrations on large tables**: `ALTER TABLE` on a 50M-row table locks the table (in older PostgreSQL). Django migrations don't handle zero-downtime migration by default — need `django-pg-zero-downtime-migrations` or manual migration strategies.
5. **N+1 in serializers**: DRF serializers are easy to write N+1 queries into. You have to explicitly add `select_related`/`prefetch_related` or you'll hit the DB once per related object.

**Cross-Questions**:
1. "You mention Django's ORM is synchronous. In your gRPC services, every gRPC call hits the DB. Under 100 concurrent gRPC requests, how many DB connections does your service hold?"
   > Each gRPC call = one Django thread = one DB connection (if using persistent connections). 100 concurrent requests = 100 connections. PostgreSQL default `max_connections` is 100. At 100 concurrent requests, you're at the limit. Fix: PgBouncer (connection pooler) — Django connects to PgBouncer, PgBouncer multiplexes onto fewer actual PostgreSQL connections.

2. "Tell me about a Django migration that caused a production incident."
   > Real-world example: adding a `NOT NULL` column with a default on a large table. Django generates `ALTER TABLE employee ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'`. PostgreSQL pre-12 rewrites the entire table for this — full table lock, minutes of downtime. Fix: (1) add column as nullable first, (2) backfill in batches, (3) add NOT NULL constraint (which is fast if no NULLs exist). `django-pg-zero-downtime-migrations` automates this pattern.

3. "How do Django signals work and when would you NOT use them?"
   > Signals (`post_save`, `pre_delete`) are implicit callbacks that fire on model events. Problem: they make code hard to follow — action happens in `views.py`, side effect triggers in `signals.py`. They run in the same transaction, so a signal failure can roll back the original operation. Avoid for: cross-service calls (e.g., don't call an external API in a `post_save` signal — use `transaction.on_commit` + Celery). Use for: tight coupling within the same Django app where the relationship is stable.

---

**Q2: "How do you manage database migrations safely in a production system with zero downtime?"**

**Your Answer**:
Zero-downtime migration strategy depends on the operation:

**Adding a nullable column** — safe, no lock:
```sql
ALTER TABLE employee ADD COLUMN middle_name VARCHAR(100);
```
No table rewrite. Instant.

**Adding a NOT NULL column** — needs 3-step migration:
```python
# Migration 1: Add as nullable
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(model='Employee', name='status',
                           field=models.CharField(max_length=50, null=True))
    ]

# Deploy. Then backfill in batches via management command:
# Employee.objects.filter(status__isnull=True).update(status='ACTIVE')

# Migration 2: Add NOT NULL constraint (fast, no rewrite if no NULLs exist)
class Migration(migrations.Migration):
    operations = [
        migrations.AlterField(model='Employee', name='status',
                             field=models.CharField(max_length=50))
    ]
```

**Adding an index** — use `CONCURRENTLY`:
```python
operations = [
    migrations.RunSQL(
        "CREATE INDEX CONCURRENTLY idx_employee_org ON employee(org_id)",
        reverse_sql="DROP INDEX idx_employee_org"
    )
]
```
`CONCURRENTLY` builds the index without locking table. Can't run inside a transaction — wrap in `atomic = False` migration.

**Cross-Questions**:
1. "You deploy Django apps on Kubernetes. During a rolling deploy, old and new pods run simultaneously for a few minutes. If migration 1 adds a column that new code writes to, old code doesn't know about it. What problems can arise?"
   > Old pod reads the row and doesn't know about the new column — that's fine (Django ignores unknown DB columns). New pod writes to the new column — fine. But: if the migration removes a column that old code reads, old pods crash. Rule: never remove a column or rename a column in a migration without first removing all code references and deploying.

2. "How do you test migrations before running on production?"
   > Run `./manage.py migrate --plan` to see what will execute. Run against a production-sized data copy (anonymized) in staging. Measure time and lock duration with `pg_locks` monitoring during staging run. For large migrations, test with `pg_restore` of a recent production snapshot.

---

**Q3: "What is Django's `select_related` vs `prefetch_related` and when does each fail you?"**

**Your Answer**:
- `select_related`: generates a SQL JOIN. Works for ForeignKey and OneToOneField. One query, returns all related data. Fails when: the related table is huge and you only need one field (JOIN fetches all columns), or when the FK is nullable and you JOIN across a lot of NULLs (wasted JOIN work).

- `prefetch_related`: runs a separate query with `WHERE id IN (...)`. Works for ManyToManyField and reverse ForeignKey. Fails when: the `IN` list is huge (1000+ IDs — PostgreSQL handles it but it's a large query), or when you need to filter the prefetched queryset (need `Prefetch` object with custom queryset).

```python
# select_related: one SQL JOIN
Employee.objects.select_related('organization').filter(org_id=1)
# SQL: SELECT e.*, o.* FROM employee e INNER JOIN organization o ON e.org_id = o.id

# prefetch_related: two queries
Announcement.objects.prefetch_related('employee_announcements').filter(org_id=1)
# SQL 1: SELECT * FROM announcement WHERE org_id = 1
# SQL 2: SELECT * FROM employee_announcement WHERE announcement_id IN (1, 2, 3, ...)
```

**Cross-Questions**:
1. "In your staffing service with 100+ gRPC RPCs, how do you enforce that developers don't introduce N+1 queries?"
   > Django Debug Toolbar in development catches N+1 in the UI. For gRPC (no browser), use `django-silk` for profiling, or log query counts via `django.db.connection.queries` in tests. Better: `nplusone` library raises an exception in test when N+1 is detected. Code review checklist: every ORM queryset in a loop needs a `select_related` or `prefetch_related`.

---

## 16. CELERY DEEP DIVE

*You use Celery heavily across multiple services. Interviewers will probe this.*

---

**Q1: "Tell me about Celery's task execution model. How many tasks can one worker run concurrently?"**

**Your Answer**:
Celery workers have two dimensions:
1. **Concurrency**: number of concurrent task executions per worker process. Default: CPU count. With `--concurrency=4`, the worker runs 4 tasks simultaneously using a process pool (prefork) or thread pool (gevent/eventlet).
2. **Prefetch count** (`CELERYD_PREFETCH_MULTIPLIER`): how many tasks a worker fetches ahead of time. Default: 4 per concurrency slot. With `--concurrency=4`, the worker holds up to 16 tasks at once (running 4, queued 12).

For long-running tasks (your Excel upload): set `CELERYD_PREFETCH_MULTIPLIER=1`. Otherwise a single worker hogs 16 tasks, preventing other workers from picking them up.

For the pool type: `prefork` (default) — true multiprocessing, bypasses GIL. Good for CPU-bound work. `gevent` — cooperative greenlets, good for I/O-bound work (lots of API calls). `eventlet` — similar to gevent.

**Cross-Questions**:
1. "You have prefork workers for Excel processing (CPU-bound). Your tasks make HTTP calls to the Employee API — these I/O calls block the process. Isn't gevent better here?"
   > Mixed workload: CPU-heavy (openpyxl parsing) + I/O-heavy (API calls). Pure prefork: 4 processes, each blocks during API call — wastes CPU. Pure gevent: cooperative multitasking, but openpyxl uses native extensions that don't yield to gevent — can block the entire greenlet pool. Practical answer: prefork with enough concurrency that blocked workers don't stall the queue. Or separate the CPU work (validation) from I/O work (API calls) into chained tasks.

2. "A Celery task for Excel upload can take 30 minutes. Your soft timeout is 25 minutes. Walk me through what happens at minute 25."
   > Soft timeout raises `SoftTimeLimitExceeded` exception in the task (via SIGALRM). The task can catch this and do graceful cleanup — checkpoint progress, mark job as timed out, notify user. At minute 30, the hard timeout sends SIGKILL — no cleanup possible. Strategy: soft timeout → checkpoint + re-queue the remaining work as a new task from where it stopped.

3. "How do you monitor Celery task failures in production?"
   > Celery has built-in `task_failure` signal. Use Flower (Celery's monitoring UI) for real-time task status. But Flower doesn't persist history well. Better: emit task events to New Relic/Datadog — task name, execution time, success/failure, queue depth. Alert on: error rate > X%, queue depth > Y (tasks accumulating faster than workers process), task execution time increasing (degraded worker performance).

---

**Q2: "What is a Celery chain, group, and chord? When would you use each?"**

**Your Answer**:
```python
from celery import chain, group, chord

# Chain: sequential tasks, output of one is input of next
result = chain(
    fetch_employees.s(org_id),
    validate_rows.s(),
    write_to_excel.s(),
    upload_to_s3.s()
)()

# Group: parallel tasks, all start simultaneously
result = group(
    send_sms.s(employee_id) for employee_id in employee_ids
)()

# Chord: parallel tasks, then a callback when all complete
result = chord(
    group(process_chunk.s(chunk) for chunk in chunks),
    finalize_upload.s(job_id)  # runs after all chunks complete
)()
```

For Excel upload: `chord` is the ideal pattern — split the file into chunks, process each chunk in parallel across workers, then finalize when all chunks complete.

**Cross-Questions**:
1. "Chord uses a result backend to track when all tasks complete. You use Redis as result backend. What happens if Redis is down when a chord's subtask completes?"
   > The subtask result can't be stored in Redis — the subtask fails or hangs. The chord callback never fires. Celery does not handle result backend unavailability gracefully by default. This is a real reliability concern: Redis is now a critical path dependency for chord completion, not just task queuing. Mitigation: use Redis with replication and failover (Redis Sentinel or ElastiCache with automatic failover). Monitor Redis separately from broker availability.

2. "In your notification system, if you wanted to batch-send 10,000 push notifications simultaneously using Celery group, what could go wrong?"
   > 10,000 tasks → 10,000 Redis/RabbitMQ messages enqueued simultaneously. This is a thundering herd: all workers start pulling at once. Firebase has concurrent connection limits and rate limits per second. The parallel group would hit Firebase's rate limits immediately. Better: `group` with rate limiting at the task level (`@task(rate_limit='100/s')`), or a single task that internally processes in batches with `asyncio.gather`.

---

## 17. REDIS DEEP DIVE

*Redis appears across Excel pipeline (broker + progress), notification hub (rate limiter), authorization service (permissions cache). Interviewers will probe this.*

---

**Q1: "You use Redis as both a Celery broker and a result/progress store. What are the trade-offs of Redis vs RabbitMQ as a Celery broker?"**

**Your Answer**:
Redis as Celery broker:
- **Simple setup**: Redis is already in the stack for caching — no extra infrastructure
- **Fast**: in-memory, sub-millisecond enqueue/dequeue
- **Limitations**: Redis `LPOP`/`RPUSH` doesn't support task priorities natively. No message acknowledgment at the broker level — if a worker crashes, the task is lost (the `acks_late=True` workaround using Celery's own acknowledgment layer helps but isn't as robust as AMQP)

RabbitMQ as Celery broker:
- **AMQP**: native acknowledgment, persistence to disk, message TTL, DLX
- **Priority queues**: native support via AMQP priority field
- **Complex**: separate service to operate and monitor
- **Better for**: tasks where durability matters more than speed, complex routing needed

In your setup: Redis broker for Excel pipeline (speed matters, short-lived tasks). RabbitMQ broker for staffing service Celery tasks (durability matters — payroll tasks must not be lost).

**Cross-Questions**:
1. "Redis stores Celery task queues as lists (`LPUSH`/`BRPOP`). What happens to queued tasks if your Redis instance runs out of memory?"
   > Redis enforces a `maxmemory` policy. With `allkeys-lru` (evict least recently used keys), it could evict queued Celery tasks — tasks are silently lost. With `noeviction` (reject writes when full), Celery's `apply_async` raises a `ConnectionError` — tasks are not queued, caller gets an error. For task queues: use `noeviction` so you get an explicit error rather than silent data loss. Monitor memory headroom and alert before it fills.

2. "You store real-time progress in Redis Streams for the Excel upload. How is a Redis Stream different from a Redis List?"
   > List: ordered, `LPOP` consumes the item (destructive read). Stream: ordered log, items persist after reading. Consumers use `XREAD` with a cursor — they can re-read from any position. Consumer groups allow multiple consumers to coordinate (each message delivered to only one consumer in the group). For progress tracking: Stream is better because a reconnecting WebSocket client can resume from where it left off using the last seen ID.

3. "Redis is single-threaded for commands. At high throughput, is this a bottleneck for your notification hub's rate limiter?"
   > Redis single-threaded for command execution, but I/O is multiplexed (event loop). Benchmarks show Redis handles ~100K simple commands/second on a single instance. Your notification hub's rate limiter makes ~1 Redis command per message consumed. At 500 OTPs/second, that's 500 Redis commands/second — well within limits. Redis becomes a bottleneck at 100K+ operations/second, where Redis Cluster (sharding) or pipelining (batch commands) is needed.

---

**Q2: "How do you handle Redis cache invalidation for permissions in the authorization service?"**

**Your Answer**:
Cache key: `permissions:{user_id}` → serialized permission list, TTL of N minutes.

The invalidation flow when permissions change:
```python
# In authorization service, when admin revokes a permission:
def revoke_permission(user_id: int, permission_id: int):
    # 1. Update PostgreSQL
    UserPermission.objects.filter(
        user_id=user_id, permission_id=permission_id
    ).delete()
    
    # 2. Immediately invalidate Redis cache
    cache.delete(f"permissions:{user_id}")
    # Next request will hit DB and re-populate cache
```

The `DeleteUserCacheData` gRPC endpoint exists specifically for this — other services can call it when they know a user's permissions have changed (e.g., the staffing service knows when an HR manager is deactivated).

**Cross-Questions**:
1. "Cache invalidation is called after DB update. What if the cache invalidation call fails (Redis is briefly unavailable)? The DB has the revoked permission but the cache still has the old one."
   > Stale cache: the user retains their old permissions until TTL expires. For a security-sensitive revocation (employee termination, insider threat), this is unacceptable. Options: (1) shorten TTL for sensitive operations — force cache miss within 60 seconds, (2) write-through invalidation — use Redis MULTI/EXEC transaction to delete cache atomically after DB update, (3) accept the stale window for non-critical permission changes. This is a fundamental distributed systems trade-off: consistency vs. availability.

2. "You cache the entire permission list for a user. If a user has 50 permissions, and one changes, you invalidate and re-fetch all 50. Is there a more efficient approach?"
   > Fine-grained caching: `permission:{user_id}:{resource_type}:{resource_id}` → bool. Invalidate only the specific permission that changed. But: this means checking N cache keys per request (one per permission check in the request). More cache hits, but more Redis round-trips. For your access pattern (check 3–5 permissions per request), loading all permissions in one cache miss + check locally is more efficient than fine-grained.

---

## 18. AWS DEEP DIVE

*Your resume lists AWS EKS, ECR, S3, Lambda, SQS, SES. Interviewers will verify depth.*

---

**Q1: "You run services on EKS. Walk me through a deployment — from code push to running in production."**

**Your Answer**:
```
1. Developer pushes code to Git branch → PR opened
2. Azure Pipeline (CI) triggered:
   - Run tests (pytest / go test)
   - Build Docker image
   - Tag image: {ECR_URL}/{service}:{git_sha}
   - Push to Amazon ECR
   - If main branch: trigger deployment

3. Deployment step:
   - Update Kubernetes Deployment manifest: image tag → new git_sha
   - kubectl apply -f deployment.yaml
   - Kubernetes rolling update: new pods start, readiness probe passes,
     old pods terminated (terminationGracePeriodSeconds honored)
   
4. Health check:
   - Readiness probe: HTTP GET /health → 200 OK before receiving traffic
   - Liveness probe: HTTP GET /health → if failing, pod restarted
   
5. Rollback:
   - kubectl rollout undo deployment/{service}
   - Rolls back to previous ReplicaSet (previous image tag)
```

**Cross-Questions**:
1. "Your Celery workers process long-running tasks. During a rolling deploy, an old worker pod is processing a 30-minute Excel upload. Kubernetes sends SIGTERM. What happens?"
   > Without graceful shutdown: SIGTERM kills the worker immediately. Task fails, job is lost (or re-queued if `acks_late=True`). With graceful shutdown: the worker catches SIGTERM, stops accepting new tasks, waits for in-flight tasks to complete, then exits. `terminationGracePeriodSeconds` must be >= max task duration. For 30-minute tasks: `terminationGracePeriodSeconds: 1800`. Kubernetes waits up to 30 minutes before SIGKILL.

2. "EKS auto-scales based on CPU. Your notification consumers are I/O-bound (waiting on SQS, calling Gupshup) — CPU is always low even under load. How do you auto-scale them?"
   > CPU-based HPA won't work. Use KEDA (Kubernetes Event-Driven Autoscaling) — scales based on SQS queue depth. `ScaledObject`: when SQS queue has > 1000 messages, add pods; when < 100, remove pods. KEDA queries CloudWatch metrics for queue depth. This correctly scales I/O-bound consumers based on actual backlog.

3. "How do you manage secrets (DB passwords, API keys) in EKS? Where do they live?"
   > Options used: Kubernetes Secrets (base64-encoded, not encrypted at rest by default — enable KMS encryption for etcd). Better: AWS Secrets Manager → Kubernetes External Secrets Operator synchronizes secrets from Secrets Manager into Kubernetes Secrets. Even better: IAM Roles for Service Accounts (IRSA) — pods assume an IAM role directly, no static credentials for AWS services.

---

**Q2: "You use S3 for storing Excel files and generated documents. How do you handle large file uploads to S3 from your application?"**

**Your Answer**:
Two patterns based on file size:

**Small files (< 100MB) — server-side upload**:
```python
import boto3
s3 = boto3.client('s3')
s3.upload_fileobj(file_object, bucket_name, s3_key)
```
File goes: Browser → Your API → S3. Doubles bandwidth consumption on your API server.

**Large files — pre-signed URL for direct upload**:
```python
# Backend generates pre-signed URL
presigned_url = s3.generate_presigned_post(
    Bucket=bucket_name,
    Key=s3_key,
    ExpiresIn=300  # 5 minutes
)
# Return URL to frontend → frontend uploads directly to S3
# File goes: Browser → S3 directly (bypasses your API)
```

For generated Excel files (download scenario): Celery worker generates the file, streams it to S3 using multipart upload for files > 5MB, then generates a pre-signed GET URL (15 minutes TTL) for the user to download.

**Cross-Questions**:
1. "Pre-signed URL for direct browser → S3 upload. The URL contains credentials. What prevents someone from intercepting the URL and uploading malicious content to your S3 bucket?"
   > The pre-signed URL is specific to one S3 key (path), one HTTP method (PUT), and expires in 5 minutes. An intercepted URL can only be used to upload to that specific file path before expiry. After the upload, your Lambda/Celery worker should: validate file type (check magic bytes, not just extension), virus scan (ClamAV or AWS GuardDuty for S3), and enforce max file size (S3 pre-signed POST `Conditions` field).

2. "Your Excel files are HR data — employee names, salaries, bank details. How do you secure this data at rest in S3?"
   > S3 Server-Side Encryption: SSE-S3 (AWS-managed keys, minimal overhead) or SSE-KMS (customer-managed keys, audit trail via CloudTrail for every key usage). For regulatory compliance (employee financial data): SSE-KMS with a dedicated KMS key per customer org. S3 bucket policy: block all public access, restrict access to specific IAM roles. S3 Access Logs: log every GetObject request for audit.

---

## 19. SDE-3 LEVEL QUESTIONS — TECHNICAL LEADERSHIP

*At SDE-3, interviewers probe beyond individual execution — they want architecture ownership, mentoring, and engineering culture contributions.*

---

**Q1: "You were promoted to SDE-3 in 2025. What changed in how you work compared to SDE-2?"**

**Your Answer**:
At SDE-2: I was given problems to solve and owned the implementation. I'd ask for design reviews and get feedback before building.

At SDE-3: I'm the one who identifies the problems, proposes the solution, gets buy-in from stakeholders, and sets technical direction for the team. Instead of getting design reviews, I'm running them. The output isn't just working code — it's architecture decisions documented well enough that the team can execute without me being the bottleneck.

Concretely:
- I make the call on tech stack for new services without needing approval
- When junior engineers ask "should we use X or Y?", I'm expected to give a reasoned answer with trade-offs, not "let me ask"
- I write the runbooks and architectural decision records (ADRs) that junior engineers reference during incidents
- I'm the person ops teams call when something's broken and nobody knows why

**Cross-Questions**:
1. "Give me an example of a technical decision you made at SDE-3 level that you had to get buy-in for from non-technical stakeholders."
   > Think: the decision to build the Excel pipeline as a separate service (cost: new infrastructure, ops overhead). Or the Exotel integration (cost: API contract, dependency on third party). Frame it as: here's the problem, here are the options, here's the cost-benefit of my recommendation, here's the risk of not doing it.

2. "You mentioned mentoring junior developers. What's the hardest part of mentoring?"
   > The hardest part: letting them make mistakes that you could prevent. If you jump in and fix every problem, they don't learn. But if you let them ship broken code to production, there's real impact. The balance: let them make decisions on non-critical paths, review their work before it touches critical systems, explain why their approach would fail rather than just telling them the right answer.

---

**Q2: "You solely manage the AJ Staffing backend. How have you structured the codebase so that someone else could take over if needed?"**

**Your Answer**:
Operability is a feature I've prioritized because I know I'm the single point of knowledge:

**Documentation**:
- `README.md` per service: setup, dependencies, how to run locally, how to deploy
- Runbook per common incident type: "Celery queue backed up" → check worker pods, check Redis memory, restart workers. "gRPC service returning INTERNAL" → check New Relic for the trace, check PostgreSQL connection count
- Architecture diagram (draw.io) showing service interactions, which queues exist, what each consumer does

**Observability**:
- New Relic alerts configured with meaningful names — an on-call engineer who doesn't know the codebase should be able to read the alert and know which service is affected
- Log structure is consistent: every log line has `service`, `org_id`, `employee_id` (where relevant) — makes `grep` and log queries fast

**Code clarity**:
- No clever hacks without comments explaining why. Complex Celery task chains have docstrings explaining the workflow
- gRPC service names match what the business calls the operation — `CreateAnnouncement` not `CreateRecord`

**Cross-Questions**:
1. "If you were hit by a bus tomorrow, what would be the first thing to break and how long before someone fixed it?"
   > Honest answer expected. The first thing: an incident that requires understanding the relationship between the staffing service, notification hub, and Exotel calling schedule — no single runbook covers this end-to-end. Time to fix: a senior engineer could navigate it in 2–4 hours with logs and the README. An incident requiring code changes: could take a day for someone unfamiliar with the codebase.

2. "What would you do differently if you were starting the staffing service today, knowing you'd be the only engineer for 6 years?"
   > Invest earlier in observability: distributed tracing from day one (OpenTelemetry). Better documentation culture. Avoid the monolith — extract services earlier so the blast radius of any one change is smaller. More aggressive testing: integration tests that run against a real DB (not mocks) would have caught several production bugs earlier.

---

**Q3: "Tell me about a time you had a technical disagreement with a product manager or another engineer. How did you resolve it?"**

**Framework**:
- Disagreement with PM: "PM wanted feature X delivered in 1 week. I assessed it would take 3 weeks to do correctly. I showed them the risk of doing it in 1 week (specific failure modes), proposed a 1-week MVP with clear limitations, and a 3-week full implementation plan. PM chose the MVP with understanding of limitations."
- Disagreement with engineer: "Colleague proposed using MongoDB for the employee records because it's flexible. I argued for PostgreSQL because employee records have strong relational structure (salary → employee → org), and MongoDB would complicate joins and transactions. I did a written trade-off doc, shared it, we discussed. They raised a valid point about schema flexibility for custom fields — we compromised: PostgreSQL for core records, MongoDB for custom template definitions."

**What interviewers look for**: You can articulate technical trade-offs clearly to non-technical people. You disagree respectfully and with evidence, not opinion. You can be persuaded when the other person makes a valid point.

---

## 20. OBSERVABILITY + TESTING + CI/CD

*Cross-cutting concerns that separate a good engineer from a great one.*

---

**Q1: "How do you test a Celery task that calls an external API (Employee Management API)?"**

**Your Answer**:
Three levels of testing:

**Unit test — mock the external call**:
```python
from unittest.mock import patch

@patch('app.worker.tasks.employee_api.create_employee')
def test_process_upload_row_success(mock_create):
    mock_create.return_value = {"id": "emp_123", "status": "created"}
    
    result = process_upload_row(
        row={"name": "John", "email": "john@org.com"},
        template=test_template
    )
    
    assert result.status == "SUCCESS"
    mock_create.assert_called_once_with({"name": "John", "email": "john@org.com"})
```

**Integration test — real Celery, real DB, mock only the external HTTP call**:
```python
@pytest.mark.celery(task_always_eager=True)  # Run task synchronously
@patch('httpx.AsyncClient.post')
def test_upload_job_end_to_end(mock_http, celery_worker):
    mock_http.return_value = Mock(status_code=200, json={"id": "emp_123"})
    
    # Create real job in test DB
    job = Job.objects.create(status="IN_QUEUE", file_url="s3://test/file.xlsx")
    
    # Run actual Celery task
    process_upload.apply(args=[str(job.id)])
    
    job.refresh_from_db()
    assert job.status == "SUCCESS"
```

**Contract test — verify your API call format matches what Employee API expects**:
Use Pact or record/replay (VCR.py) — record a real API response in dev, replay it in tests. Detects API drift when the Employee service changes their contract.

**Cross-Questions**:
1. "Your Excel upload has a dry-run mode and an actual mode using the same code path. How do you test that dry-run doesn't mutate state?"
   > Assert that no external API was called during dry-run (`mock_create.assert_not_called()`). Assert that the DB has no new employee records after dry-run. Assert that S3 has no new files uploaded after dry-run. Integration test that runs dry-run then queries every side-effect source.

2. "You test with `task_always_eager=True` which runs Celery synchronously. What production behaviors does this miss?"
   > It misses: actual serialization/deserialization (task args are passed in-process, not serialized to JSON → Redis → deserialized). This hides bugs where the task args contain non-serializable objects. Also misses: retry behavior (eager mode doesn't retry on failure). And misses: concurrency races (multiple workers consuming the same task). For these: run tests against a real Redis/RabbitMQ in a Docker Compose test environment.

---

**Q2: "How do you trace a request through your microservices — from the original API call to the notification sent?"**

**Your Answer**:
Current state: partial observability. New Relic instruments each service independently but doesn't stitch together cross-service traces.

To do it properly with distributed tracing:
```python
# FastAPI service (producer)
from opentelemetry import trace
from opentelemetry.propagate import inject

tracer = trace.get_tracer(__name__)

@app.post("/upload")
async def upload_excel(file: UploadFile):
    with tracer.start_as_current_span("upload_excel") as span:
        span.set_attribute("org_id", org_id)
        
        # Inject trace context into Celery task headers
        headers = {}
        inject(headers)  # adds traceparent, tracestate headers
        
        task = process_upload.apply_async(
            args=[job_id],
            headers={"tracing": headers}
        )
```

```python
# Celery worker (consumer) — extract and continue trace
def process_upload(self, job_id: str):
    # Extract trace context from headers
    ctx = extract(self.request.headers.get("tracing", {}))
    with tracer.start_as_current_span("process_upload", context=ctx):
        # This span is a child of the API span
        ...
```

With OpenTelemetry + Jaeger, you'd see a flame graph: `upload_excel → process_upload → employee_api.create → notification_hub.send_otp` as a single trace.

**Cross-Questions**:
1. "Without distributed tracing today, how do you debug a production issue where an upload job succeeded but the employee didn't receive the notification?"
   > Manual trace: find the job ID from the user's report → query MongoDB for job record → find which rows were processed → check notification hub DB for `task` records with that org_id around that time → check if the OTP task was created → check delivery status in `vendor_event` table. This is feasible but takes 30–45 minutes vs. 2 minutes with a flame graph. This is exactly the gap that justifies adding distributed tracing.

---

**Q3: "How do you ensure code quality across 6+ microservices when you're often the only engineer?"**

**Your Answer**:
Process compensates for team size:
- **Pre-commit hooks**: black (Python formatter), isort (import sorter), flake8 (linter), mypy (type checker). Fast feedback before even pushing.
- **CI gates**: Tests must pass, linting must pass. Azure Pipelines blocks merge if CI fails.
- **Type hints everywhere**: Python type hints caught a class of bugs where I was passing the wrong argument type to a function — especially useful across service boundaries.
- **Code review for myself**: For significant changes, I write the PR description as if explaining to a colleague — this forces me to articulate why, not just what. Sometimes I catch my own bugs this way.
- **Integration tests**: For each service, a test suite that runs against a real database and mocked external APIs. These catch "it works on my machine" bugs.

---

## 21. SCENARIO-BASED QUESTIONS

*Senior engineers are tested with realistic scenarios, not just "explain X."*

---

**Scenario 1: Production is down. 3am.**

**Interviewer**: "Your monitoring alerts at 3am — the staffing API is returning 500s. Walk me through exactly what you do."

**Your Answer**:
```
0:00 — Alert fires. Acknowledge in PagerDuty to stop escalation.

0:01 — Check dashboard: which endpoints are 500ing?
        Is it all endpoints or specific ones?
        Is it all orgs or specific org?

0:03 — Check recent deploys: was anything deployed in the last hour?
        If yes, rollback first, ask questions later.
        kubectl rollout undo deployment/api-staffing

0:05 — If no recent deploy, check logs:
        kubectl logs -l app=api-staffing --since=15m | grep ERROR
        Look for: DB connection errors, timeout errors, 3rd party API errors

0:07 — Check DB health:
        PostgreSQL connections: SELECT count(*) FROM pg_stat_activity;
        Slow queries: SELECT query, duration FROM pg_stat_activity
                      WHERE duration > interval '5 seconds';

0:10 — Check downstream services:
        Is notification hub responding? (gRPC health check)
        Is authorization service responding?
        Is RabbitMQ healthy?

0:15 — Mitigation:
        If DB connections exhausted: restart PgBouncer
        If specific endpoint: disable or rate-limit it
        If external dependency: enable fallback mode if exists

0:30 — Write brief incident note in Slack #incidents
        "API returning 500s since 3am. Root cause: X. Mitigation: Y. Full RCA tomorrow."
```

**Cross-Questions**:
1. "During the incident, users are actively trying to log in and failing. How do you communicate status to them?"
   > Status page update (if you have one — statuspage.io). Slack/email notification to key account contacts if enterprise customers are affected. The communication is the ops team's job — your job is to get the system back up. But you need to give the ops team accurate information: "ETA for fix is 30 minutes" vs "unknown."

2. "Root cause turned out to be a missing database index on a 50M row table — a query that used to be fast started causing full table scans after data grew. How do you fix this without taking downtime?"
   > `CREATE INDEX CONCURRENTLY idx_employee_org_id ON employee(org_id, status)` — CONCURRENTLY doesn't lock the table. Can run in production. Monitor `pg_stat_progress_create_index` to track progress. The risk: `CONCURRENTLY` takes longer and uses more I/O than regular index creation. Do it during low-traffic hours if possible.

---

**Scenario 2: Unexpected scale.**

**Interviewer**: "A large enterprise client onboards with 200,000 employees at once. Your system was designed for orgs of up to 50,000. Walk me through what breaks and how you handle it."

**Your Answer**:
What breaks, layer by layer:

**Excel upload**: A 200K-row Excel file is ~20MB. openpyxl loading it into memory: ~200MB per worker (openpyxl's in-memory representation is ~10x file size). If your workers have 512MB memory limit, this OOMs the worker. Fix: use openpyxl `read_only=True` (streaming mode, constant memory), process the file from S3 in chunks.

**Database — bulk insert**: `bulk_create(200,000 EmployeeAnnouncement records, batch_size=1000)` = 200 DB round-trips in a single transaction. This transaction holds locks for minutes. Fix: break into multiple transactions, process in chunks with separate transactions.

**Celery workers**: One task processing 200K rows for 2+ hours. Other orgs' uploads are starved. Fix: split the large job into smaller chunk-tasks using Celery chord. Each chunk processes 5,000 rows, 40 parallel chunks, complete in parallel.

**Notification fan-out**: After bulk create, send 200K push notifications. A single Celery task trying to batch 200K notifications overwhelms the notification hub. Fix: Celery group with 200 tasks of 1,000 notifications each, rate-limited.

**PostgreSQL**: 200K rows suddenly inserted into `employee` table. If you have triggers, indexes being maintained, or FK constraint checks — each row add triggers work. Fix: disable indexes before bulk insert, rebuild after, wrap in COPY command.

**Cross-Questions**:
1. "You handled it this time by splitting into chunks. But how do you design the system upfront to handle arbitrary scale without knowing the max org size?"
   > Chunk-based processing from day one — never write a task that processes "all rows" synchronously. Always: fetch page N of 1000, process, enqueue page N+1. The system naturally handles 1,000 or 1,000,000 rows with the same code path.

2. "The client wants to know: when will my 200,000 employees be ready in the system? How do you give an accurate ETA?"
   > Progress tracking: total rows / rows processed = % complete. ETA = (elapsed time / % complete) * remaining %. Expose this via the WebSocket progress stream. The challenge: ETA is inaccurate early (first 5% is slow as system warms up) and assumes constant processing speed (doesn't account for DB slowdowns, API rate limits).

---

**Scenario 3: Security incident.**

**Interviewer**: "You discover that a colleague accidentally pushed a `.env` file with production DB credentials to a public GitHub repo 3 days ago. Walk me through your response."

**Your Answer**:
```
Immediate (next 60 minutes):
1. Rotate the DB password immediately — even before assessing exposure
   ALTER USER staffing_db PASSWORD 'new_random_password_128_chars';
   Update Kubernetes Secret, restart pods with new credentials.

2. Rotate all other secrets in that .env file:
   - JWT signing secret → invalidates all existing tokens (users re-login)
   - AWS credentials → rotate IAM access key
   - API keys (Gupshup, SendGrid, etc.)
   - Google service account → generate new key, revoke old

Assessment (next 2 hours):
3. Check if the repo was actually public or just accidentally committed
   (private repo → lower risk, but still rotate)

4. Check GitHub for forks or stars added in the last 3 days
   (indicates someone found it)

5. Audit PostgreSQL access logs for the last 3 days:
   SELECT * FROM pg_stat_activity WHERE usename = 'staffing_db'
   and any logs of queries from unexpected IP addresses

6. Check AWS CloudTrail for API calls using the leaked IAM key

7. If any suspicious access: treat as breach, escalate to management and legal

Prevention:
- Add .env to .gitignore (it was already there — how did this happen? git add -f?)
- Add a pre-commit hook: git-secrets scans for credential patterns before allowing commit
- Use AWS Secrets Manager instead of .env files — secrets never touch the filesystem
```

**Cross-Questions**:
1. "Rotating the JWT secret invalidates all active sessions. It's 2pm on a Monday — all users get logged out. How do you mitigate this?"
   > For JWT: support two valid secrets during rotation (old and new). Accept tokens signed with either secret for a grace period (30 minutes). After grace period, reject old secret. This allows active users to finish their session naturally, while new tokens use the new secret.

2. "You mentioned checking PostgreSQL access logs. Does your PostgreSQL instance have logging enabled for all queries?"
   > Default PostgreSQL: logs only errors and slow queries. For security audit: `log_connections=on`, `log_disconnections=on`, `pgaudit` extension for per-statement logging. But full query logging on a high-write system is expensive (I/O overhead). Compromise: log all DDL (schema changes) and certain sensitive queries (SELECT on salary, payment tables).

---

*Prepared April 2026 | For Akshay Kumar's backend engineering interviews*
*All question flows simulate real interviewer behavior: resume claim → open question → your answer → probe*

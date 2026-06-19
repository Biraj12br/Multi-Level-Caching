2-Level Cache Design
Overview

The 2-Level Cache Design project demonstrates a high-performance caching architecture using Flask, Redis, and an in-memory local cache to reduce database latency and improve application throughput.
The application stores biller information in MYSQL DB and retrieves data through a two-layer caching mechanism before accessing the database.

Architecture
                Client
                   │
                   ▼
            Flask Application
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   L1 Cache (Local)    L2 Cache (Redis)
          │                 │
          └────────┬────────┘
                   ▼
              MYSQL Database

Cache Flow

1. Request Received
A client requests employee data through the Flask REST API.

2. Check L1 Cache
The application first checks the local in-memory cache.
If found:

Return immediately.
Lowest latency.
No network call.

3. L1 Cache Miss
If data is absent in L1:

Query Redis (L2 Cache).

4. L2 Cache Hit
If Redis contains the data:
Return data.
Repopulate L1 cache.
Avoid database access.

5. L2 Cache Miss
If Redis also misses:

Query MYSQLDB.
Store response in Redis.
Store response in Local Cache.
Return response.

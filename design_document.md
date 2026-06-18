# EBPP Solution — Flask 2-Level Cache Design Document

## 1. Overview
This document describes the design for a Python Flask application that demonstrates a 2-level caching strategy using:
- In-memory cache (Level 1)
- Redis cache (Level 2)
- MySQL database as the source of truth

The application exposes a REST API to fetch tenant-specific rules stored in a MySQL table named `biller_master_data`.

## 2. Goals
- Build a Flask-based REST API: `/getRules/<tenantName>`
- Store tenant rule metadata in MySQL
- Implement centralized error handling
- Implement centralized logging
- Use Docker for MySQL and Redis dependencies
- Show two-level caching with different TTL values

## 3. Application Architecture

### 3.1 Components
- Flask app: HTTP API server
- MySQL: relational data store with a `biller_master_data` table
- Redis: distributed cache for Level 2
- In-memory cache: process-local cache for Level 1
- Docker compose: containerize MySQL and Redis

### 3.2 Request flow
1. Client calls `/getRules/<tenantName>`
2. Application checks Level 1 (in-memory cache)
3. If not found, it checks Level 2 (Redis)
4. If still not found, it queries MySQL
5. Result is written to Redis and the in-memory cache
6. Response returned to client

## 4. Data Model

### 4.1 Table: `biller_master_data`
Columns:
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `tenant_name` VARCHAR(255) NOT NULL
- `biller_name` VARCHAR(255) NOT NULL
- `rule_name` VARCHAR(255) NOT NULL
- `rule_value` VARCHAR(255) NOT NULL
- `created_at` DATETIME NOT NULL
- `created_by` VARCHAR(255) NOT NULL
- `modified_at` DATETIME NULL
- `modified_by` VARCHAR(255) NULL

### 4.2 Example rows
- Row 1: `1`, `Jio`, `GST_No`, `12345`, `2026-06-07 10:00:00`, `admin`, `2026-06-07 10:00:00`, `admin`
- Row 2: `2`, `Airtel`, `GST_No`, `5463`, `2026-06-07 10:05:00`, `admin`, `2026-06-07 10:05:00`, `admin`

> The API should return the rule row for the requested tenant name.

## 5. API Design

### 5.1 Endpoint
- `GET /getRules/<tenantName>`

### 5.2 Behavior
- Validate `tenantName`
- Return tenant-specific rules from cache or database
- If tenant not found, return `404 Not Found`

### 5.3 Response format
```json
{
  "tenant_name": "Jio",
  "biller_name": "Jio",
  "rule_name": "GST_No",
  "rule_value": "12345",
  "created_at": "2026-06-07T10:00:00",
  "created_by": "admin",
  "modified_at": "2026-06-07T10:00:00",
  "modified_by": "admin"
}
```

### 5.4 Example usage
- Request: `GET /getRules/Jio`
- Response: rule data for tenant `Jio`

## 6. Cache Design

### 6.1 Levels
- Level 1: In-memory cache inside the Flask process
  - Very short TTL, e.g. 10–30 seconds
  - Fastest access
  - Ideal for highly repeated calls within a single instance
- Level 2: Redis cache
  - High TTL, e.g. 24 hours or more
  - Shared across application instances
  - Acts as a second cache layer before hitting MySQL
- Level 3: MySQL database
  - Source of truth
  - Used when both cache layers miss

### 6.2 Proposed cache flow
1. Request arrives
2. Check in-memory cache for key `tenant:<tenantName>`
3. If missed, check Redis for same key
4. If missed, query MySQL
5. Write result to Redis with a long TTL
6. Write result to in-memory cache with a short TTL
7. Return result

### 6.3 TTL recommendations
- In-memory cache TTL: `10 seconds` to `30 seconds`
- Redis cache TTL: `12 hours` to `24 hours` or configurable via environment variable

### 6.4 Cache invalidation strategy
- Use TTL expiry
- If rules may change frequently, consider invalidating both caches when updates occur
- For this demo, TTL-based expiry is sufficient

## 7. Cache library options for Python

### 7.1 In-memory cache libraries
- `cachetools`
  - Provides TTLCache, LRUCache, LFUCache
  - Simple and widely used
- `functools.lru_cache`
  - Built-in Python memoization
  - Not TTL-based without wrapper
- `cacheout`
  - Simple in-memory cache with TTL support
- `dogpile.cache`
  - Advanced caching support with expiration

### 7.2 Redis cache libraries
- `redis-py` (`redis`)
  - Official Redis client
- `Flask-Caching`
  - Works with Redis backends and in-memory backends
- `aioredis` or `redis.asyncio`
  - For async Flask or async frameworks
- `django-redis` (not applicable here, but similar architecture)

### 7.3 Recommended combination for this app
- In-memory: `cachetools.TTLCache`
- Redis: `redis` client directly or via `Flask-Caching`

## 8. Dependency setup with Docker

### 8.1 Why Docker
- Ensures MySQL and Redis are available consistently
- Avoids local environment dependency mismatches
- Simplifies onboarding and cleanup

### 8.2 Docker Compose services
- `mysql`
  - Image: `mysql:8.0`
  - Environment: `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`
  - Port: `3306`
- `redis`
  - Image: `redis:7`
  - Port: `6379`

### 8.3 Development notes
- Python is local, so only MySQL and Redis run in containers
- Flask app connects to `localhost:3306` and `localhost:6379`
- Use Docker volumes to persist MySQL data

## 9. Centralized error handling

### 9.1 Flask error handler strategy
- Use Flask `errorhandler` or `register_error_handler`
- Catch application errors centrally
- Return consistent JSON error responses

### 9.2 Error structure
```json
{
  "error": {
    "type": "NotFoundError",
    "message": "Tenant Jio not found",
    "status": 404
  }
}
```

### 9.3 Suggested exception classes
- `AppError` — base exception with HTTP status
- `NotFoundError` — 404
- `BadRequestError` — 400
- `CacheError` — 500
- `DatabaseError` — 500

### 9.4 Example error handler
- Log exception details
- Return JSON payload with status code
- Include an application-specific error code/message

## 10. Centralized logging

### 10.1 Logging goals
- Record application startup
- Log API requests and responses
- Log cache hits and misses
- Log database queries and failures
- Capture exceptions with stack traces

### 10.2 Recommended logging setup
- Use Python `logging` module
- Configure a structured formatter
- Route logs to console and optionally a file
- Set the logger at module/application level

### 10.3 Logger configuration example
- `logger = logging.getLogger(__name__)`
- `logging.basicConfig(level=logging.INFO, format=...)`
- Add handlers for `StreamHandler`
- Use `app.logger` for Flask integration

### 10.4 Logging events
- Startup: `Application started, loading config`
- Cache: `Level1 cache hit`, `Level1 cache miss`, `Redis cache hit`, `Redis cache miss`
- DB: `Querying MySQL for tenant: Jio`
- Errors: log full exception traceback

## 11. Application modules and structure

### 11.1 Suggested file layout
- `app.py` — Flask application entrypoint
- `config.py` — configuration values, cache TTLs, DB/Redis URLs
- `models.py` — database model definitions or SQL helper functions
- `cache.py` — cache initialization and helpers
- `services.py` — business logic for rule fetching and cache flow
- `errors.py` — custom exceptions and error handlers
- `logging_setup.py` — centralized logger configuration
- `docker-compose.yml` — MySQL and Redis containers
- `requirements.txt` — Python dependencies

### 11.2 Module responsibilities
- `app.py`
  - Initialize Flask
  - Register routes and error handlers
  - Start app
- `services.py`
  - Implement `get_rules_for_tenant(tenantName)`
  - Manage cache lookup order
- `cache.py`
  - Configure in-memory `TTLCache`
  - Configure Redis client
- `models.py`
  - Query MySQL using `mysql-connector-python`, `pymysql`, or `SQLAlchemy`
- `errors.py`
  - Define exception hierarchy and handler registration
- `logging_setup.py`
  - Configure `logging` before app startup

## 12. Sample technical design decisions

### 12.1 Flask + SQLAlchemy or raw connector
- Use `SQLAlchemy` for maintainability and mapping convenience
- Or use `pymysql` / `mysql-connector-python` for minimal example

### 12.2 Caching implementation
- In-memory: `cachetools.TTLCache(maxsize=128, ttl=15)`
- Redis: `redis.Redis(host=..., port=..., db=0)`
- Cache keys: `rules:tenant:<tenantName>`

### 12.3 Response caching details
- Store serialized JSON in Redis
- Store Python object or serialized payload in in-memory cache
- Deserialize when returning response

## 13. Deployment and run instructions

### 13.1 Docker compose startup
- `docker compose up -d`
- Ensure MySQL and Redis are healthy

### 13.2 Application startup
- Install Python deps: `pip install -r requirements.txt`
- Run Flask app: `python app.py`

### 13.3 Testing the API
- `curl http://localhost:5000/getRules/Jio`
- `curl http://localhost:5000/getRules/Airtel`

## 14. Future enhancements
- Add `POST /rules` or update endpoints to refresh cache
- Add authentication/authorization
- Add Redis cache invalidation hooks on data changes
- Add metrics for hits/misses and response time
- Add schema validation for API input/output

## 15. Notes
- The application is designed for demonstration and learning.
- TTL values should be configurable rather than hard-coded.
- Docker dependency isolation means only MySQL and Redis require containers.

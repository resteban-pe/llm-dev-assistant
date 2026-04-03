# llm-dev-assistant

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![Claude API](https://img.shields.io/badge/Claude-claude--sonnet--4--6-blueviolet?logo=anthropic&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

AI-powered microservice that generates production-ready Java code — Spring Boot project structure, JUnit 5 tests, OpenAPI 3.0 documentation, and Clean Architecture reviews — via REST endpoints backed by the Claude API.

---

## Architecture

```
Client Request
     │
     ▼
┌─────────────────────────────┐
│        FastAPI (port 8083)  │
│  ┌──────────┐ ┌──────────┐  │
│  │ /generate│ │ /review  │  │
│  └────┬─────┘ └────┬─────┘  │
│       │            │        │
│  ┌────▼────────────▼─────┐  │
│  │  System Prompt (.md)  │  │
│  └──────────┬────────────┘  │
└─────────────┼───────────────┘
              │
              ▼
      Claude API (claude-sonnet-4-6)
              │
              ▼
     { "result": "...", "tokens_used": N }
```

---

## Endpoints

All endpoints are prefixed with `/api/v1`.

| Method | Path | Description | Input (key fields) |
|--------|------|-------------|-------------------|
| `GET` | `/` | Health check | — |
| `POST` | `/api/v1/generate/structure` | Generates a Clean Architecture Spring Boot folder tree + class table | `project_name`, `domain_description` |
| `POST` | `/api/v1/generate/tests` | Generates a complete JUnit 5 + Mockito test class (happy path, error cases, edge cases) | `class_name`, `java_class` |
| `POST` | `/api/v1/generate/docs` | Generates a valid OpenAPI 3.0 YAML block with schemas, responses and examples | `api_title`, `endpoints: []` |
| `POST` | `/api/v1/review/code` | Reviews Java code against Clean Architecture and SOLID principles; returns a severity table (HIGH/MEDIUM/LOW) | `code`, `context` |

All endpoints return:
```json
{
  "result": "<generated content>",
  "tokens_used": 1024
}
```

Interactive docs available at `http://localhost:8083/docs`.

---

## Quick Start

### Option A — Docker (recommended)

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd llm-dev-assistant

# 2. Configure your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Build and run
docker compose up -d

# 4. Verify
curl http://localhost:8083/
# {"service":"llm-dev-assistant","status":"running","version":"1.0.0"}
```

### Option B — Local (Python 3.11+)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Run
uvicorn app.main:app --reload --port 8083

# 4. Verify
curl http://localhost:8083/
```

---

## Example — POST /api/v1/generate/structure

**Request:**
```bash
curl -s -X POST http://localhost:8083/api/v1/generate/structure \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "payment-service",
    "domain_description": "sistema de pagos con usuarios y transacciones"
  }'
```

**Response** (`tokens_used: 2845`):
```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── paymentservice/
│   │           ├── domain/
│   │           │   ├── model/
│   │           │   │   ├── User.java
│   │           │   │   ├── Transaction.java
│   │           │   │   ├── Payment.java
│   │           │   │   ├── Money.java                  ← Value Object
│   │           │   │   ├── TransactionStatus.java      ← Enum
│   │           │   │   └── PaymentMethod.java          ← Enum
│   │           │   ├── port/
│   │           │   │   ├── in/
│   │           │   │   │   ├── CreateUserUseCase.java
│   │           │   │   │   ├── GetUserUseCase.java
│   │           │   │   │   ├── ProcessPaymentUseCase.java
│   │           │   │   │   ├── GetTransactionUseCase.java
│   │           │   │   │   └── ListTransactionsByUserUseCase.java
│   │           │   │   └── out/
│   │           │   │       ├── UserRepositoryPort.java
│   │           │   │       ├── TransactionRepositoryPort.java
│   │           │   │       └── PaymentGatewayPort.java
│   │           │   └── service/
│   │           │       ├── UserService.java
│   │           │       ├── PaymentService.java
│   │           │       └── TransactionService.java
│   │           ├── application/
│   │           │   └── dto/
│   │           │       ├── request/
│   │           │       │   ├── CreateUserRequest.java
│   │           │       │   ├── ProcessPaymentRequest.java
│   │           │       │   └── ListTransactionsRequest.java
│   │           │       └── response/
│   │           │           ├── UserResponse.java
│   │           │           ├── TransactionResponse.java
│   │           │           └── PaymentResponse.java
│   │           ├── infrastructure/
│   │           │   ├── persistence/
│   │           │   │   ├── entity/
│   │           │   │   │   ├── UserJpaEntity.java
│   │           │   │   │   ├── TransactionJpaEntity.java
│   │           │   │   │   └── PaymentJpaEntity.java
│   │           │   │   ├── repository/
│   │           │   │   │   ├── UserJpaRepository.java
│   │           │   │   │   ├── TransactionJpaRepository.java
│   │           │   │   │   └── PaymentJpaRepository.java
│   │           │   │   ├── adapter/
│   │           │   │   │   ├── UserRepositoryAdapter.java
│   │           │   │   │   ├── TransactionRepositoryAdapter.java
│   │           │   │   │   └── PaymentGatewayAdapter.java
│   │           │   │   └── mapper/
│   │           │   │       ├── UserPersistenceMapper.java
│   │           │   │       ├── TransactionPersistenceMapper.java
│   │           │   │       └── PaymentPersistenceMapper.java
│   │           │   ├── web/
│   │           │   │   ├── controller/
│   │           │   │   │   ├── UserController.java
│   │           │   │   │   ├── PaymentController.java
│   │           │   │   │   └── TransactionController.java
│   │           │   │   ├── mapper/
│   │           │   │   │   ├── UserWebMapper.java
│   │           │   │   │   ├── PaymentWebMapper.java
│   │           │   │   │   └── TransactionWebMapper.java
│   │           │   │   └── exception/
│   │           │   │       ├── GlobalExceptionHandler.java
│   │           │   │       ├── UserNotFoundException.java
│   │           │   │       ├── TransactionNotFoundException.java
│   │           │   │       └── PaymentProcessingException.java
│   │           │   └── config/
│   │           │       ├── UseCaseConfig.java
│   │           │       ├── PersistenceConfig.java
│   │           │       └── PaymentGatewayConfig.java
│   │           └── PaymentServiceApplication.java
│   └── resources/
│       ├── application.yml
│       ├── application-dev.yml
│       └── application-prod.yml
└── test/
    └── java/
        └── com/
            └── paymentservice/
                ├── domain/service/
                │   ├── UserServiceTest.java
                │   ├── PaymentServiceTest.java
                │   └── TransactionServiceTest.java
                ├── infrastructure/
                │   ├── persistence/adapter/
                │   │   ├── UserRepositoryAdapterTest.java
                │   │   └── TransactionRepositoryAdapterTest.java
                │   └── web/controller/
                │       ├── UserControllerTest.java
                │       ├── PaymentControllerTest.java
                │       └── TransactionControllerTest.java
                └── PaymentServiceApplicationTest.java
```

| Class | Layer | Responsibility |
|-------|-------|----------------|
| `User` | domain/model | Entity representing a payment system user with identity data |
| `Transaction` | domain/model | Immutable record of a financial movement between parties |
| `Payment` | domain/model | Encapsulates payment intent before becoming a confirmed transaction |
| `Money` | domain/model | Value Object representing a monetary amount with currency, enforcing invariants |
| `TransactionStatus` | domain/model | Enum: PENDING, COMPLETED, FAILED, REVERSED |
| `PaymentMethod` | domain/model | Enum: CARD, BANK_TRANSFER, WALLET |
| `CreateUserUseCase` | domain/port/in | Use case interface for registering a new user |
| `GetUserUseCase` | domain/port/in | Use case interface for querying a user by ID |
| `ProcessPaymentUseCase` | domain/port/in | Use case interface orchestrating payment validation and execution |
| `GetTransactionUseCase` | domain/port/in | Use case interface for retrieving a transaction by ID |
| `ListTransactionsByUserUseCase` | domain/port/in | Use case interface for fetching a user's transaction history |
| `UserRepositoryPort` | domain/port/out | Abstracts persistence operations on the User entity |
| `TransactionRepositoryPort` | domain/port/out | Abstracts persistence operations on the Transaction entity |
| `PaymentGatewayPort` | domain/port/out | Abstracts communication with the external payment processor |
| `UserService` | domain/service | Implements `CreateUserUseCase` and `GetUserUseCase` with business rules |
| `PaymentService` | domain/service | Implements `ProcessPaymentUseCase` orchestrating validation, gateway and persistence |
| `TransactionService` | domain/service | Implements transaction query and listing use cases |

---

## Prompt Library

Each endpoint is powered by a dedicated system prompt in `prompts/`:

| File | Role | Output format |
|------|------|---------------|
| `generate_structure.md` | Senior Java architect specialized in Clean Architecture | ASCII folder tree + markdown class table |
| `generate_tests.md` | Senior QA engineer specialized in Spring Boot testing | Complete Java test class (JUnit 5 + Mockito + AssertJ) |
| `generate_docs.md` | Technical writer specialized in REST APIs and OpenAPI | Valid YAML OpenAPI 3.0 block |
| `review_code.md` | Senior software architect focused on Clean Architecture and SOLID | Executive summary + severity table + SOLID checklist |

These prompts were developed as part of the [ai-dev-prompts-library](https://github.com/resteban-pe) portfolio project and are reused here as microservice system prompts.

---

## Project Structure

```
llm-dev-assistant/
├── app/
│   ├── config.py          ← API key, shared Claude client, model constants
│   ├── main.py            ← FastAPI app, CORS, router registration
│   └── routers/
│       ├── generate.py    ← /generate/structure, /generate/tests, /generate/docs
│       └── review.py      ← /review/code
├── prompts/
│   ├── generate_structure.md
│   ├── generate_tests.md
│   ├── generate_docs.md
│   └── review_code.md
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Author

**Roosevelt Esteban Torres**
[github.com/resteban-pe](https://github.com/resteban-pe) · [linkedin.com/in/roosevelt-esteban](https://linkedin.com/in/roosevelt-esteban)

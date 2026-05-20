# Flowspace

A production-ready multi-tenant SaaS project management platform built with FastAPI, React, PostgreSQL, and deployed on AWS. Think of it as a Jira/Trello alternative with full team management, billing, and cloud deployment.

## Live Demo

- Frontend: http://flowspace-frontend-9d099811.s3-website.ap-south-1.amazonaws.com
- API Docs: http://13.235.218.59:8000/docs

## Features

- Multi-tenant architecture — each company gets its own isolated workspace at signup
- Kanban board with drag and drop task management
- Team management with role-based access control (Admin / Member)
- Project visibility control — assign projects to specific teams
- Task management — priority levels, due dates, assignees, descriptions
- Billing and subscription plans via Razorpay (Free / Pro / Enterprise)
- JWT authentication with access and refresh tokens
- File storage via AWS S3
- Workspace settings and member invite system

## Tech Stack

### Backend
- **FastAPI** — async Python web framework
- **PostgreSQL** — primary relational database
- **SQLAlchemy** — async ORM with Alembic migrations
- **MongoDB Atlas** — comments and activity feeds
- **Redis** — caching and token management
- **Razorpay** — payment processing
- **Pydantic** — data validation and serialization

### Frontend
- **React 18** — UI framework with Vite
- **TanStack Query** — server state management and caching
- **Zustand** — global client state
- **Tailwind CSS** — utility-first styling
- **dnd-kit** — drag and drop for kanban board
- **Axios** — HTTP client with JWT interceptors

### Infrastructure
- **AWS EC2 t3.micro** — application server
- **AWS RDS PostgreSQL** — managed database
- **AWS ElastiCache Redis** — managed Redis
- **AWS S3** — static frontend hosting and file uploads
- **Terraform** — infrastructure as code (deploy and destroy with one command)

## Architecture

```
Browser (React)
      |
AWS S3 (Static Hosting)
      |
      | API calls
      |
AWS EC2 (FastAPI + Uvicorn + Nginx)
      |
      |---> AWS RDS (PostgreSQL)
      |---> AWS ElastiCache (Redis)
      |---> MongoDB Atlas
      |---> AWS S3 (File uploads)
```

## Local Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker and Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/SlingggShottt/flowspace.git
cd flowspace
```

### 2. Backend setup

```bash
# Create and activate virtual environment
python3 -m venv flowspace-venv
source flowspace-venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env and fill in your values
```

### 3. Start databases with Docker

```bash
docker compose up -d
```

This starts PostgreSQL, MongoDB, and Redis locally.

### 4. Run database migrations

```bash
export PYTHONPATH=$(pwd)
alembic upgrade head
```

### 5. Start the backend server

```bash
uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

### 6. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend is available at `http://localhost:5173`

## Environment Variables

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| APP_NAME | Application name |
| APP_ENV | development or production |
| SECRET_KEY | JWT signing secret |
| DATABASE_URL | PostgreSQL connection string |
| MONGODB_URL | MongoDB Atlas connection string |
| MONGODB_DB_NAME | MongoDB database name |
| REDIS_URL | Redis connection string |
| AWS_REGION | AWS region |
| S3_BUCKET_NAME | S3 bucket for file uploads |
| RAZORPAY_KEY_ID | Razorpay API key ID |
| RAZORPAY_KEY_SECRET | Razorpay API secret |

## AWS Deployment with Terraform

Infrastructure is fully managed with Terraform. One command to deploy, one command to destroy.

### Prerequisites

- AWS account with free tier
- AWS CLI configured (`aws configure`)
- Terraform installed

### Deploy

```bash
cd infrastructure
terraform init
terraform apply
```

This creates:
- VPC with public and private subnets
- EC2 t3.micro instance (free tier)
- RDS PostgreSQL t3.micro (free tier)
- ElastiCache Redis t3.micro (free tier)
- S3 buckets for frontend and uploads
- Security groups and IAM roles
- Elastic IP (static IP that never changes)

### Upload frontend after deploy

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://YOUR_FRONTEND_BUCKET --delete
```

### Destroy to save credits

```bash
cd infrastructure
terraform destroy
```

## Running Tests

```bash
# Create test database first
docker exec -it flowspace-postgres psql -U flowspace -c "CREATE DATABASE flowspace_test;"

# Run tests
export PYTHONPATH=$(pwd)
pytest tests/ -v
```

## Project Structure

```
flowspace/
├── app/
│   ├── routers/            # HTTP route definitions
│   ├── services/           # Business logic layer
│   ├── repositories/       # Database query layer
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── core/               # Config, security, dependencies
│   └── db/                 # Database connection and session
├── frontend/
│   └── src/
│       ├── api/            # Axios API client functions
│       ├── components/     # Reusable React components
│       │   ├── board/      # Kanban board components
│       │   └── layout/     # Layout components
│       ├── pages/          # Page-level components
│       └── store/          # Zustand global state
├── migrations/             # Alembic migration history
├── infrastructure/         # Terraform AWS infrastructure
├── tests/                  # Pytest test suite
├── docker-compose.yml      # Local development databases
└── .env.example            # Environment variable template
```

## Design Patterns Used

- **Repository Pattern** — database queries separated from business logic
- **Service Layer Pattern** — business logic separated from HTTP handlers
- **Dependency Injection** — FastAPI Depends() for database sessions and auth
- **SOLID Principles** — single responsibility across all layers

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Register new company and admin user |
| POST | /auth/login | Login and get JWT token |
| POST | /auth/refresh | Refresh access token |
| GET | /projects | List all projects for workspace |
| POST | /projects | Create new project |
| GET | /projects/:id/columns | List columns for a project |
| POST | /projects/:id/columns | Create a column |
| POST | /projects/:id/columns/:id/tasks | Create a task |
| PATCH | /tasks/:id/move | Move task to different column |
| GET | /workspace/members | List workspace members |
| POST | /workspace/invite | Invite a member |
| GET | /teams | List all teams |
| POST | /teams | Create a team |
| GET | /billing | Get billing info and plan limits |
| POST | /billing/order | Create Razorpay payment order |
| POST | /billing/verify | Verify payment and upgrade plan |

## Resume Description

> Built a production-ready multi-tenant SaaS project management platform using FastAPI, React, PostgreSQL, MongoDB, and Redis — deployed on AWS using Terraform with one-command deploy/destroy, Razorpay billing integration, role-based access control, team management, and a drag-and-drop kanban board.

# Flowspace

A production-ready multi-tenant SaaS project management platform built with FastAPI, React, PostgreSQL, and deployed on AWS. Think of it as a Jira/Trello alternative with full team management, billing, and cloud deployment.

## Live Demo

- Frontend: http://flowspace-frontend-prod.s3-website.ap-south-1.amazonaws.com
- API Docs: http://13.235.218.59:8000/docs

## Features

### Project Management
- Multi-tenant architecture — each company gets its own isolated workspace
- Kanban board with drag and drop task management
- Resizable columns with hover effect
- Task priority levels (Low, Medium, High, Critical)
- Task due dates with overdue highlighting in red
- Task comments with threaded replies
- Activity feed — full history of every task change
- Task search across the entire workspace
- Soft delete for tasks and projects

### Team & User Management
- Role-based access control (Admin / Member)
- Team creation — assign members to teams
- Project visibility per team — members only see their team's projects
- Member invite system
- User profile with name and avatar
- Collapsible sidebar with plan badge

### Billing & Subscriptions
- Free plan — 3 projects, 5 members
- Pro plan — 10 projects, unlimited members (₹999/month)
- Enterprise plan — unlimited everything (₹2,999/month)
- Razorpay payment integration
- Real-time plan upgrade after payment
- Plan badge visible in sidebar at all times

### Notifications
- Bell icon in top right corner on every page
- Shows count of overdue tasks
- Dropdown list of all overdue tasks with due dates

## Tech Stack

### Backend
- **FastAPI** — async Python web framework
- **PostgreSQL** — primary relational database
- **SQLAlchemy** — async ORM with Alembic migrations
- **MongoDB Atlas** — comments and activity feeds
- **Redis** — caching and token management
- **Razorpay** — payment processing
- **Motor** — async MongoDB driver
- **Pydantic** — data validation and serialization
- **JWT** — authentication with access and refresh tokens
- **bcrypt** — password hashing

### Frontend
- **React 18** — UI framework with Vite
- **TanStack Query** — server state management and caching
- **Zustand** — global client state
- **Tailwind CSS** — utility-first styling
- **dnd-kit** — drag and drop for kanban board
- **Axios** — HTTP client with JWT interceptors
- **Lucide React** — icons

### Infrastructure
- **AWS EC2 t3.micro** — application server (free tier)
- **AWS RDS PostgreSQL** — managed database (free tier)
- **AWS ElastiCache Redis** — managed Redis (free tier)
- **AWS S3** — static frontend hosting and file uploads
- **AWS Elastic IP** — static IP that never changes
- **Nginx** — reverse proxy
- **Terraform** — infrastructure as code

## Architecture

```
Browser (React)
      |
AWS S3 (Static Hosting)
      |
      | HTTP API calls
      |
AWS Elastic IP → AWS EC2 (FastAPI + Uvicorn + Nginx)
                      |
                      |---> AWS RDS (PostgreSQL)
                      |---> AWS ElastiCache (Redis)
                      |---> MongoDB Atlas (Comments, Activity)
                      |---> AWS S3 (File uploads)
                      |---> Razorpay (Payments)
```

## Design Patterns

- **Repository Pattern** — database queries separated from business logic
- **Service Layer Pattern** — business logic separated from HTTP handlers
- **Dependency Injection** — FastAPI Depends() for sessions and auth
- **SOLID Principles** — single responsibility across all layers

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
python3 -m venv flowspace-venv
source flowspace-venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
```

### 3. Start databases

```bash
docker compose up -d
```

Starts PostgreSQL, MongoDB, and Redis locally.

### 4. Run migrations

```bash
export PYTHONPATH=$(pwd)
alembic upgrade head
```

### 5. Start backend

```bash
uvicorn app.main:app --reload
```

API at `http://localhost:8000`
Docs at `http://localhost:8000/docs`

### 6. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend at `http://localhost:5173`

## Environment Variables

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

### Prerequisites

- AWS account (free tier)
- AWS CLI configured
- Terraform installed

### Deploy everything

```bash
cd infrastructure
terraform init
terraform apply
```

Creates: VPC, EC2 t3.micro, RDS PostgreSQL, ElastiCache Redis, S3 buckets, Elastic IP, Security groups, IAM roles

### Deploy frontend

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://flowspace-frontend-prod --delete
```

### Update server with latest code

```bash
ssh -i ~/.ssh/id_rsa ubuntu@YOUR_IP
sudo git -C /app fetch origin
sudo git -C /app reset --hard origin/main
sudo systemctl restart flowspace
```

### Destroy to save credits

```bash
cd infrastructure
terraform destroy
```

## Running Tests

```bash
docker exec -it flowspace-postgres psql -U flowspace -c "CREATE DATABASE flowspace_test;"
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
│   └── db/                 # Database connections (PostgreSQL + MongoDB)
├── frontend/
│   └── src/
│       ├── api/            # Axios API client functions
│       ├── components/
│       │   ├── board/      # Kanban board components
│       │   └── layout/     # Sidebar, AppLayout, NotificationBell
│       ├── pages/          # Page components
│       └── store/          # Zustand global state
├── migrations/             # Alembic migration history
├── infrastructure/         # Terraform AWS infrastructure
├── tests/                  # Pytest test suite
├── docker-compose.yml      # Local development databases
└── .env.example            # Environment variable template
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Register new company and admin |
| POST | /auth/login | Login and get JWT |
| POST | /auth/refresh | Refresh access token |
| POST | /auth/logout | Logout |
| GET | /projects | List projects |
| POST | /projects | Create project |
| PATCH | /projects/:id | Update project |
| DELETE | /projects/:id | Archive project |
| GET | /projects/:id/columns | List columns |
| POST | /projects/:id/columns | Create column |
| POST | /projects/:id/columns/:id/tasks | Create task |
| PATCH | /tasks/:id | Update task |
| PATCH | /tasks/:id/move | Move task to column |
| DELETE | /tasks/:id | Delete task |
| GET | /tasks/search | Search tasks |
| GET | /tasks/:id/comments | Get comments |
| POST | /tasks/:id/comments | Add comment |
| GET | /tasks/:id/activity | Get activity feed |
| GET | /workspace/members | List members |
| POST | /workspace/invite | Invite member |
| GET | /teams | List teams |
| POST | /teams | Create team |
| POST | /teams/:id/members | Add member to team |
| GET | /users/me | Get profile |
| PATCH | /users/me | Update profile |
| GET | /billing | Get billing info |
| POST | /billing/order | Create payment order |
| POST | /billing/verify | Verify payment and upgrade plan |
| POST | /billing/downgrade | Downgrade to free |

## Billing Plans

| Plan | Projects | Members | Price |
|---|---|---|---|
| Free | 3 | 5 | ₹0 |
| Pro | 10 | Unlimited | ₹999/month |
| Enterprise | Unlimited | Unlimited | ₹2,999/month |

## Resume Description

> Built a production-ready multi-tenant SaaS project management platform (like Jira) using FastAPI, React, PostgreSQL, MongoDB, and Redis — deployed on AWS using Terraform with one-command deploy/destroy, Razorpay billing with 3 subscription tiers, role-based access control, team management, drag-and-drop kanban board, task comments and activity feeds, real-time notifications, and a user profile system.

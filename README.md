# Flowspace

A production-ready multi-tenant SaaS project management platform built with FastAPI, React, PostgreSQL, and deployed on AWS. Think of it as a Jira/Trello alternative with full team management, billing, email notifications, and cloud deployment.

## Live Demo

- Frontend: http://flowspace-frontend-prod.s3-website.ap-south-1.amazonaws.com
- API Docs: http://13.207.122.41:8000/docs

> The infrastructure is spun down when not in use to save costs. If the app is offline, reach out and it can be live in under 10 minutes. The site automatically shows an offline page with project details and links when the server is down.

## Features

### Project Management
- Multi-tenant architecture — each company gets its own isolated workspace
- Kanban board with drag and drop task management
- Resizable columns
- Task priority levels (Low, Medium, High, Critical)
- Task due dates with overdue highlighting in red
- Task comments with full thread support
- Activity feed — complete history of every task change
- Task search across the entire workspace
- Soft delete for tasks and projects

### Team and User Management
- Role-based access control (Admin / Member)
- Team creation with project visibility per team
- Members only see projects assigned to their team
- Member invite system with email delivery
- Forced password change on first login for invited users
- User profile page with name and avatar

### Email System
- Email DNS validation on registration — warns if domain does not exist
- Welcome email on registration
- Invite email with temporary password
- Task assigned notification email
- Comment notification email to task assignee
- Daily overdue digest email at 8am

### Password Management
- Forgot password flow with email reset link
- Change password in profile with current and new password
- Force password change on first login for invited members

### Billing and Subscriptions
- Free plan — 3 projects, 5 members
- Pro plan — 10 projects, unlimited members (₹999/month)
- Enterprise plan — unlimited projects and members (₹2,999/month)
- Razorpay payment integration with test mode
- Real-time plan upgrade after successful payment
- Plan badge visible in sidebar at all times

### Role-Based UI
- Admins see Teams, Billing, workspace Settings, invite and remove members
- Members see only their own Profile and the Members list (read-only)
- Settings page shows workspace controls for admins, profile redirect for members

### Notifications
- Bell icon in top right corner on every page
- Shows count of overdue tasks
- Dropdown list of all overdue tasks with due dates

### Offline Resilience
- Health check on every page load
- Automatically redirects to offline page when API is unreachable
- Offline page shows full tech stack, GitHub and LinkedIn links
- Offline page is always live on S3 regardless of infrastructure state

## Tech Stack

### Backend
- **FastAPI** — async Python web framework
- **PostgreSQL** — primary relational database
- **SQLAlchemy** — async ORM
- **Alembic** — database migrations
- **MongoDB Atlas** — comments and activity feeds (Motor async driver)
- **Redis** — caching and token management
- **Razorpay** — payment processing
- **Resend** — transactional email delivery
- **Pydantic** — data validation and serialization
- **JWT** — authentication with access and refresh tokens
- **bcrypt** — password hashing
- **APScheduler** — daily overdue digest cron job
- **dnspython** — email domain DNS validation

### Frontend
- **React** — UI framework with Vite
- **TanStack Query** — server state management and caching
- **Zustand** — global client state
- **Tailwind CSS** — utility-first styling
- **dnd-kit** — drag and drop for kanban board
- **Axios** — HTTP client with JWT interceptors
- **Lucide React** — icons
- **React Router v6** — client-side routing with protected routes

### Infrastructure
- **AWS EC2 t3.micro** — application server (free tier)
- **AWS RDS PostgreSQL** — managed relational database (free tier)
- **AWS ElastiCache Redis** — managed Redis (free tier)
- **AWS S3** — static frontend hosting and file uploads
- **AWS VPC** — isolated network with public and private subnets
- **AWS IAM** — roles and policies for EC2 access to S3
- **AWS Elastic IP** — static IP that never changes
- **Nginx** — reverse proxy
- **Terraform** — infrastructure as code (one command deploy and destroy)
- **GitHub Actions** — CI/CD pipeline (tests, frontend deploy, backend deploy)

## Architecture

```
Browser (React)
      |
AWS S3 (Static Hosting)
      |
      | HTTP API calls
      |
AWS Elastic IP -> AWS EC2 (FastAPI + Uvicorn + Nginx)
                      |
                      |---> AWS RDS (PostgreSQL)
                      |---> AWS ElastiCache (Redis)
                      |---> MongoDB Atlas (Comments, Activity)
                      |---> AWS S3 (File uploads)
                      |---> Razorpay (Payments)
                      |---> Resend (Emails)
```

## CI/CD Pipeline

Every push to main triggers three parallel jobs:

```
Push to main
      |
      |---> Run Tests (pytest, 54 tests, spins up PostgreSQL service)
      |         |
      |         |--> Deploy Frontend (npm build + S3 sync)
      |         |--> Deploy Backend (SSH into EC2, git pull, restart)
      |
      |---> Deploy Offline Page (always runs, ensures page is live)
```

- **Tests** always run in GitHub's own servers — no EC2 needed
- **Frontend deploy** always runs — deploys to S3 regardless of EC2 state
- **Backend deploy** runs when EC2 is up — skips gracefully when infra is destroyed
- **Offline page** always runs — recruiters always see something at the URL

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
| DATABASE_URL | PostgreSQL async connection string |
| MONGODB_URL | MongoDB Atlas connection string |
| MONGODB_DB_NAME | MongoDB database name |
| REDIS_URL | Redis connection string |
| AWS_REGION | AWS region |
| S3_BUCKET_NAME | S3 bucket for file uploads |
| RAZORPAY_KEY_ID | Razorpay API key ID |
| RAZORPAY_KEY_SECRET | Razorpay API secret |
| RESEND_API_KEY | Resend API key for emails |
| FRONTEND_URL | Frontend URL for email links |

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
aws s3 cp public/offline.html s3://flowspace-frontend-prod/offline.html
```

### Update server with latest code

```bash
ssh -i ~/.ssh/id_rsa ubuntu@YOUR_ELASTIC_IP
cd /app && sudo git fetch origin && sudo git reset --hard origin/main
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=/app && alembic upgrade head
sudo systemctl restart flowspace
```

### Destroy to save credits

```bash
cd infrastructure
terraform destroy
```

After destroying, the offline page is automatically restored on the next git push via GitHub Actions. The frontend automatically detects the API is down and redirects to the offline page.

## Running Tests

```bash
docker compose up -d
docker exec -it flowspace-postgres psql -U flowspace -c "CREATE DATABASE flowspace_test;"
export PYTHONPATH=$(pwd)
pytest tests/ -v
```

54 tests across 5 test files covering auth, users, projects, workspace, teams, and billing.

## Project Structure

```
flowspace/
├── app/
│   ├── routers/            # HTTP route definitions
│   ├── services/           # Business logic layer
│   ├── repositories/       # Database query layer
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── core/               # Config, security, dependencies, email validator
│   └── db/                 # PostgreSQL and MongoDB connections
├── frontend/
│   └── src/
│       ├── api/            # Axios API client functions
│       ├── components/
│       │   ├── board/      # Kanban board, task cards, task modal, search
│       │   └── layout/     # Sidebar, AppLayout, NotificationBell, AuthGuard
│       ├── pages/          # All page components
│       └── store/          # Zustand global state
├── .github/workflows/      # GitHub Actions CI/CD (deploy.yml, offline.yml)
├── migrations/             # Alembic migration history
├── infrastructure/         # Terraform AWS infrastructure
├── tests/                  # Pytest test suite (54 tests)
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
| GET | /users/me | Get own profile |
| PATCH | /users/me | Update profile |
| POST | /users/me/change-password | Change password |
| POST | /users/forgot-password | Request password reset email |
| POST | /users/reset-password | Reset password with token |
| GET | /billing | Get billing info and plan limits |
| POST | /billing/order | Create Razorpay payment order |
| POST | /billing/verify | Verify payment and upgrade plan |
| POST | /billing/downgrade | Downgrade to free plan |

## Billing Plans

| Plan | Projects | Members | Price |
|---|---|---|---|
| Free | 3 | 5 | ₹0 |
| Pro | 10 | Unlimited | ₹999/month |
| Enterprise | Unlimited | Unlimited | ₹2,999/month |

## Resume Description

> Built a production-ready multi-tenant SaaS project management platform (like Jira) using FastAPI, React, PostgreSQL, MongoDB, and Redis — deployed on AWS using Terraform with one-command deploy/destroy, full GitHub Actions CI/CD pipeline with 54 automated tests, Razorpay billing with 3 subscription tiers, role-based access control, team management, drag-and-drop kanban board, task comments and activity feeds, transactional email notifications via Resend, forgot password flow, and a fully role-gated UI for admins and members.

## Links

- GitHub: https://github.com/SlingggShottt/flowspace
- LinkedIn: https://www.linkedin.com/in/divyansh-pankaj-mishra-4719b4204/


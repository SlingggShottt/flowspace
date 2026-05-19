#!/bin/bash
# infrastructure/user_data.sh

set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install dependencies
apt-get install -y python3-pip python3-venv git nginx postgresql-client

# Install Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker ubuntu

# Create app directory
mkdir -p /app
cd /app

# Clone the repository
git clone https://github.com/SlingggShottt/flowspace.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cat > /app/.env << EOF
APP_NAME=Flowspace
APP_ENV=production
SECRET_KEY=${secret_key}
DATABASE_URL=postgresql+asyncpg://flowspace:${db_password}@${db_host}:5432/flowspace
MONGODB_URL=${mongodb_url}
MONGODB_DB_NAME=flowspace
REDIS_URL=redis://${redis_host}:6379
AWS_REGION=${aws_region}
S3_BUCKET_NAME=${s3_bucket}
EOF

# Run database migrations
cd /app
export PYTHONPATH=/app
source venv/bin/activate
alembic upgrade head

# Create systemd service for FastAPI
cat > /etc/systemd/system/flowspace.service << EOF
[Unit]
Description=Flowspace FastAPI
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/app
Environment=PYTHONPATH=/app
ExecStart=/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
EnvironmentFile=/app/.env

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx as reverse proxy
cat > /etc/nginx/sites-available/flowspace << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/flowspace /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Start services
systemctl daemon-reload
systemctl enable flowspace
systemctl start flowspace
systemctl restart nginx
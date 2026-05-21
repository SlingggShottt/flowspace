set -e

apt-get update -y
apt-get upgrade -y
apt-get install -y python3-pip python3-venv git nginx postgresql-client

curl -fsSL https://get.docker.com | sh
usermod -aG docker ubuntu

mkdir -p /app
cd /app

git config --global --add safe.directory /app
git clone https://github.com/SlingggShottt/flowspace.git .

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

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
RAZORPAY_KEY_ID=${razorpay_key_id}
RAZORPAY_KEY_SECRET=${razorpay_key_secret}
RESEND_API_KEY=${resend_api_key}
FRONTEND_URL=http://flowspace-frontend-prod.s3-website.ap-south-1.amazonaws.com
EOF

cd /app
export PYTHONPATH=/app
source venv/bin/activate
alembic upgrade head

# Fix CORS in main.py after clone
sed -i 's|"http://localhost:5173",|"http://localhost:5173",\n        "http://flowspace-frontend-prod.s3-website.ap-south-1.amazonaws.com",|' /app/app/main.py

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

# Create a deploy script so you can update the app without SSH
cat > /usr/local/bin/flowspace-deploy << 'DEPLOY'
#!/bin/bash
set -e
echo "Pulling latest code..."
cd /app
git config --global --add safe.directory /app
git pull
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=/app
alembic upgrade head
sed -i 's|"http://localhost:5173",|"http://localhost:5173",\n        "http://flowspace-frontend-prod.s3-website.ap-south-1.amazonaws.com",|' /app/app/main.py
systemctl restart flowspace
echo "Deploy complete!"
DEPLOY

chmod +x /usr/local/bin/flowspace-deploy

# Create a systemd service that runs flowspace-deploy on every boot
cat > /etc/systemd/system/flowspace-deploy.service << EOF
[Unit]
Description=Flowspace Deploy on Boot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/flowspace-deploy
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

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

systemctl daemon-reload
systemctl enable flowspace
systemctl enable flowspace-deploy
systemctl start flowspace
systemctl restart nginx
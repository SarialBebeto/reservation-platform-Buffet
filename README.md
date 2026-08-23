# Buffet Reservation System

A professional, full-stack reservation management system built with **FastAPI**, **PostgreSQL**, and **Tailwind CSS**. Designed for high-control manual payment verification without the overhead of complex payment gateways.

## Key Features

- **Dynamic Order Calculation:** Users can select quantities for various menu items (Sushi, Buffet, etc.) with real-time total price calculation.
- **Automated Reference Generation:** Unique transaction codes are generated for every request to simplify bank/PayPal reconciliation.
- **Dual-Email Workflow:** - **Pending:** Automatic professional receipt sent to users upon request.
- **Confirmation:** Admin-triggered ticket delivery once payment is verified.
- **Admin Dashboard:** Secure interface to manage pending payments, view order summaries, and confirm bookings.
- **Internationalization:** Integrated `intl-tel-input` for global phone number validation and flag selection.

## Tech Stack

- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Frontend:** HTML5, Tailwind CSS, JavaScript (Vanilla)
- **Deployment:** Docker, Kubernetes (k3s)
- **Communication:** FastAPI-Mail (SMTP/Gmail)

## Prerequisites & System Requirements (Ubuntu)

To set up this application on a fresh Ubuntu server (or automate via Ansible), install the following system dependencies:

### 1. System Packages
Run the following to install Python, the required build tools for PostgreSQL (`psycopg2`), and a local database/web server:

```bash
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    gcc \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    nginx
```
*(Note: `gcc` and `libpq-dev` are strictly required to compile the `psycopg2` driver).* 

### 2. Deployment Tools 
- **Docker** (to build from the provided `Dockerfile`)
- **k3s** (for lightweight Kubernetes deployment via `deployment.yaml`)

### 3. External Services
- Gmail Account (with App Password enabled for SMTP email delivery)

### 4. Automated Infrastructure Setup (Ansible)
Alternatively, if you want to automatically set up the fresh Ubuntu server with all dependencies, firewall rules, and `k3s`, use the provided Ansible playbook:
```bash
ansible-playbook -K infrastructure.yml
```

## Environment Variables

The application requires the following environment variables (stored in Kubernetes Secrets or a `.env` file):

| Variable | Description |
| :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string |
| `ADMIN_USERNAME` | Username for the Admin Dashboard |
| `ADMIN_PASSWORD` | Password for the Admin Dashboard |
| `MAIL_USERNAME` | SMTP Email (e.g., your-gmail@gmail.com) |
| `MAIL_PASSWORD` | SMTP App Password (16 characters) |

## Installation & Local Setup

1. **Clone the repository:**
  git clone [https://github.com/SarialBebeto/reservation-platform-Buffet.git]
  cd reservation-buffet

2. **Install Dependencies**
 pip install -r requirements.txt

3. **Database Initialization**
The application uses SQLAlchemy to automatically create tables. Ensure the DATABASE_URL is active.

4. **Run the application**
 uvicorn main:app --reload
 Access the app at http://localhost:8000

## Deployment

### Option A: Docker Compose Deployment (Recommended for Single Server)

1. **Configure Environment Variables**
   Copy `.env.example` to `.env` and fill in your passwords and SMTP details:
   ```bash
   cp .env.example .env
   ```

2. **Run with Docker Compose**
   ```bash
   # Build images and start containers in detached mode
   docker compose up -d --build

   # Check container status
   docker compose ps

   # View application logs
   docker compose logs -f web
   ```
   The application will be accessible at `http://localhost:8000`.

3. **Installing Docker on Rocky Linux 10 / RHEL** (if not already installed):
   ```bash
   sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
   sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   ```

### Option B: Kubernetes (K3s / Helm) Deployment
The project includes a `buffet-app` Helm chart for Kubernetes deployment:

1. **Apply Secrets & Deploy**
   ```bash
   helm upgrade --install app-release ./buffet-app --namespace production --create-namespace
   ```


📂 Project Structure

├── main.py             # FastAPI logic & API routes
├── models.py           # Database schema
├── database.py         # SQLAlchemy configuration
├── static/
│   ├── main.js         # Frontend logic & PayPal integration
│   ├── favicon.png     # Website icon
│   
└── templates/
    ├── index.html      # Main reservation form
    └── admin.html      # Admin management dashboard


## System Architecture & Security
The application is deployed on a k3s cluster with a layered security approach: 

1. *Ingress(Nginx)*: Acts as the entry point , handling SSL termination (HTTPS) and routing traffic to the FastAPI service.

2. *Firewall Rules*:
  Port 80/443 : Open to the public for the reservation web interface

  Port 5432 (Postgres): Strictly internal; only accessible by the FastAPI pod via the ClusterIP service 

  Port 22 (SSH): Restricted to specific IP addresses for administrative maintenance.

3. *Reserve Proxy Logic*: Nginx manages headers, ensures strict-origin-when-cross-origin policies, and buffers requests to protect the application server.


## Security & Networking
The server follows a "Deny by Default" policy. Only the minimum necessary ports are exposed to the public internet.

Firewall Configuration (UFW)
To replicate the production security environment, the following ufw rules are applied on the host: 

# 1. Block all incoming, allow all outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 2. Allow SSH (Standard or Custom Port)
sudo ufw allow ssh

# 3. Allow Web Traffic for Nginx (HTTP & HTTPS)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 4. Enable Firewall
sudo ufw enable

Network Topology
Public Layer: Nginx Ingress listens on ports 80/443.

Private Layer: The PostgreSQL database is bound to the cluster-ip and is not accessible via the public IP of the server. Even if ufw were disabled, the database is only listening for internal Kubernetes traffic.

Reverse Proxy: Nginx is configured to pass the X-Forwarded-For header so that FastAPI can log the real IP of the customers for security auditing.
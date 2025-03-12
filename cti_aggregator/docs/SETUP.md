# CTI Aggregator Setup Guide

This guide will help you set up the CTI Aggregator project, including all its components:
- Python backend (Django)
- Redis server
- Celery workers
- Frontend dashboard

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker (for Redis)
- Git

## Clone the Repository

```bash
git clone https://github.com/yourusername/cti-aggregator.git
cd cti-aggregator
```

## Backend Setup

### 1. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root directory with the following variables:

```
# Django settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings (if using PostgreSQL)
# DB_NAME=cti_aggregator
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Redis settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# CrowdStrike API credentials (if available)
FALCON_CLIENT_ID=your_client_id
FALCON_CLIENT_SECRET=your_client_secret
```

### 4. Set up the database

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
cd ..
```

## Redis Setup

### Using Docker (recommended)

```bash
# Pull the Redis image
docker pull redis

# Start a Redis container
docker run --name redis-server -p 6379:6379 -d redis

# Verify Redis is running
docker ps
```

### Alternative: Install Redis directly

If you prefer not to use Docker, you can install Redis directly:

- **Windows**: Download and install from [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
- **Linux**: `sudo apt-get install redis-server`
- **Mac**: `brew install redis`

## Frontend Setup

### 1. Install Node.js dependencies

```bash
cd frontend/cti-dashboard
npm install
cd ../..
```

## Running the Application

You can start all components individually or use the provided PowerShell script.

### Using the PowerShell script (Windows)

```powershell
# From the project root
.\Test.ps1
```

This script will:
1. Check if Redis is running and start it if needed
2. Apply any pending database migrations
3. Start the Django backend server
4. Run Tailored Intelligence tests and updates
5. Start Celery worker and beat scheduler
6. Start the frontend dashboard

### Starting components individually

#### 1. Start Redis (if not using Docker)

```bash
# Windows
redis-server

# Linux/Mac
redis-server
```

#### 2. Start Django backend

```bash
cd backend
python manage.py runserver
```

#### 3. Start Celery worker

```bash
# In a new terminal
cd backend
celery -A backend.celery worker --loglevel=info --pool=solo
```

#### 4. Start Celery beat scheduler

```bash
# In a new terminal
cd backend
celery -A backend.celery beat --loglevel=info
```

#### 5. Start the frontend

```bash
# In a new terminal
cd frontend/cti-dashboard
npm run dev
```

## Accessing the Application

- **Frontend Dashboard**: http://localhost:3000
- **Django Admin**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/

## Troubleshooting

### Redis Connection Issues

If you encounter Redis connection issues:

1. Verify Redis is running:
   ```bash
   docker ps | grep redis-server
   ```

2. Check Redis connection:
   ```bash
   redis-cli ping
   ```
   Should return "PONG"

### Database Migration Issues

If you encounter database migration issues:

1. Reset migrations (if needed):
   ```bash
   cd backend
   python manage.py migrate --fake zero
   python manage.py makemigrations
   python manage.py migrate
   ```

### Frontend Build Issues

If you encounter issues with the frontend:

1. Clear node_modules and reinstall:
   ```bash
   cd frontend/cti-dashboard
   rm -rf node_modules
   npm install
   ```

2. Check for compatibility issues:
   ```bash
   npm list --depth=0
   ```

## Data Sources

The application uses several data sources:

1. **CrowdStrike Intelligence API**: Requires valid API credentials
2. **CISA KEV**: Public data source
3. **Various threat intelligence blogs**: Public data sources

For CrowdStrike API access, you'll need to set the appropriate environment variables in the `.env` file.

## Scheduled Tasks

The application uses Celery to run scheduled tasks:

1. Fetch intelligence articles from various sources
2. Update CrowdStrike Tailored Intelligence data
3. Update CISA KEV data

These tasks are configured in the Celery beat scheduler.

## Development

For development, you can use the following commands:

- Run tests: `python manage.py test`
- Run specific data source tests: `python run_tailored_intel_update.py --test`
- Update data manually: `python run_tailored_intel_update.py` 
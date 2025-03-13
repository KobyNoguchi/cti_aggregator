# CTI Aggregator

A comprehensive Cyber Threat Intelligence aggregation system that collects, processes, and visualizes threat data from multiple sources.

> **IMPORTANT**: This project is designed to run on Windows systems. It uses Docker Desktop for Windows to manage all dependencies. You **DO NOT** need to install Redis or any other technologies separately - everything is automatically set up when you run the Docker Compose command.

## Overview

This project consists of several components:
- Backend (Django REST API)
- Frontend (React dashboard)
- Celery workers for asynchronous task processing
- Redis for caching and message brokering

## Prerequisites

- Windows 10/11 operating system
- Docker Desktop for Windows (required for containerized deployment)
- Git for Windows
- PowerShell 7 (recommended, but PowerShell 5.1 also works)

## Pre-Installation: Setting Up Docker Desktop for Windows

If you don't have Docker Desktop installed, follow these instructions:

1. Download and install Docker Desktop for Windows from [Docker Hub](https://www.docker.com/products/docker-desktop)
2. Follow the installation wizard
3. Docker Compose comes included with Docker Desktop for Windows
4. After installation, start Docker Desktop and ensure it's running (look for the Docker icon in your system tray)
5. Verify the installation by opening PowerShell and running:
   ```powershell
   docker --version
   docker-compose --version
   ```

## Installation

1. Clone the repository using PowerShell:
```powershell
git clone https://github.com/YOUR_USERNAME/Peregrine.git
cd Peregrine
```

2. No additional installation steps are required as the application runs in Docker containers.

## Running the Application

You have two options to run the application:

### Option 1: Using Docker Compose (Recommended)

```powershell
cd cti_aggregator/docker
docker-compose up -d
```

This will:
- Start a Redis instance for caching and message brokering (no separate Redis installation is required)
- Build and start the Django backend server
- Start Celery workers and beat scheduler for background tasks
- Build and start the React frontend

### Option 2: Using the PowerShell Script

```powershell
cd cti_aggregator
.\Test.ps1
```

This will:
- Check if Redis is running in Docker and start it if needed
- Apply any pending database migrations
- Start the Django backend server
- Run intelligence tests and updates
- Start Celery workers and Celery Beat scheduler
- Start the frontend dashboard
- Open the dashboard in your default browser

## Accessing the Application

Once all components are running:
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin interface: http://localhost:8000/admin/

## Troubleshooting

### Docker Issues
- Ensure Docker Desktop is running (check system tray for the Docker whale icon)
- Check container status: `docker ps -a`
- View container logs: `docker logs [container-name]`
- Restart all services: `docker-compose down && docker-compose up -d`

### PowerShell Execution Policy
If you encounter execution policy errors when running PowerShell scripts, try running PowerShell as Administrator and setting:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Conflicts
If you encounter port conflicts, you may have other services using ports 3000, 8000, or 6379. You can modify the port mappings in `docker-compose.yml`.

## Development

For development, you can use the individual requirements.txt files:
- Backend: `cti_aggregator/backend/requirements.txt`
- Dashboards: `cti_aggregator/dashboards/requirements.txt`
- Comprehensive: `cti_aggregator/docker/requirements.txt`

## Project Structure

- `backend/`: Django REST API
- `frontend/`: React dashboard
- `dashboards/`: Streamlit dashboards for data visualization
- `data_sources/`: Data collection modules
- `docker/`: Docker configuration files

## License

[Your license information here] 
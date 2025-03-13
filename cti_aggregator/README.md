# CTI Aggregator

A comprehensive Cyber Threat Intelligence aggregation system that collects, processes, and visualizes threat data from multiple sources.

> **IMPORTANT**: This project uses Docker and Docker Compose to manage all dependencies. You **DO NOT** need to install Redis or any other technologies separately - everything is automatically set up when you run the Docker Compose command. Simply follow the Docker installation instructions below if you don't already have Docker installed.

## Overview

This project consists of several components:
- Backend (Django REST API)
- Frontend (React dashboard)
- Celery workers for asynchronous task processing
- Redis for caching and message brokering

## Prerequisites

- Docker and Docker Compose (required for containerized deployment)
- Git

## Pre-Installation: Setting Up Docker and Docker Compose

If you don't have Docker and Docker Compose installed, follow these instructions:

### Installing Docker

#### Windows
1. Download and install Docker Desktop from [Docker Hub](https://www.docker.com/products/docker-desktop)
2. Follow the installation wizard
3. Docker Compose comes included with Docker Desktop for Windows

#### macOS
1. Download and install Docker Desktop from [Docker Hub](https://www.docker.com/products/docker-desktop)
2. Follow the installation wizard
3. Docker Compose comes included with Docker Desktop for macOS

#### Linux (Ubuntu/Debian)
1. Update your package index:
   ```bash
   sudo apt-get update
   ```
2. Install dependencies:
   ```bash
   sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
   ```
3. Add Docker's official GPG key:
   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   ```
4. Set up the stable repository:
   ```bash
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   ```
5. Update the package index again:
   ```bash
   sudo apt-get update
   ```
6. Install Docker:
   ```bash
   sudo apt-get install docker-ce docker-ce-cli containerd.io
   ```
7. Add your user to the docker group to run Docker without sudo:
   ```bash
   sudo usermod -aG docker $USER
   ```
8. Log out and log back in for the changes to take effect

### Installing Docker Compose (Linux Only)
1. Download the current stable release of Docker Compose:
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```
2. Apply executable permissions:
   ```bash
   sudo chmod +x /usr/local/bin/docker-compose
   ```

### Verify the Installation
```bash
docker --version
docker-compose --version
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/Peregrine.git
cd Peregrine
```

2. No additional installation steps are required as the application runs in Docker containers.

## Running the Application

The easiest way to run the application is using Docker Compose:

```bash
cd cti_aggregator/docker
docker-compose up -d
```

This will:
- Start a Redis instance for caching and message brokering (no separate Redis installation is required)
- Build and start the Django backend server
- Start Celery workers and beat scheduler for background tasks
- Build and start the React frontend

## Accessing the Application

Once all containers are running:
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin interface: http://localhost:8000/admin/

## Troubleshooting

### Docker Issues
- Ensure Docker daemon is running: `sudo systemctl start docker` (Linux only)
- Check container status: `docker ps -a`
- View container logs: `docker logs [container-name]`
- Restart all services: `docker-compose down && docker-compose up -d`

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
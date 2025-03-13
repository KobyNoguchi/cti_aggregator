# CTI Aggregator

A comprehensive Cyber Threat Intelligence aggregation system that collects, processes, and visualizes t
hreat data from multiple sources.

> **IMPORTANT**: This project is designed to run on Windows systems. It uses Docker Desktop for Windows
 to manage all dependencies. You **DO NOT** need to install Redis or any other technologies separately
- everything is automatically set up when you run the Docker Compose command.

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

- Ensure Docker Desktop is running (check system tray for the Docker whale icon)
- Check container status: `docker ps -a`
- View container logs: `docker logs [container-name]`
- Restart all services: `docker-compose down && docker-compose up -d`

### PowerShell Execution Policy
If you encounter execution policy errors when running PowerShell scripts, try running PowerShell as Adm
inistrator and setting:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Conflicts
If you encounter port conflicts, you may have other services using ports 3000, 8000, or 6379. You can m
odify the port mappings in `docker-compose.yml`.

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

## Starting the Application
**Option 1: Using Docker Compose (recommended)**
*In PowerShell*
- cd cti_aggregator/docker
- docker-compose up -d

**Option 2: Using the PowerShell Script**
*In PowerShell*
- cd cti_aggregator
- .\Test.ps1


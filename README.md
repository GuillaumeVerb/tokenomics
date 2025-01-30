# Tokenomics Application

This application consists of a FastAPI backend, React frontend, and MongoDB database. Below are instructions for running the application using Docker.

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd tokenomics
```

2. Create a `.env` file in the root directory:
```bash
# Backend
MONGODB_URI=mongodb://mongo:27017/tokenomics
JWT_SECRET=your_jwt_secret_key_here
ENVIRONMENT=production

# Frontend
REACT_APP_API_URL=http://localhost:8000
NODE_ENV=production
```

3. Build and start the containers:
```bash
docker-compose up --build
```

This command will:
- Build the Docker images for the backend and frontend
- Start all services defined in docker-compose.yml
- Create necessary volumes and networks
- Set up environment variables

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MongoDB: localhost:27017

## Development Mode

For development, you can use the volume mounts to enable hot-reloading:
- Backend code changes in `./backend/app` will be reflected immediately
- Frontend code changes in `./frontend/src` and `./frontend/public` will trigger automatic rebuilds

## Container Management

Common commands:

```bash
# Start containers in the background
docker-compose up -d

# View container logs
docker-compose logs -f

# Stop containers
docker-compose down

# Stop containers and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose up --build <service-name>
```

## Architecture

The application uses a three-tier architecture:
1. Frontend (React) - Port 3000
2. Backend (FastAPI) - Port 8000
3. Database (MongoDB) - Port 27017

All services are connected through a Docker network named `app-network`.

## Data Persistence

MongoDB data is persisted using a named volume `mongodb_data`. This ensures your data survives container restarts.

## Health Checks

The application includes health checks for:
- Backend service (HTTP endpoint)
- MongoDB (ping command)

These ensure the application only starts when all dependencies are healthy.

## Troubleshooting

1. If the frontend can't connect to the backend:
   - Check if the backend container is running: `docker-compose ps`
   - Verify the backend health check: `docker-compose logs backend`
   - Ensure REACT_APP_API_URL is set correctly

2. If MongoDB connection fails:
   - Check if MongoDB container is running: `docker-compose ps`
   - Verify MongoDB logs: `docker-compose logs mongo`
   - Ensure MONGODB_URI is correct in the environment variables

3. For permission issues:
   - Ensure the current user has permissions to access Docker
   - Check volume mount permissions 
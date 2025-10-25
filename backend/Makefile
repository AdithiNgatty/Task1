# Makefile for Docker FastAPI Backend

# Variables
IMAGE_NAME = login_backend
TAG = latest
DOCKER_USERNAME = adithigatty

# Build Docker image
build:
	docker build -t $(IMAGE_NAME):$(TAG) .

# Run docker-compose
up:
	docker-compose up --build -d

# Stop containers
down:
	docker-compose down

# Show running containers
ps:
	docker ps

# View logs
logs:
	docker-compose logs -f

# Tag image for Docker Hub
tag:
	docker tag $(IMAGE_NAME):$(TAG) $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

# Push to Docker Hub
push: tag
	docker push $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

# Remove local images (optional cleanup)
clean:
	docker rmi $(IMAGE_NAME):$(TAG) || true

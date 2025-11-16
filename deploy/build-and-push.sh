#!/bin/bash

# Build and Push Script for TamaOd
# Usage: ./deploy/build-and-push.sh [registry] [tag]
# Example: ./deploy/build-and-push.sh quay.io/username v1.0.0
#
# Note: This script can be run from any directory - it will automatically
# change to the project root for the build context

set -e

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
REGISTRY=${1:-}
TAG=${2:-latest}

if [ -z "$REGISTRY" ]; then
    echo "Error: Registry must be provided as the first argument."
    exit 1
fi
IMAGE_NAME="tamaod"

FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}"

# Change to project root for build context
cd "$PROJECT_ROOT"

echo "Building Docker image..."
podman build -f deploy/Dockerfile -t ${IMAGE_NAME}:${TAG} .

echo "Tagging image as ${FULL_IMAGE}:${TAG}..."
podman tag ${IMAGE_NAME}:${TAG} ${FULL_IMAGE}:${TAG}

# Also tag as latest if not already latest
if [ "$TAG" != "latest" ]; then
    echo "Tagging image as ${FULL_IMAGE}:latest..."
    podman tag ${IMAGE_NAME}:${TAG} ${FULL_IMAGE}:latest
fi

echo "Pushing image to registry..."
podman push ${FULL_IMAGE}:${TAG}

if [ "$TAG" != "latest" ]; then
    podman push ${FULL_IMAGE}:latest
fi

echo "Successfully built and pushed:"
echo "  ${FULL_IMAGE}:${TAG}"
if [ "$TAG" != "latest" ]; then
    echo "  ${FULL_IMAGE}:latest"
fi

echo ""
echo "To run the container:"

echo "To run with custom environment:"
echo "  podman run -p 8080:8080 \\"
echo "    --env-file .env.prod \\"
echo "    --name tamaod-app \\"
echo "    ${FULL_IMAGE}:${TAG}" 
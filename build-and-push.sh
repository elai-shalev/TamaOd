#!/bin/bash

# Build and Push Script for TamaOd
# Usage: ./build-and-push.sh [registry] [tag]
# Example: ./build-and-push.sh quay.io/username v1.0.0

set -e

# Default values

REGISTRY=${1:-}
TAG=${2:-latest}

if [ -z "$REGISTRY" ]; then
    echo "Error: Registry must be provided as the first argument."
    exit 1
fi
IMAGE_NAME="tamaod"

FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}"

echo "Building Docker image..."
podman build -t ${IMAGE_NAME}:${TAG} .

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
echo "  podman run -p 8080:8080 ${FULL_IMAGE}:${TAG}"
echo ""
echo "To run with custom environment:"
echo "  podman run -p 8080:8080 \\"
echo "    -e SECRET_KEY=\"your-secret-key\" \\"
echo "    -e ALLOWED_HOSTS=\"yourdomain.com\" \\"
echo "    ${FULL_IMAGE}:${TAG}" 
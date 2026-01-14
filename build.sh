#!/bin/bash
set -e

echo "🚀 Starting build process for Render.com deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Build frontend
echo "🎨 Building frontend..."
cd frontend

# Install Node.js dependencies
npm install

# Build production frontend
npm run build

cd ..

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs

# Copy built frontend to static directory
echo "📋 Setting up static files..."
mkdir -p static
cp -r frontend/dist/* static/

echo "✅ Build completed successfully!"

#!/bin/bash
set -e

echo "🚀 Starting build process for Render.com deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found! Render should auto-install it for Python services."
    echo "⚠️  Frontend will not be built. Please enable Node.js in Render settings."
    exit 0
fi

echo "📦 Node.js version: $(node --version)"
echo "📦 NPM version: $(npm --version)"

# Build frontend
echo "🎨 Building frontend..."
cd frontend

# Install Node.js dependencies
echo "📦 Installing frontend dependencies..."
npm ci --production=false

# Build production frontend
echo "🏗️  Building production bundle..."
npm run build

cd ..

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs

# Copy built frontend to static directory
echo "📋 Copying built frontend to static directory..."
mkdir -p static
cp -r frontend/dist/* static/

echo "✅ Build completed successfully!"
echo "📂 Static files are in: static/"
ls -la static/ | head -10

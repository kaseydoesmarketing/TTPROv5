#!/bin/bash
# Ensure vite is installed and available
if [ ! -f "./node_modules/.bin/vite" ]; then
    echo "Vite not found, installing dependencies..."
    npm install
fi

# Run the build
npx vite build
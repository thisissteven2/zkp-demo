#!/bin/bash

set -e

# Absolute path of the script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ZKP_DIR="$SCRIPT_DIR/zkp"
BUILD_DIR="$ZKP_DIR/build"
PTAU_DIR="$ZKP_DIR/ptau"

function run_service() {
  local SERVICE_DIR=$1
  local PORT=$2

  echo "Setting up service in $SERVICE_DIR..."

  pushd "$SCRIPT_DIR/$SERVICE_DIR" > /dev/null

  if [ ! -d "venv" ]; then
    python3 -m venv venv
  fi

  # Activate virtualenv cross-platform
  if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows Git Bash or similar
    source venv/Scripts/activate
  else
    # Unix/Linux/macOS
    source venv/bin/activate
  fi

  echo "Starting service on port $PORT..."
  uvicorn app:app --port $PORT &

  popd > /dev/null
}

# Start backend services
run_service "proof-service" 5003
run_service "idp-service" 5000
run_service "verifier-service" 5002
run_service "protected-service" 5001

# Open frontend in default browser
FRONTEND_PATH="$SCRIPT_DIR/frontend/index.html"
echo "Opening frontend: $FRONTEND_PATH"

if command -v xdg-open > /dev/null; then
  xdg-open "$FRONTEND_PATH"
elif command -v open > /dev/null; then
  open "$FRONTEND_PATH"
elif command -v powershell.exe > /dev/null; then
  powershell.exe start "$FRONTEND_PATH"
else
  echo "Please open frontend/index.html manually in your browser."
fi
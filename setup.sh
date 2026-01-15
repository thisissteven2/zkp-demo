#!/bin/bash

set -e

echo "Starting setup..."

ZKP_DIR="./zkp"
BUILD_DIR="$ZKP_DIR/build"
PTAU_DIR="$ZKP_DIR/ptau"

function check_zkp() {
  echo "Checking ZKP setup..."

  if [ ! -d "$BUILD_DIR" ]; then
    echo "Build folder missing."
    return 1
  fi

  if [ ! -f "$PTAU_DIR/pot12_final_phase2.ptau" ]; then
    echo "PTAU final phase2 file missing."
    return 1
  fi

  if [ ! -f "$BUILD_DIR/age_balance_final.zkey" ]; then
    echo "Final zkey file missing."
    return 1
  fi

  if [ ! -f "$BUILD_DIR/verification_key.json" ]; then
    echo "Verification key missing."
    return 1
  fi

  echo "ZKP setup looks complete."
  return 0
}

function run_zkp_setup() {
  echo "Running ZKP setup..."

  cd "$ZKP_DIR"

  # Compile circuit
  echo "Compiling age_balance.circom..."
  circom circuit/age_balance.circom --r1cs --wasm --sym -l node_modules -o build

  # Setup ptau if not exists
  if [ ! -f "$PTAU_DIR/pot12_0000.ptau" ]; then
    mkdir -p "$PTAU_DIR"
    cd "$PTAU_DIR"
    echo "Generating initial Powers of Tau (pot12_0000.ptau)..."
    snarkjs powersoftau new bn128 12 pot12_0000.ptau -v

    echo "Contributing to Powers of Tau (pot12_final.ptau)..."
    snarkjs powersoftau contribute pot12_0000.ptau pot12_final.ptau --name="Steven" -v

    echo "Verifying Powers of Tau..."
    snarkjs powersoftau verify pot12_final.ptau

    cd ..
  else
    echo "Powers of Tau already present."
  fi

  # Prepare phase2
  echo "Preparing phase2 ptau file..."
  snarkjs powersoftau prepare phase2 ptau/pot12_final.ptau ptau/pot12_final_phase2.ptau

  # Groth16 setup
  echo "Running Groth16 setup..."
  snarkjs groth16 setup build/age_balance.r1cs ptau/pot12_final_phase2.ptau build/age_balance_0000.zkey

  # Contribute to zkey
  echo "Contributing to final zkey..."
  snarkjs zkey contribute build/age_balance_0000.zkey build/age_balance_final.zkey --name="Steven contribution" -e="random_entropy_123"

  # Export verification key
  echo "Exporting verification key..."
  snarkjs zkey export verificationkey build/age_balance_final.zkey build/verification_key.json

  # Create example input.json
  echo "Creating example input.json..."
  cat > build/input.json <<EOL
{
  "age": 22,
  "balance": 5000,
  "valid": 1
}
EOL

  echo "ZKP setup complete."
  cd ..
}

function setup_service() {
  local SERVICE_DIR=$1
  local PORT=$2

  echo "Setting up service in $SERVICE_DIR..."

  cd "$SERVICE_DIR"

  # Create virtual env if not exists
  if [ ! -d "venv" ]; then
    python3 -m venv venv
  fi

  source venv/bin/activate

  pip install --upgrade pip
  pip install -r requirements.txt

  echo "Starting service on port $PORT..."
  uvicorn app:app --port $PORT &

  cd ..
}

echo "Checking ZKP build and keys..."
if ! check_zkp; then
  run_zkp_setup
else
  echo "ZKP build already present, skipping setup."
fi

# Start backend services
setup_service "proof-service" 5003
setup_service "identity-provider" 5000
setup_service "verification-service" 5001

# Open frontend in default browser (Linux/macOS)
FRONTEND_PATH="$(pwd)/frontend/index.html"
echo "Opening frontend: $FRONTEND_PATH"

if which xdg-open > /dev/null; then
  xdg-open "$FRONTEND_PATH"
elif which open > /dev/null; then
  open "$FRONTEND_PATH"
else
  echo "Please open frontend/index.html manually in your browser."
fi

echo "Setup complete. Backend services are running."
echo "To stop services, kill their processes or close this terminal."

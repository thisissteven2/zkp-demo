#!/bin/bash

set -e

echo "Starting setup..."

# Absolute path of the script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ZKP_DIR="$SCRIPT_DIR/zkp"
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

  pushd "$ZKP_DIR" > /dev/null

  # Compile circuit
  echo "Compiling age_balance.circom..."
  circom circuit/age_balance.circom --r1cs --wasm --sym -l node_modules -o build

  # Setup ptau if not exists
  if [ ! -f "ptau/pot12_0000.ptau" ]; then
    mkdir -p ptau
    pushd ptau > /dev/null

    echo "Generating initial Powers of Tau (pot12_0000.ptau)..."
    snarkjs powersoftau new bn128 12 pot12_0000.ptau -v

    echo "Contributing to Powers of Tau (pot12_final.ptau)..."
    # Provide entropy automatically to avoid prompt
    printf "Steven random entropy\n" | snarkjs powersoftau contribute pot12_0000.ptau pot12_final.ptau --name="Steven" -v

    echo "Verifying Powers of Tau..."
    snarkjs powersoftau verify pot12_final.ptau

    popd > /dev/null
  else
    echo "Powers of Tau already present."
  fi

  echo "Preparing phase2 ptau file..."
  snarkjs powersoftau prepare phase2 ptau/pot12_final.ptau ptau/pot12_final_phase2.ptau

  echo "Running Groth16 setup..."
  snarkjs groth16 setup build/age_balance.r1cs ptau/pot12_final_phase2.ptau build/age_balance_0000.zkey

  echo "Contributing to final zkey..."
  snarkjs zkey contribute build/age_balance_0000.zkey build/age_balance_final.zkey --name="Steven contribution" -e="random_entropy_123"

  echo "Exporting verification key..."
  snarkjs zkey export verificationkey build/age_balance_final.zkey build/verification_key.json

  echo "Copying verification_key.json to verifier-service..."
  cp build/verification_key.json "$SCRIPT_DIR/verifier-service/"

  echo "Creating example input.json..."
  cat > build/input.json <<EOL
{
  "age": 22,
  "balance": 5000,
  "valid": 1
}
EOL

  echo "ZKP setup complete."

  popd > /dev/null
}

function setup_service() {
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

  pip install --upgrade pip
  pip install -r requirements.txt
}

echo "Checking ZKP build and keys..."
if ! check_zkp; then
  run_zkp_setup
else
  echo "ZKP build already present, skipping setup."
fi

# Setup backend services
setup_service "proof-service" 5003
setup_service "idp-service" 5000
setup_service "verifier-service" 5001
setup_service "protected-service" 5002

echo "Setup complete. Backend services ready to run."

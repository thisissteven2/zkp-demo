#!/bin/bash

set -e

echo "Starting ZKP rebuild..."

# Absolute path of the script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ZKP_DIR="$SCRIPT_DIR/zkp"
BUILD_DIR="$ZKP_DIR/build"
PTAU_DIR="$ZKP_DIR/ptau"

pushd "$ZKP_DIR" > /dev/null

# Recompile circuit
echo "Recompiling age_balance.circom..."
circom circuit/age_balance.circom --r1cs --wasm --sym -l node_modules -o build

# Ensure ptau files exist (run only if missing)
if [ ! -f "ptau/pot12_0000.ptau" ]; then
  mkdir -p ptau
  pushd ptau > /dev/null

  echo "Generating initial Powers of Tau (pot12_0000.ptau)..."
  snarkjs powersoftau new bn128 12 pot12_0000.ptau -v

  echo "Contributing to Powers of Tau (pot12_final.ptau)..."
  printf "Steven random entropy\n" | snarkjs powersoftau contribute pot12_0000.ptau pot12_final.ptau --name="Steven" -v

  echo "Verifying Powers of Tau..."
  snarkjs powersoftau verify pot12_final.ptau

  popd > /dev/null
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

echo "Rebuild complete."

popd > /dev/null

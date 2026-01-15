from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os

app = FastAPI(title="ZKP Proof Generation Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc)
    allow_headers=["*"],  # Allow all headers
)

ZKP_BUILD_DIR = "../zkp/build"

class ProofRequest(BaseModel):
    age: int
    balance: int

@app.post("/generate-proof")
def generate_proof(req: ProofRequest):
    input_data = {
        "age": req.age,
        "balance": req.balance,
        "valid": 1
    }

    input_path = os.path.join(ZKP_BUILD_DIR, "input.json")
    witness_path = os.path.join(ZKP_BUILD_DIR, "witness.wtns")
    proof_path = os.path.join(ZKP_BUILD_DIR, "proof.json")
    public_path = os.path.join(ZKP_BUILD_DIR, "public.json")
    wasm_path = os.path.join(ZKP_BUILD_DIR, "age_balance_js", "age_balance.wasm")
    zkey_path = os.path.join(ZKP_BUILD_DIR, "age_balance_final.zkey")

    # Write input.json
    with open(input_path, "w") as f:
        json.dump(input_data, f)

    # Generate witness
    witness_cmd = [
        "node",
        os.path.join(ZKP_BUILD_DIR, "age_balance_js", "generate_witness.js"),
        wasm_path,
        input_path,
        witness_path
    ]
    witness_proc = subprocess.run(witness_cmd, capture_output=True, text=True, shell=True)
    if witness_proc.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Witness generation failed: {witness_proc.stderr}")

    # Generate proof
    prove_cmd = [
        "npx",
        "snarkjs",
        "groth16",
        "prove",
        zkey_path,
        witness_path,
        proof_path,
        public_path
    ]
    prove_proc = subprocess.run(prove_cmd, capture_output=True, text=True, shell=True)
    if prove_proc.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Proof generation failed: {prove_proc.stderr}")

    # Read proof and public.json to return
    with open(proof_path) as f:
        proof = json.load(f)
    with open(public_path) as f:
        public = json.load(f)

    return {
        "proof": proof,
        "public": public
    }

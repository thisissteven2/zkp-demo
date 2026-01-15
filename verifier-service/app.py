from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import subprocess
import json
import tempfile
import os

app = FastAPI(title="ZKP Verifier Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc)
    allow_headers=["*"],  # Allow all headers
)

# ---- Request schema ----
class ProofRequest(BaseModel):
    proof: dict
    public: list

# ---- Verify endpoint ----
@app.post("/verify-proof")
def verify_proof(req: ProofRequest):
    with tempfile.TemporaryDirectory() as tmpdir:
        proof_path = os.path.join(tmpdir, "proof.json")
        public_path = os.path.join(tmpdir, "public.json")

        with open(proof_path, "w") as f:
            json.dump(req.proof, f)

        with open(public_path, "w") as f:
            json.dump(req.public, f)

        result = subprocess.run(
            "npx snarkjs groth16 verify verification_key.json "
            f"{public_path} {proof_path}",
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode != 0:
            raise HTTPException(status_code=400, detail="Invalid ZK proof")

        return {
            "verified": True
        }

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time
from jose import jwt

app = FastAPI(title="Identity Provider (IdP)")

# Shared secret with protected-service
SECRET_KEY = "SUPER_SECRET_IDP_KEY"
ALGORITHM = "HS256"
TOKEN_TTL = 60  # seconds

# Verifier service endpoint
VERIFIER_URL = "http://127.0.0.1:5002/verify-proof"


# Expected request body from user
class ProofRequest(BaseModel):
    proof: dict
    public: list


@app.post("/issue-token")
def issue_token(req: ProofRequest):
    # 1. Forward proof to verifier-service
    resp = requests.post(VERIFIER_URL, json={
        "proof": req.proof,
        "public": req.public
    })

    # 2. If verifier rejects proof → deny token
    if resp.status_code != 200:
        raise HTTPException(status_code=403, detail="Invalid ZK proof")

    # 3. Proof is valid → issue JWT
    now = int(time.time())
    payload = {
        "iss": "idp-service",
        "iat": now,
        "exp": now + TOKEN_TTL,

        # 🔐 This is the ONLY thing protected-service cares about
        "zk_verified": True
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

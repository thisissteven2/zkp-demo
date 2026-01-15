from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time
from jose import jwt

app = FastAPI(title="Identity Provider (IdP)")

SECRET_KEY = "SUPER_SECRET_IDP_KEY"
ALGORITHM = "HS256"
TOKEN_TTL = 60  # seconds

VERIFIER_URL = "http://127.0.0.1:5002/verify-proof"
class ProofRequest(BaseModel):
    proof: dict
    public: list

@app.post("/issue-token")
def issue_token(req: ProofRequest):
    resp = requests.post(VERIFIER_URL, json=req)

    if resp.status_code != 200:
        raise HTTPException(status_code=403, detail="Invalid ZK proof")

    now = int(time.time())
    payload = {
        "iss": "idp-service",
        "iat": now,
        "exp": now + TOKEN_TTL,
        "scope": "age_balance_verified"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

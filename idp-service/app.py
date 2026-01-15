from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import time
from jose import jwt

app = FastAPI(title="Identity Provider (IdP)")

SECRET_KEY = "SUPER_SECRET_IDP_KEY"
ALGORITHM = "HS256"
TOKEN_TTL = 60  # seconds


class ProofRequest(BaseModel):
    user_id: str
    age: int
    balance: int


def generate_fake_zkp(user_id: str, age: int, balance: int) -> str:
    condition_met = (age >= 18) and (balance >= 1000)
    payload = f"{user_id}|{condition_met}|{time.time()}"
    return hashlib.sha256(payload.encode()).hexdigest()


@app.post("/generate-proof")
def generate_proof(req: ProofRequest):
    proof = generate_fake_zkp(req.user_id, req.age, req.balance)

    payload = {
        "proof": proof,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_TTL,
        "iss": "idp-service"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

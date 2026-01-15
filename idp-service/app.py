from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import time

app = FastAPI(title="Identity Provider (IdP)")

class ProofRequest(BaseModel):
    user_id: str
    age: int
    balance: int

class ProofResponse(BaseModel):
    proof: str
    issued_at: int

def generate_fake_zkp(user_id: str, age: int, balance: int) -> str:
    condition_met = (age >= 18) and (balance >= 1000)
    payload = f"{user_id}|{condition_met}|{time.time()}"
    return hashlib.sha256(payload.encode()).hexdigest()

@app.post("/generate-proof", response_model=ProofResponse)
def generate_proof(req: ProofRequest):
    proof = generate_fake_zkp(req.user_id, req.age, req.balance)
    return {
        "proof": proof,
        "issued_at": int(time.time())
    }

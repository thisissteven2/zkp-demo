from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class VerifyRequest(BaseModel):
    token: str

@app.post("/verify-proof")
def verify_proof(req: VerifyRequest):
    # Stage 1: always valid
    return {
        "valid": True
    }

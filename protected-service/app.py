from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

app = FastAPI(title="Protected Service")

# ---- Request Model ----
class AccessRequest(BaseModel):
    proof: str
    issued_at: int

# ---- Fake Proof Verifier ----
def verify_fake_zkp(proof: str, issued_at: int) -> bool:
    """
    Simulates verification of a ZKP proof.
    """
    now = int(time.time())

    # Reject old proofs (replay protection)
    if now - issued_at > 60:
        return False

    # For now, any non-empty proof is considered valid
    return len(proof) > 0


# ---- Protected Endpoint ----
@app.post("/access-resource")
def access_resource(req: AccessRequest):
    is_valid = verify_fake_zkp(req.proof, req.issued_at)

    if not is_valid:
        raise HTTPException(status_code=403, detail="Invalid or expired proof")

    return {
        "status": "ACCESS_GRANTED",
        "message": "You may access the protected resource"
    }

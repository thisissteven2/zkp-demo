from fastapi import FastAPI, HTTPException, Header
from jose import jwt, JWTError
import time

app = FastAPI(title="Protected Service")

SECRET_KEY = "SUPER_SECRET_IDP_KEY"
ALGORITHM = "HS256"

@app.post("/access-resource")
def access_resource(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    proof = payload.get("proof")
    if not proof:
        raise HTTPException(status_code=403, detail="Missing proof")

    return {
        "status": "ACCESS_GRANTED",
        "issuer": payload.get("iss"),
        "issued_at": payload.get("iat")
    }

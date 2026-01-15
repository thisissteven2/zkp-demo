from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from jose import jwt, JWTError
import time

app = FastAPI(title="Protected Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc)
    allow_headers=["*"],  # Allow all headers
)

# MUST match idp-service
SECRET_KEY = "SUPER_SECRET_IDP_KEY"
ALGORITHM = "HS256"
TRUSTED_ISSUER = "idp-service"

class TokenRequest(BaseModel):
    token: str

@app.post("/access-resource")
def access_resource(req: TokenRequest):
    token = req.token

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        # 2. Verify JWT signature
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 3. Verify issuer
        if payload.get("iss") != TRUSTED_ISSUER:
            raise HTTPException(status_code=403, detail="Untrusted issuer")

        # 4. Verify expiration
        if payload.get("exp") < time.time():
            raise HTTPException(status_code=403, detail="Token expired")

        # 5. Verify ZK approval flag
        if payload.get("zk_verified") is not True:
            raise HTTPException(status_code=403, detail="ZK proof not verified")

    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

    # 6. Grant access
    return {
        "status": "ACCESS_GRANTED",
        "issuer": payload["iss"],
        "issued_at": payload["iat"]
    }

from fastapi import FastAPI, HTTPException, Header
from jose import jwt, JWTError
import time

app = FastAPI(title="Protected Service")

# MUST match idp-service
SECRET_KEY = "SUPER_SECRET_IDP_KEY"
ALGORITHM = "HS256"
TRUSTED_ISSUER = "idp-service"


@app.post("/access-resource")
def access_resource(authorization: str = Header(...)):
    # 1. Check Authorization header format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.replace("Bearer ", "")

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

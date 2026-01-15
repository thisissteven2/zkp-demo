from fastapi import FastAPI, Header, HTTPException
import requests

app = FastAPI()

VERIFIER_URL = "http://localhost:6000/verify-proof"

@app.post("/protected-action")
def protected_action(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    response = requests.post(
        VERIFIER_URL,
        json={"token": token}
    )

    result = response.json()

    if result.get("valid"):
        return {"status": "access granted"}
    else:
        raise HTTPException(status_code=403, detail="Access denied")

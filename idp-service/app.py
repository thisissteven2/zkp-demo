from fastapi import FastAPI

app = FastAPI()

@app.post("/generate-proof")
def generate_proof():
    # Stage 1: return fake token
    return {
        "token": "FAKE_TOKEN_STAGE_1"
    }

# Project Setup Guide

This document explains how to set up and run the Zero-Knowledge Proof (ZKP) demo project locally.

---

## Prerequisites

- Node.js and npm installed (for zkp folder)
- `circom` installed globally (download from https://github.com/iden3/circom/releases)
- Python 3 and pip installed (for backend services)
- `uvicorn` installed for running FastAPI services

---

## Step 1: Setup ZKP Folder (Manual step before running the script)

1. Open terminal and navigate to the `zkp` folder:

    ```bash
    cd zkp
    ```

2. Install global and local dependencies:

    ```bash
    npm install -g snarkjs
    npm install
    ```

3. Make sure `circom` is installed globally and accessible from your shell.

    ```bash
    circom --version
    ```

Once these steps are done, proceed to the next step.

## Step 2: Run the automated setup script

Back in the root project folder, run the setup script:

```bash
./setup.sh
```

The script will:
- Check if the ZKP build artifacts (`build` folder and required files) exist and are valid.
- If missing or incomplete, it will run the necessary commands to compile the circuit, run the trusted setup, generate keys, and prepare everything for proof generation.
- Set up and start all backend services.
- Open the frontend `index.html` file in your default browser.

## Step 3: Service Setup and Running

The script will:
- Enter each service folder (`proof-service`, `verification-service`, `identity-provider`, etc.).
- Create and activate a Python virtual environment (if not exists).
- Install Python dependencies from `requirements.txt`.
- Run the services with `uvicorn` on their respective ports.

## Step 4: Access the Frontend

After all services are running, the script will open the frontend index.html file directly in your browser.

**Note:** The frontend opens the file path directly (no live server required). Make sure your browser allows JS to make requests to the backend services at `localhost`.

## Manual Notes

- The mathematical constraint enforced is that the user must be at least 18 years old and have a balance greater than 1000. This constraint can be changed by making modifications to the file `./zkp/circuit/age_balance.circom`.
- Ensure all services run on their respective ports:
    - Identity Provider service: 5000
    - Protected Resource service: 5001
    - Verifier service: 5002
    - Proof generation service: 5003
- If you make any changes in the zkp circuit or related files, rerun the setup script to rebuild.
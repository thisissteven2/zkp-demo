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

## Step 2: Run the Automated Setup Script

Back in the root project folder, run the setup script:

```bash
./setup.sh
```

The script will:
- Check if the ZKP build artifacts (`build` folder and required files) exist and are valid.
- If missing or incomplete, it will compile the circuit, run the trusted setup, generate keys, and prepare everything for proof generation.
- Create Python virtual environments for backend services if not present.
- Install backend service dependencies.

> Note: `setup.sh` does not start the backend services.

## Step 3: Running Backend Services

After the setup completes, start all backend services and open the frontend in your browser by running:

```bash
./run.sh
```

This script will:
- Activate each service's virtual environment.
- Start all backend services on their respective ports:
    - Identity Provider service: `5000`
    - Protected Resource service: `5001`
    - Verifier service: `5002`
    - Proof Generation service: `5003`
- Open the frontend `index.html` in your default browser.

## Step 4: Rebuild ZKP Artifacts (After Circuit Changes)

If you make any changes to the ZKP circuit file zkp/circuit/age_balance.circom or related files, run the rebuild script to regenerate the ZKP build artifacts without reinstalling backend dependencies:

```bash
./rebuild-zkp.sh
```

This script will:
- Recompile the circuit.
- Rerun the trusted setup and key generation steps.
- Copy the updated verification key to the verifier service folder.

## Additional Notes

- The mathematical constraint enforced is that the user must be at least 18 years old and have a balance greater than 1000. This constraint can be changed by editing `./zkp/circuit/age_balance.circom`.
- The frontend runs as a static file (`index.html`), so no live server is needed. Make sure your browser allows JS requests to the backend services running on localhost.
- To stop backend services, kill their running processes or close the terminal windows.
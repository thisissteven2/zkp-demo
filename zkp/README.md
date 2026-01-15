Prerequisites:
Install circom from https://github.com/iden3/circom/releases

Run the below command to install both global and local project dependencies:

```bash
npm install -g snarkjs
npm install
```

Compile formal constraint system (./circuit/age_balance.circom) into R1CS using the command below:

```bash
circom circuit/age_balance.circom \
  --r1cs --wasm --sym \
  -l node_modules \
  -o build
```
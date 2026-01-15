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

After compiling the circuit into R1CS, a Groth16 trusted setup was performed. The setup used prepared Powers of Tau parameters to generate a circuit-specific proving key. A verification key was then exported for use by the verifier service.

Complete commands run are as seen below:

```bash
# under the /ptau folder
 snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
 snarkjs powersoftau contribute pot12_0000.ptau pot12_final.ptau --name="Steven" -v
 snarkjs powersoftau verify pot12_final.ptau
```

```bash
cd ../build
snarkjs powersoftau prepare phase2 \
   ../ptau/pot12_final.ptau \
   ../ptau/pot12_final_phase2.ptau

snarkjs groth16 setup \
   age_balance.r1cs \
   ../ptau/pot12_final_phase2.ptau \
   age_balance_0000.zkey

snarkjs zkey contribute \
   age_balance_0000.zkey \
   age_balance_final.zkey \
   --name="Steven contribution" \
   -e="random_entropy_123"

snarkjs zkey export verificationkey \
   age_balance_final.zkey \
   verification_key.json
```

Still inside `./build` folder, create `input.json`:

```json
// Assertion will fail if age < 18 or balance < 1000
{
	"age": 22,
	"balance": 5000,
	"valid": 1
}
```

Run the following commands to verify the proof:

```bash
node age_balance_js/generate_witness.js \
  age_balance_js/age_balance.wasm \
  input.json \
  witness.wtns

snarkjs groth16 prove \
  age_balance_final.zkey \
  witness.wtns \
  proof.json \
  public.json

snarkjs groth16 verify \
  verification_key.json \
  public.json \
  proof.json
```

Still inside `./build` folder, copy the verification key to our `verifier-service` folder:

```bash
cp verification_key.json ../../verifier-service/
```

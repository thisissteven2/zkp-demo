async function generateProof(age, balance) {
	try {
		const resp = await fetch("http://localhost:5003/generate-proof", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ age, balance }),
		});

		const data = await resp.json();
		return { proof: data.proof, publicSignals: data.public };
	} catch (error) {
		console.error("generateProof error:", error);
		throw error;
	}
}

async function issueJWT(proof, publicSignals) {
	try {
		const resp = await fetch("http://localhost:5000/issue-token", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ proof, public: publicSignals }),
		});

		const data = await resp.json();
		return data.access_token;
	} catch (error) {
		console.error("issueJWT error:", error);
		throw error;
	}
}

async function callProtectedService(accessToken) {
	try {
		const resp = await fetch("http://localhost:5001/access-resource", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token: accessToken }),
		});

		const data = await resp.json();
		return {
			status: data.status,
			issuer: data.issuer,
			issuedAt: data.issued_at,
		};
	} catch (error) {
		console.error("issueJWT error:", error);
		throw error;
	}
}

document.addEventListener("DOMContentLoaded", () => {
	const form = document.getElementById("zkpForm");
	const resultElem = document.getElementById("result");

	form.addEventListener("submit", async (e) => {
		e.preventDefault();
		resultElem.textContent = "Working...\n\n";

		const age = parseInt(form.age.value, 10);
		const balance = parseInt(form.balance.value, 10);

		try {
			// 1. Generate the zero-knowledge proof by calling your backend
			resultElem.textContent += "Step 1: Generating zero-knowledge proof...\n\n";
			const { proof, publicSignals } = await generateProof(age, balance);

			resultElem.textContent += `Proof snippet:\n${JSON.stringify(proof.pi_a || proof, null, 2)}\n\n`;
			resultElem.textContent += `Public signals:\n${JSON.stringify(publicSignals, null, 2)}\n\n`;

			// 2. Call IdP to issue JWT token by verifying proof
			resultElem.textContent += "Step 2: Requesting JWT token...\n\n";
			const accessToken = await issueJWT(proof, publicSignals);

			resultElem.textContent += `Access token:\n${accessToken}\n\n`;

			// 3. Call protected service with JWT token
			resultElem.textContent += "Step 3: Accessing protected resource with token...\n\n";
			const protectedResult = await callProtectedService(accessToken);

			const { status, issuer, issuedAt } = protectedResult;
			resultElem.textContent += `Status: ${status}\nIssuer: ${issuer}\nIssued At: ${issuedAt}\n`;
		} catch (error) {
			resultElem.textContent += "Error: Failed to generate proof or access resource.\n\n";
			resultElem.textContent += "Error details: " + error.message;
		}
	});
});

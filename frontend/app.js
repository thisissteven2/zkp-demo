async function generateProof(age, balance) {
	try {
		const resp = await fetch("http://localhost:9000/generate-proof", {
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
		const resp = await fetch("http://localhost:6000/access-resource", {
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
		resultElem.textContent = "Working...";

		const age = parseInt(form.age.value, 10);
		const balance = parseInt(form.balance.value, 10);

		try {
			// 1. Generate the zero-knowledge proof by calling your backend
			const { proof, publicSignals } = await generateProof(age, balance);

			// 2. Call IdP to issue JWT token by verifying proof
			const accessToken = await issueJWT(proof, publicSignals);

			// 3. Call protected service with JWT token
			const protectedResult = await callProtectedService(accessToken);

			// resultElem.textContent = JSON.stringify(protectedResult, null, 2);
		} catch (error) {
			resultElem.textContent = "Error: " + error.message;
		}
	});
});

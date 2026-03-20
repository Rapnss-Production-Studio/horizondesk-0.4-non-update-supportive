const apiUrl = "https://horizon-online.api-rapnss.workers.dev/api/auth/oauth-sync";

async function testSync() {
    try {
        const res = await fetch(apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: "test1234",
                email: "test@example.com",
                name: "Test User"
            })
        });
        
        const data = await res.text();
        console.log("Status:", res.status);
        console.log("Response:", data);
    } catch (e) {
        console.error(e);
    }
}

testSync();

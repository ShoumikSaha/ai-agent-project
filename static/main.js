document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("website-form");
    const responseEl = document.getElementById("response");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const website = document.getElementById("website").value;
        responseEl.textContent = "Thinking...";

        try {
            const res = await fetch("/api/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ website })
            });
            const data = await res.json();
            if (data.response) {
                responseEl.textContent = data.response;
            } else {
                responseEl.textContent = data.error || "Unknown error";
            }
        } catch (err) {
            responseEl.textContent = "Request failed: " + err.message;
        }
    });
});
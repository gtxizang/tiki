/* JSON-LD display, copy, and download */

function displayJsonLd(data) {
    const codeEl = document.getElementById("jsonld-output");
    if (!codeEl || !data.jsonld) return;
    codeEl.textContent = JSON.stringify(data.jsonld, null, 2);
}

function displaySummary(data) {
    const container = document.getElementById("summary-content");
    if (!container || !data.jsonld) return;

    const dataset = data.jsonld["@graph"]?.[0] || data.jsonld;

    const items = [];

    if (dataset["dct:title"]) {
        items.push(["Title", dataset["dct:title"]]);
    }

    if (dataset["dct:description"]) {
        const desc = dataset["dct:description"];
        items.push(["Description", desc.length > 150 ? desc.slice(0, 150) + "..." : desc]);
    }

    if (dataset["dct:language"]) {
        items.push(["Language", dataset["dct:language"]]);
    }

    if (dataset["dct:creator"]?.["foaf:name"]) {
        items.push(["Creator", dataset["dct:creator"]["foaf:name"]]);
    }

    const distribution = dataset["dcat:distribution"]?.[0];
    if (distribution) {
        if (distribution["dcat:mediaType"]) {
            items.push(["Media Type", distribution["dcat:mediaType"]]);
        }
    }

    container.innerHTML = items
        .map(
            ([label, value]) => `
        <div class="summary-item">
            <span class="summary-item__label">${label}</span>
            <span class="summary-item__value">${value}</span>
        </div>
    `
        )
        .join("");

    // Keywords
    const keywords = dataset["dcat:keyword"] || [];
    if (keywords.length > 0) {
        container.innerHTML += `
            <div class="summary-item" style="flex-direction: column; gap: 0.5rem;">
                <span class="summary-item__label">Keywords</span>
                <div class="tag-list">
                    ${keywords.map((k) => `<span class="tag">${k}</span>`).join("")}
                </div>
            </div>
        `;
    }
}

function copyJsonLd() {
    const codeEl = document.getElementById("jsonld-output");
    if (!codeEl) return;
    navigator.clipboard.writeText(codeEl.textContent).then(() => {
        const btn = document.querySelector("[onclick='copyJsonLd()']");
        if (btn) {
            const original = btn.textContent;
            btn.textContent = "Copied!";
            setTimeout(() => (btn.textContent = original), 1500);
        }
    });
}

function downloadJsonLd() {
    const codeEl = document.getElementById("jsonld-output");
    if (!codeEl) return;
    const blob = new Blob([codeEl.textContent], { type: "application/ld+json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "dcat-ap.jsonld";
    a.click();
    URL.revokeObjectURL(url);
}

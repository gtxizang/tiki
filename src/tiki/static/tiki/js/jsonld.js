/* JSON-LD display, copy, and download */

function displayJsonLd(data) {
    var codeEl = document.getElementById("jsonld-output");
    if (!codeEl || !data.jsonld) return;
    codeEl.textContent = JSON.stringify(data.jsonld, null, 2);
}

function displaySummary(data) {
    var container = document.getElementById("summary-content");
    if (!container || !data.jsonld) return;

    var dataset = data.jsonld["@graph"] ? data.jsonld["@graph"][0] : data.jsonld;
    var items = [];

    if (dataset["dct:title"]) {
        items.push(["Title", dataset["dct:title"]]);
    }
    if (dataset["dct:description"]) {
        var desc = dataset["dct:description"];
        items.push(["Description", desc.length > 150 ? desc.slice(0, 150) + "..." : desc]);
    }
    if (dataset["dct:language"]) {
        items.push(["Language", dataset["dct:language"]]);
    }
    if (dataset["dct:creator"] && dataset["dct:creator"]["foaf:name"]) {
        items.push(["Creator", dataset["dct:creator"]["foaf:name"]]);
    }
    var distribution = dataset["dcat:distribution"] ? dataset["dcat:distribution"][0] : null;
    if (distribution && distribution["dcat:mediaType"]) {
        items.push(["Media Type", distribution["dcat:mediaType"]]);
    }

    container.innerHTML = items
        .map(function (pair) {
            return '<div class="flex justify-between py-2 border-b" style="border-color: var(--colour-border);">' +
                '<span class="text-sm font-medium" style="color: var(--colour-text);">' + pair[0] + '</span>' +
                '<span class="text-sm text-right max-w-[60%]" style="color: var(--colour-text-muted);">' + pair[1] + '</span>' +
                '</div>';
        })
        .join("");

    // Keywords
    var keywords = dataset["dcat:keyword"] || [];
    if (keywords.length > 0) {
        container.innerHTML +=
            '<div class="pt-3">' +
            '<span class="text-sm font-medium" style="color: var(--colour-text);">Keywords</span>' +
            '<div class="flex flex-wrap gap-2 mt-2">' +
            keywords.map(function (k) {
                return '<span class="inline-block px-3 py-1 text-xs rounded-full" ' +
                    'style="background: var(--colour-bg-secondary); color: var(--colour-text-muted);">' + k + '</span>';
            }).join("") +
            '</div></div>';
    }
}

function copyJsonLd() {
    var codeEl = document.getElementById("jsonld-output");
    if (!codeEl) return;
    navigator.clipboard.writeText(codeEl.textContent).then(function () {
        var btn = document.querySelector("[onclick='copyJsonLd()']");
        if (btn) {
            var original = btn.textContent;
            btn.textContent = "Copied!";
            setTimeout(function () { btn.textContent = original; }, 1500);
        }
    });
}

function downloadJsonLd() {
    var codeEl = document.getElementById("jsonld-output");
    if (!codeEl) return;
    var blob = new Blob([codeEl.textContent], { type: "application/ld+json" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "dcat-ap.jsonld";
    a.click();
    URL.revokeObjectURL(url);
}

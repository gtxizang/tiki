/* Edit-in-place for empty DCAT-AP fields */

function displayEmptyFields(data) {
    const container = document.getElementById("empty-fields");
    if (!container) return;

    const emptyFields = data.empty_fields || [];
    if (emptyFields.length === 0) {
        container.innerHTML = "";
        container.closest(".empty-fields")?.classList.remove("active");
        return;
    }

    container.closest(".empty-fields")?.classList.add("active");

    const labels = {
        "dct:license": "License",
        "dct:publisher": "Publisher",
        "dcat:contactPoint": "Contact Point",
    };

    container.innerHTML = emptyFields
        .map(
            (field) => `
        <div class="empty-field-row">
            <label>${labels[field] || field}</label>
            <input type="text" data-field="${field}" placeholder="Enter ${labels[field] || field}...">
            <button onclick="saveField(this, '${field}')">Save</button>
        </div>
    `
        )
        .join("");
}

async function saveField(btn, fieldName) {
    const input = btn.parentElement.querySelector("input");
    const value = input.value.trim();
    if (!value) return;

    const uploadId = window.tikiResult?.id;
    if (!uploadId) return;

    btn.disabled = true;
    btn.textContent = "Saving...";

    try {
        const response = await fetch(`/api/result/${uploadId}/edit/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field: fieldName, value }),
        });

        const data = await response.json();

        if (response.ok) {
            window.tikiResult.jsonld = data.jsonld;
            window.tikiResult.empty_fields = data.empty_fields;

            if (typeof displayJsonLd === "function") {
                displayJsonLd(window.tikiResult);
            }
            displayEmptyFields(window.tikiResult);
        } else {
            alert(data.error || "Failed to save");
            btn.disabled = false;
            btn.textContent = "Save";
        }
    } catch (err) {
        alert("Network error: " + err.message);
        btn.disabled = false;
        btn.textContent = "Save";
    }
}

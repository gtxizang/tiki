/* Edit-in-place for empty DCAT-AP fields */

function displayEmptyFields(data) {
    var container = document.getElementById("empty-fields");
    var section = container ? container.closest(".empty-fields-section") : null;
    if (!container) return;

    var emptyFields = data.empty_fields || [];
    if (emptyFields.length === 0) {
        container.innerHTML = "";
        if (section) section.classList.remove("active");
        return;
    }

    if (section) section.classList.add("active");

    var labels = {
        "dct:license": "License",
        "dct:publisher": "Publisher",
        "dcat:contactPoint": "Contact Point",
    };

    container.innerHTML = emptyFields
        .map(function (field) {
            return '<div class="flex items-center gap-3 mb-3">' +
                '<label class="text-sm font-medium min-w-36" style="color: var(--colour-text);">' +
                (labels[field] || field) + '</label>' +
                '<input type="text" data-field="' + field + '" ' +
                'placeholder="Enter ' + (labels[field] || field) + '..." ' +
                'class="flex-1 px-3 py-2 text-sm rounded border" ' +
                'style="border-color: var(--colour-border); background: var(--colour-bg-secondary); color: var(--colour-text);">' +
                '<button onclick="saveField(this, \'' + field + '\')" ' +
                'class="px-4 py-2 text-sm font-medium text-white rounded transition-colors" ' +
                'style="background: var(--colour-link);" ' +
                'onmouseover="this.style.background=\'var(--colour-link-hover)\'" ' +
                'onmouseout="this.style.background=\'var(--colour-link)\'">Save</button>' +
                '</div>';
        })
        .join("");
}

async function saveField(btn, fieldName) {
    var input = btn.parentElement.querySelector("input");
    var value = input.value.trim();
    if (!value) return;

    var uploadId = window.tikiResult && window.tikiResult.id;
    if (!uploadId) return;

    btn.disabled = true;
    btn.textContent = "Saving...";

    try {
        var response = await fetch("/api/result/" + uploadId + "/edit/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field: fieldName, value: value }),
        });

        var data = await response.json();

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

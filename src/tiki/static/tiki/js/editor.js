/* Edit-in-place for DCAT-AP required fields */

var LICENCES = [
    { uri: "https://creativecommons.org/publicdomain/zero/1.0/", label: "CC0 1.0 — Public domain" },
    { uri: "https://creativecommons.org/licenses/by/4.0/", label: "CC BY 4.0 — Attribution" },
    { uri: "https://creativecommons.org/licenses/by-sa/4.0/", label: "CC BY-SA 4.0 — Attribution, share-alike" },
    { uri: "https://creativecommons.org/licenses/by-nc/4.0/", label: "CC BY-NC 4.0 — Attribution, non-commercial" },
    { uri: "https://creativecommons.org/licenses/by-nc-sa/4.0/", label: "CC BY-NC-SA 4.0 — Attribution, non-commercial, share-alike" },
    { uri: "https://creativecommons.org/licenses/by-nd/4.0/", label: "CC BY-ND 4.0 — Attribution, no derivatives" },
    { uri: "https://creativecommons.org/licenses/by-nc-nd/4.0/", label: "CC BY-NC-ND 4.0 — Most restrictive" },
    { uri: "https://data.gov.ie/pages/opendatalicence", label: "Irish PSI Licence" },
    { uri: "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/", label: "OGL v3.0 — UK Open Government" },
    { uri: "https://opensource.org/licenses/MIT", label: "MIT — Permissive software licence" },
];

var ALL_FIELDS = ["dct:license", "dct:publisher", "dcat:contactPoint"];
var FIELD_LABELS = {
    "dct:license": "License",
    "dct:publisher": "Publisher",
    "dcat:contactPoint": "Contact Point",
};

function escapeAttr(s) {
    return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;");
}

function buildLicenceSelect(currentValue) {
    var options = '<option value="">Select a licence...</option>';
    LICENCES.forEach(function (l) {
        var selected = l.uri === currentValue ? " selected" : "";
        options += '<option value="' + escapeAttr(l.uri) + '"' + selected + '>' + l.label + '</option>';
    });
    return '<select data-field="dct:license" ' +
        'class="flex-1 px-3 py-2 text-sm rounded border" ' +
        'style="border-color: var(--colour-border); background: var(--colour-bg-secondary); color: var(--colour-text);">' +
        options + '</select>';
}

function buildTextInput(field, label, currentValue) {
    return '<input type="text" data-field="' + field + '" ' +
        'value="' + escapeAttr(currentValue) + '" ' +
        'placeholder="Enter ' + label + '..." ' +
        'class="flex-1 px-3 py-2 text-sm rounded border" ' +
        'style="border-color: var(--colour-border); background: var(--colour-bg-secondary); color: var(--colour-text);">';
}

function displayEmptyFields(data) {
    var container = document.getElementById("empty-fields");
    var section = container ? container.closest(".empty-fields-section") : null;
    if (!container) return;

    if (section) section.classList.add("active");

    var edits = (data.jsonld && data.jsonld["@graph"] && data.jsonld["@graph"][0]) || {};

    container.innerHTML = ALL_FIELDS
        .map(function (field) {
            var currentValue = edits[field] || "";
            // Objects (like empty placeholders) aren't real values
            if (typeof currentValue === "object") currentValue = "";

            var label = FIELD_LABELS[field] || field;
            var inputHtml = field === "dct:license"
                ? buildLicenceSelect(currentValue)
                : buildTextInput(field, label, currentValue);

            var savedIndicator = currentValue
                ? '<span class="text-xs" style="color: var(--colour-text-muted);">Saved</span>'
                : '';

            return '<div class="flex items-center gap-3 mb-3">' +
                '<label class="text-sm font-medium min-w-36" style="color: var(--colour-text);">' +
                label + '</label>' +
                inputHtml +
                '<button onclick="saveField(this, \'' + field + '\')" ' +
                'class="px-4 py-2 text-sm font-medium text-white rounded transition-colors" ' +
                'style="background: var(--colour-link);" ' +
                'onmouseover="this.style.background=\'var(--colour-link-hover)\'" ' +
                'onmouseout="this.style.background=\'var(--colour-link)\'">Save</button>' +
                savedIndicator +
                '</div>';
        })
        .join("");
}

async function saveField(btn, fieldName) {
    var input = btn.parentElement.querySelector("select, input");
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
        }
    } catch (err) {
        alert("Network error: " + err.message);
    }

    btn.disabled = false;
    btn.textContent = "Save";
}

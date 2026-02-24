document.addEventListener("DOMContentLoaded", function () {
    var zone = document.getElementById("upload-zone");
    var input = document.getElementById("file-input");
    var progressBar = document.querySelector(".progress-bar");
    var progressFill = document.querySelector(".progress-fill");
    var progressStatus = document.querySelector(".progress-status");
    var errorMessage = document.querySelector(".error-message");
    var resultSection = document.querySelector(".result-section");

    if (!zone || !input) return;

    zone.addEventListener("click", function () { input.click(); });

    zone.addEventListener("dragover", function (e) {
        e.preventDefault();
        zone.classList.add("dragover");
    });

    zone.addEventListener("dragleave", function () {
        zone.classList.remove("dragover");
    });

    zone.addEventListener("drop", function (e) {
        e.preventDefault();
        zone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    input.addEventListener("change", function () {
        if (input.files.length > 0) {
            uploadFile(input.files[0]);
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.add("active");
        progressBar.classList.remove("active");
        zone.classList.remove("uploading");
    }

    function setProgress(percent, status) {
        progressFill.style.width = percent + "%";
        progressStatus.textContent = status;
    }

    async function uploadFile(file) {
        errorMessage.classList.remove("active");
        resultSection.classList.remove("active");
        zone.classList.add("uploading");
        progressBar.classList.add("active");

        setProgress(10, "Uploading file...");

        var formData = new FormData();
        formData.append("file", file);

        try {
            setProgress(30, "Extracting metadata with Tika...");

            var response = await fetch("/api/enrich/", {
                method: "POST",
                body: formData,
            });

            setProgress(80, "Processing response...");

            var data = await response.json();

            if (!response.ok) {
                showError(data.error || "Upload failed");
                return;
            }

            setProgress(100, "Complete!");
            zone.classList.remove("uploading");

            window.tikiResult = data;
            displayResult(data);
        } catch (err) {
            showError("Network error: " + err.message);
        }
    }

    function displayResult(data) {
        resultSection.classList.add("active");

        if (typeof displaySummary === "function") {
            displaySummary(data);
        }
        if (typeof displayJsonLd === "function") {
            displayJsonLd(data);
        }
        if (typeof displayEmptyFields === "function") {
            displayEmptyFields(data);
        }
    }
});

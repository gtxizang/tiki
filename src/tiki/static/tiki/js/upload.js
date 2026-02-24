document.addEventListener("DOMContentLoaded", () => {
    const zone = document.getElementById("upload-zone");
    const input = document.getElementById("file-input");
    const progressBar = document.querySelector(".progress-bar");
    const progressFill = document.querySelector(".progress-bar__fill");
    const progressStatus = document.querySelector(".progress-bar__status");
    const errorMessage = document.querySelector(".error-message");
    const resultSection = document.querySelector(".result-section");

    if (!zone || !input) return;

    zone.addEventListener("click", () => input.click());

    zone.addEventListener("dragover", (e) => {
        e.preventDefault();
        zone.classList.add("dragover");
    });

    zone.addEventListener("dragleave", () => {
        zone.classList.remove("dragover");
    });

    zone.addEventListener("drop", (e) => {
        e.preventDefault();
        zone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    input.addEventListener("change", () => {
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

        const formData = new FormData();
        formData.append("file", file);

        try {
            setProgress(30, "Extracting metadata with Tika...");

            const response = await fetch("/api/enrich/", {
                method: "POST",
                body: formData,
            });

            setProgress(80, "Processing response...");

            const data = await response.json();

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

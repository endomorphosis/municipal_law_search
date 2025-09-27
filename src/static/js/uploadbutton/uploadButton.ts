/**
 * Handles the file upload to the FastAPI backend.
 * @param file The file to upload.
 */
async function uploadDocument(file: File): Promise<void> {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload_document", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            console.log("Upload successful:", result);
            alert("File uploaded successfully!");
        } else {
            const errorText = await response.text();
            console.error("Upload failed:", response.statusText, errorText);
            alert(`Upload failed: ${errorText}`);
        }
    } catch (error) {
        console.error("An error occurred during upload:", error);
        alert("An error occurred during upload. Please check the console.");
    }
}

/**
 * Creates and configures the upload button and its associated file input.
 * @param container The HTML element to which the button will be appended.
 */
export function setupUploadButton(container: HTMLElement): void {
    // Create a hidden file input element
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.style.display = "none";

    // Restrict file types, e.g., to PDFs and Word documents
    fileInput.accept = ".pdf,.doc,.docx,text/plain";

    // Create the visible upload button
    const uploadButton = document.createElement("button");
    uploadButton.textContent = "Upload Document";

    // When the button is clicked, trigger the file input's click event
    uploadButton.addEventListener("click", () => {
        fileInput.click();
    });

    // When a file is selected in the file input
    fileInput.addEventListener("change", () => {
        const files = fileInput.files;
        if (files && files.length > 0) {
            const file = files[0];
            uploadDocument(file);
        }
        // Reset the input value to allow uploading the same file again
        fileInput.value = "";
    });

    // Append both elements to the provided container
    container.appendChild(uploadButton);
    container.appendChild(fileInput);
}

// Example usage:
// This assumes you have an element with the id 'upload-container' in your HTML.
// document.addEventListener('DOMContentLoaded', () => {
//     const uploadContainer = document.getElementById('upload-container');
//     if (uploadContainer) {
//         setupUploadButton(uploadContainer);
//     }
// });
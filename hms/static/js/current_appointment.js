// Function to search for a patient by ID or name
function searchPatient() {
    const searchInput = document.getElementById("patientSearch").value.trim();
    const currentAppointmentSection = document.getElementById("currentAppointment");
    const currentPatientName = document.getElementById("currentPatientName");
    const currentPatientId = document.getElementById("currentPatientId");
    const appointmentDetails = document.getElementById("appointmentDetails");

    // Clear previous details
    currentPatientName.textContent = "";
    currentPatientId.textContent = "";
    appointmentDetails.innerHTML = "";
    appointmentDetails.style.display = "none";

    if (!searchInput) {
        alert("Please enter a patient ID or name to search.");
        return;
    }

    // Simulate fetching patient data (replace this with an actual API call)
    fetch(`/search_patient?query=${encodeURIComponent(searchInput)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error fetching patient data");
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.patient) {
                // Populate patient details
                currentPatientName.textContent = data.patient.name;
                currentPatientId.textContent = data.patient.id;

                // Populate appointment details
                const appointmentHTML = `
                    <h3>Appointment Details</h3>
                    <p>Consultation Date: ${data.patient.consultationDate || "N/A"}</p>
                    <p>Diagnosis: ${data.patient.diagnosis || "N/A"}</p>
                    <p>Treatment: ${data.patient.treatment || "N/A"}</p>
                `;
                appointmentDetails.innerHTML = appointmentHTML;
                appointmentDetails.style.display = "block";
            } else {
                alert("No patient found with the provided ID or name.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while searching for the patient.");
        });
}

// Document upload form submission handler
document.getElementById("documentUploadForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);

    // Simulate document upload (replace with actual API call)
    fetch("/upload_document", {
        method: "POST",
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error uploading document");
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert("Document uploaded successfully!");
                this.reset(); // Reset the form after successful upload
            } else {
                alert("Failed to upload document.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while uploading the document.");
        });
});

// Prescription form submission handler
document.getElementById("prescriptionForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);

    // Simulate prescription saving (replace with actual API call)
    fetch("/save_prescription", {
        method: "POST",
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error saving prescription");
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert("Prescription saved successfully!");
                this.reset(); // Reset the form after successful save
            } else {
                alert("Failed to save prescription.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while saving the prescription.");
        });
});

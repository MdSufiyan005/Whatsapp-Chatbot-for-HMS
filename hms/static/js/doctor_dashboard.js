document.addEventListener('DOMContentLoaded', function() {
    // Initialize the page
    loadMedicalRecords();
    
    // Add form submission handlers
    const prescriptionForm = document.getElementById('prescriptionForm');
    if (prescriptionForm) {
        prescriptionForm.addEventListener('submit', handlePrescriptionSubmit);
    }
});
// document.addEventListener('DOMContentLoaded', function() {
//     const searchBar = document.getElementById('patientSearchBar');
//     const patientDetails = document.querySelector('.patient-details');

//     searchBar.addEventListener('keyup', function() {
//         const searchText = searchBar.value.toLowerCase();
//         const patientName = document.getElementById('currentPatientName').textContent.toLowerCase();
//         const patientId = document.getElementById('currentPatientId').textContent.toLowerCase();

//         // Check if the search text matches either the patient name or ID
//         if (patientName.includes(searchText) || patientId.includes(searchText)) {
//             patientDetails.style.display = ''; // Show the patient details if there's a match
//         } else {
//             patientDetails.style.display = 'none'; // Hide if there's no match
//         }
//     });
// });

// function searchPatient() {
//     const searchTerm = document.getElementById('patientSearch').value;
    
//     if (!searchTerm) {
//         alert("Please enter a search term.");
//         return; // Prevents the API call if the search term is empty
//     }

//     fetch(`/api/patient/search?term=${encodeURIComponent(searchTerm)}`)
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         })
//         .then(data => {
//             console.log('Search API response:', data); // Log the response data
//             if (data.success) {
//                 loadPatientHistory(data.patientId); // Call to load patient history
//                 // Load patient details if needed
//                 viewPatientDetails(data.patientId); // Call to load patient details
//             } else {
//                 alert(data.message); // Show error message if patient not found
//             }
//         })
//         .catch(error => console.error('Search error:', error));
// }

function viewPatientDetails(patientId) {
    fetch(`/api/patient/${patientId}`)
        .then(response => response.json())
        .then(data => {
            if(data.success){
                document.getElementById('currentPatientName').textContent=data.patient.patientName;
                document.getElementById('currentPatientName').textContent=data.patient.patientID;
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
}

function loadMedicalRecords() {
    fetch('/api/medical-records')
        .then(response => response.json())
        .then(records => {
            const recordsList = document.getElementById('medicalRecordsList');
            recordsList.innerHTML = records.map(record => `
                <div class="record-item">
                    <span>${record.filename}</span>
                    <span>${record.uploadDate}</span>
                    <button onclick="viewDocument('${record.id}')">View</button>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error:', error));
}

function handlePrescriptionSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    fetch('/api/prescriptions/add', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert('Prescription saved successfully');
    })
    .catch(error => console.error('Error:', error));
}

function viewDocument(documentId) {
    window.open(`/api/documents/${documentId}`, '_blank');
}
document.addEventListener('DOMContentLoaded', function() {
    // Initialize forms
    initializeForms();
    
    // Load current appointment if any
    loadCurrentAppointment();
});


function loadCurrentAppointment() {
    fetch('/api/current-appointment')
        .then(response => response.json())
        .then(data => {
            if (data.appointment) {
                document.getElementById('currentPatientName').textContent = data.patient.name;
                document.getElementById('currentPatientId').textContent = data.patient.id;
                // Enable upload and prescription forms
                enableCurrentAppointmentForms(true);
            } else {
                // No current appointment
                enableCurrentAppointmentForms(false);
            }
        });
}

function loadPatientHistory(patientId) {
    fetch(`/api/patient/${patientId}/history`)
        .then(response => response.json())
        .then(data => {
            console.log('Patient history API response:', data); // Log the response data
            const tbody = document.querySelector('#historyTable tbody');
            tbody.innerHTML = ''; // Clear existing rows

            // Check if appointments exist
            if (data.appointments && data.appointments.length > 0) {
                // Populate the table with appointment data
                data.appointments.forEach(app => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${app.patientID}</td>
                        <td>${app.doctorID}</td>
                        <td>${app.appointment_date}</td>
                        <td>${app.diagnosis || 'N/A'}</td>
                        <td>
                            <button onclick="viewAppointmentDetails('${app.appointmentID}')">View Details</button>
                        </td>
                        <td>
                            <button onclick="viewDocuments('${app.appointmentID}')">View Documents</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } else {
                // If no appointments found, display a message
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="6">No appointment history found for this patient.</td>`;
                tbody.appendChild(row);
            }
        })
        .catch(error => console.error('Error loading patient history:', error));
}

function initializeForms() {
    // Document upload form handler
    document.getElementById('documentUploadForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        fetch('/api/upload-document', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert('Document uploaded successfully');
        })
        .catch(error => console.error('Upload error:', error));
    });

    // Prescription form handler
    document.getElementById('prescriptionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        
        fetch('/api/save-prescription', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert('Prescription saved successfully');
        })
        .catch(error => console.error('Prescription error:', error));
    });
}

function viewAppointmentDetails(appointmentId) {
    fetch(`/api/patient/appointment/${appointmentId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const appointment = data.appointment;
                // Display appointment details in a modal or a dedicated section
                displayAppointmentDetails(appointment);
            } else {
                alert(data.message); // Show error message if appointment not found
            }
        })
        .catch(error => console.error('Error fetching appointment details:', error));
}

function displayAppointmentDetails(appointment) {
    // Assuming you have a modal or a section to display the details
    const detailsSection = document.getElementById('appointmentDetails');
    detailsSection.innerHTML = `
        <h3>Appointment Details</h3>
        <p><strong>Appointment ID:</strong> ${appointment.appointmentID}</p>
        <p><strong>Patient ID:</strong> ${appointment.patientID}</p>
        <p><strong>Doctor ID:</strong> ${appointment.doctorID}</p>
        <p><strong>Date:</strong> ${appointment.appointment_date}</p>
        <p><strong>Diagnosis:</strong> ${appointment.diagnosis || 'N/A'}</p>
        <p><strong>Phone Number:</strong> ${appointment.phone_number}</p>
        <button onclick="closeDetails()">Close</button>
    `;
    detailsSection.style.display = 'block'; // Show the details section
}

function closeDetails() {
    const detailsSection = document.getElementById('appointmentDetails');
    detailsSection.style.display = 'none'; // Hide the details section
}

function enableCurrentAppointmentForms(enable) {
    const forms = document.querySelectorAll('#documentUploadForm, #prescriptionForm');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, button, select');
        inputs.forEach(input => input.disabled = !enable);
    });
}

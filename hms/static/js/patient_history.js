document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patient-search-form');
    const resultsContainer = document.getElementById('results-container');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const searchTerm = form.elements['search_term'].value.trim();

        if (!searchTerm) {
            alert('Please enter a search term.');
            return;
        }

        // Send a POST request to the Flask route
        fetch('/search_patient', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ search_term: searchTerm })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayPatientData(data);
            } else {
                resultsContainer.innerHTML = `<p>${data.message}</p>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultsContainer.innerHTML = `<p>An error occurred while searching for the patient.</p>`;
        });
    });

    function displayPatientData(data) {
        const { patient, appointments, medical_records } = data;

        let html = `
            <h2>Patient Details</h2>
            <table>
                <tr><th>ID</th><td>${patient.patientID}</td></tr>
                <tr><th>Name</th><td>${patient.patientName}</td></tr>
                <tr><th>Contact</th><td>${patient.Contact}</td></tr>
                <tr><th>Email</th><td>${patient.Email}</td></tr>
                <tr><th>DOB</th><td>${patient.DOB}</td></tr>
            </table>
            <h3>Appointments</h3>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Doctor</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${appointments.map(appointment => `
                        <tr>
                            <td>${appointment.appointment_date}</td>
                            <td>${appointment.doctorID}</td>
                            <td>${appointment.status}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            <h3>Medical Records</h3>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Diagnosis</th>
                        <th>Treatment</th>
                    </tr>
                </thead>
                <tbody>
                    ${medical_records.map(record => `
                        <tr>
                            <td>${record.consultationDate}</td>
                            <td>${record.diagnosis}</td>
                            <td>${record.treatment}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        resultsContainer.innerHTML = html;
    }
});
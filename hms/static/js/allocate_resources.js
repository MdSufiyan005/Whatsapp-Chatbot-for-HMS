document.getElementById('allocateForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Gather form data
    const patientId = document.getElementById('patientId').value;
    const resourceType = document.getElementById('resourceType').value;
    const quantity = document.getElementById('quantity').value;
    const requestDate = document.getElementById('requestDate').value;

    // Send data to the server
    fetch('/allocate_resources/allocate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            patientID: patientId,
            resource_id: resourceType,
            quantity: quantity,
            request_date: requestDate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('returnForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Gather form data
    const returnPatientId = document.getElementById('returnPatientId').value;
    const returnResourceType = document.getElementById('returnResourceType').value;
    const returnQuantity = document.getElementById('returnQuantity').value;
    const returnDate = document.getElementById('returnDate').value;

    // Send data to the server
    fetch('/allocate_resources/return', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            patientID: returnPatientId,
            resource_id: returnResourceType,
            quantity: returnQuantity,
            returned_date: returnDate
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
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
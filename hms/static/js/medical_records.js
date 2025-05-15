document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('search-button');
    const searchRecordIdInput = document.getElementById('search-record-id');
    const searchPatientIdInput = document.getElementById('search-patient-id');
    const recordsTable = document.getElementById('records-table').getElementsByTagName('tbody')[0];

    // Function to filter records based on search criteria
    function filterRecords() {
        const recordId = searchRecordIdInput.value.toLowerCase();
        const patientId = searchPatientIdInput.value.toLowerCase();

        Array.from(recordsTable.rows).forEach(row => {
            const recordIdCell = row.cells[0].textContent.toLowerCase();
            const patientIdCell = row.cells[1].textContent.toLowerCase();

            if ((recordId && !recordIdCell.includes(recordId)) || (patientId && !patientIdCell.includes(patientId))) {
                row.style.display = 'none';
            } else {
                row.style.display = '';
            }
        });
    }

    // Event listener for the search button
    searchButton.addEventListener('click', filterRecords);

    // Optional: Add event listeners for 'Enter' key press on search inputs
    searchRecordIdInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            filterRecords();
        }
    });

    searchPatientIdInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            filterRecords();
        }
    });

    // Fetch records from the server
    fetch('/api/records')
        .then(response => response.json())
        .then(data => {
            console.log('Number of records fetched:', data.length); // Log the number of records
            data.forEach(record => {
                const row = recordsTable.insertRow();
                // Assuming record has properties 'recordId' and 'patientId'
                row.insertCell(0).textContent = record.recordId;
                row.insertCell(1).textContent = record.patientId;
                // Add more cells as needed
            });
        })
        .catch(error => console.error('Error fetching records:', error));
});

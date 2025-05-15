document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('searchBtn');
    const searchForm = document.getElementById('searchForm');
    const updateForm = document.getElementById('updateForm');
    const patientUpdateForm = document.getElementById('patientUpdateForm');

    searchBtn.addEventListener('click', function() {
        const patientId = document.getElementById('patient_id').value;
        const dob = document.getElementById('dob').value;
        
        if (!patientId || !dob) {
            alert('Please enter both Patient ID and Date of Birth');
            return;
        }

        const searchUrl = `/search_patient?patient_id=${encodeURIComponent(patientId)}&dob=${encodeURIComponent(dob)}`;
        
        fetch(searchUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('update_patient_id').value = data.patient.patientID;
                    document.getElementById('update_patient_name').value = data.patient.patientName;
                    document.getElementById('update_contact').value = data.patient.Contact;
                    document.getElementById('update_email').value = data.patient.Email;
                    searchForm.classList.add('hidden');
                    updateForm.classList.remove('hidden');
                } else {
                    alert(data.message || 'Patient not found!');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error searching for patient. Please try again.');
            });
    });

    patientUpdateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(patientUpdateForm);
        
        fetch('/update_patient', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Patient details updated successfully!');
                window.location.href = '/patients';
            } else {
                alert('Error updating patient details: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating patient details.');
        });
    });
});

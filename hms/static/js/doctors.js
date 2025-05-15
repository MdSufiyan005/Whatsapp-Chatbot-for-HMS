document.addEventListener('DOMContentLoaded', function() {
    const addDoctorForm = document.getElementById('add-doctor-form');
    const doctorList = document.getElementById('doctor-list');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    // Add new doctor
    addDoctorForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(addDoctorForm);
        
        fetch('/add_doctor', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const newDoctorItem = createDoctorItem(data.doctor);
                doctorList.appendChild(newDoctorItem);
                addDoctorForm.reset();
            } else {
                alert('Error adding doctor: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Search functionality
    function searchDoctors() {
        const searchTerm = searchInput.value.toLowerCase();
        const doctorItems = doctorList.getElementsByClassName('doctor-item');
        
        Array.from(doctorItems).forEach(item => {
            const doctorText = item.textContent.toLowerCase();
            if (doctorText.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    searchButton.addEventListener('click', searchDoctors);
    searchInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            searchDoctors();
        }
    });

    // Helper function to create a new doctor list item
    function createDoctorItem(doctor) {
        const li = document.createElement('li');
        li.className = 'doctor-item';
        li.innerHTML = `
            <strong>${doctor.doctorName}</strong><br>
            Specialty: ${doctor.specialty}<br>
            Qualifications: ${doctor.qualifications}
        `;
        return li;
    }

    // Sort doctors alphabetically
    function sortDoctors() {
        const doctors = Array.from(doctorList.getElementsByClassName('doctor-item'));
        doctors.sort((a, b) => {
            const nameA = a.querySelector('strong').textContent.toLowerCase();
            const nameB = b.querySelector('strong').textContent.toLowerCase();
            return nameA.localeCompare(nameB);
        });
        doctors.forEach(doctor => doctorList.appendChild(doctor));
    }

    sortDoctors();
});

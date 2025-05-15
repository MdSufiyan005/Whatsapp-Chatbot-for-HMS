// static/js/appointments.js
document.addEventListener('DOMContentLoaded', function() {
    const appointmentForm = document.getElementById('appointmentForm');
    const searchForm = document.getElementById('searchForm');
    const appointmentList = document.getElementById('appointmentList');

    // Handle the appointment form submission
    appointmentForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(appointmentForm);

        // Send the form data to the server using Fetch API
        fetch(appointmentForm.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message); // Use the message from the server response
                appointmentForm.reset();
                loadAppointments(); // Reload appointments after successful submission
            } else {
                alert('Error scheduling appointment: ' + data.message);
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    });

    // Handle the search form submission
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        const searchQuery = document.getElementById('searchQuery').value;

        fetch(searchForm.action + '?search_query=' + encodeURIComponent(searchQuery))
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            appointmentList.innerHTML = ''; // Clear the current appointment list
            if (data.appointments && data.appointments.length > 0) {
                data.appointments.forEach(appointment => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `
                        <strong>${appointment.name}</strong> with Dr. ${appointment.doctor_name}<br>
                        Date: ${appointment.appointment_time}<br>
                        Phone: ${appointment.mobile}
                    `;
                    appointmentList.appendChild(listItem);
                });
            } else {
                appointmentList.innerHTML = '<li>No appointments found.</li>';
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            appointmentList.innerHTML = '<li>Error searching for appointments. Please try again.</li>';
        });
    });

    // Function to load appointments
    function loadAppointments() {
        fetch('/appointments') // Adjust the URL as necessary
        .then(response => response.json())
        .then(data => {
            appointmentList.innerHTML = ''; // Clear the current appointment list
            if (data.appointments && data.appointments.length > 0) {
                data.appointments.forEach(appointment => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `
                        <strong>${appointment.name}</strong> with Dr. ${appointment.doctor_name}<br>
                        Date: ${appointment.appointment_time}<br>
                        Phone: ${appointment.mobile}
                    `;
                    appointmentList.appendChild(listItem);
                });
            } else {
                appointmentList.innerHTML = '<li>No appointments found.</li>';
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }

    // Load appointments when the page loads
    loadAppointments();
});
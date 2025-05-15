const addStaffForm = document.getElementById('add-staff-form');

addStaffForm.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent form submission
    const newStaff = {
        staffID: document.getElementById('staff-id').value,
        staffName: document.getElementById('staff-name').value,
        staff_role: document.getElementById('staff-role').value,
        userName: document.getElementById('username').value,
        password: document.getElementById('staff-password').value, // Normally, hash the password
        Contact: document.getElementById('contact-number').value,
        email: document.getElementById('email-id').value
    };

    console.log("Submitting new staff: ", newStaff); // Debugging information

    // Send the data to the server
    fetch('/hospital_staff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newStaff)
    })
    .then(data => {
        if (data.success) {
            console.log("Server response: ", data); // Debugging information
            // Show confirmation message
            alert('Staff member successfully added!');
            // Add the new staff member to the table
            addStaffToTable(newStaff);
            // Reset the form fields after success
            addStaffForm.reset();
        } else {
            console.error("Error from server: ", data.message); // Debugging information
            // Show error message from the server response
            alert('Error adding staff: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error adding new staff:', error); // Debugging information
        alert('There was an error while adding the staff. Please try again.');
    });
});

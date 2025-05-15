// staff_leave.js

// Function to validate the leave application form
function validateLeaveApplication() {
    const staffId = document.getElementById("staffId").value.trim();
    const staffName = document.getElementById("staffName").value.trim();
    const reason = document.getElementById("reason").value.trim();
    const timePeriod = document.getElementById("timePeriod").value.trim();

    // Check if all fields are filled
    if (!staffId || !staffName || !reason || !timePeriod) {
        alert("All fields are required!");
        return false;
    }

    // Validate the time period format (basic validation)
    const timePeriodRegex = /^\d{4}-\d{2}-\d{2} to \d{4}-\d{2}-\d{2}$/;
    if (!timePeriodRegex.test(timePeriod)) {
        alert("Please enter the time period in the format: YYYY-MM-DD to YYYY-MM-DD");
        return false;
    }

    return true; // All validations passed
}

// Function to handle form submission
function handleFormSubmission(event) {
    // Prevent the default form submission
    event.preventDefault();

    // Validate the form
    if (validateLeaveApplication()) {
        // If validation is successful, submit the form
        alert("Leave application submitted successfully!");
        document.querySelector("form").submit(); // Submit the form
    }
}

// Add event listener to the form
document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    form.addEventListener("submit", handleFormSubmission);
});
document.addEventListener('DOMContentLoaded', function() {
    // Function to toggle appointment details
    function toggleAppointmentDetails(event) {
        const appointmentItem = event.currentTarget;
        appointmentItem.classList.toggle('expanded');
    }

    // Add click event listeners to all appointment items
    const appointmentItems = document.querySelectorAll('.appointment-item');
    appointmentItems.forEach(item => {
        item.addEventListener('click', toggleAppointmentDetails);
    });

    // Function to filter appointments
    function filterAppointments() {
        const searchInput = document.getElementById('search-input');
        const filter = searchInput.value.toLowerCase();
        const appointmentItems = document.querySelectorAll('.appointment-item');

        appointmentItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(filter)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    // Add search input and button
    const container = document.querySelector('.container');
    const searchHTML = `
        <div class="search-container">
            <input type="text" id="search-input" placeholder="Search appointments...">
            <button id="search-button">Search</button>
        </div>
    `;
    container.insertAdjacentHTML('afterbegin', searchHTML);

    // Add event listener for search button
    const searchButton = document.getElementById('search-button');
    searchButton.addEventListener('click', filterAppointments);

    // Add event listener for search input (real-time filtering)
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', filterAppointments);

    searchButton.addEventListener('click', function() {
        const searchTerm = searchInput.value.toLowerCase();

        appointmentItems.forEach(item => {
            const patientName = item.querySelector('strong:nth-child(1)').nextSibling.textContent.toLowerCase();
            const doctorName = item.querySelector('strong:nth-child(3)').nextSibling.textContent.toLowerCase();

            if (patientName.includes(searchTerm) || doctorName.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });
});

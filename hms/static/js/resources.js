document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#dataForm');
    const editButtons = document.querySelectorAll('button[onclick^="editData"]');
    const addButtons = document.querySelectorAll('button[onclick^="addData"]');

    function createFields(fields) {
        // Clear existing input fields
        const existingFields = form.querySelectorAll('.dynamic-field');
        existingFields.forEach(field => field.remove());

        // Add new input fields based on the selected table
        fields.forEach(field => {
            const label = document.createElement('label');
            label.textContent = field.label;
            label.classList.add('dynamic-field');

            const input = document.createElement('input');
            input.type = field.type;
            input.name = field.name;
            input.classList.add('dynamic-field');

            form.appendChild(label);
            form.appendChild(input);
        });

        form.style.display = 'block'; // Show the form
    }

    function populateForm(row, fieldNames) {
        const cells = row.querySelectorAll('td');
        fieldNames.forEach((name, index) => {
            const input = form.querySelector(`input[name="${name}"]`);
            if (input) {
                input.value = cells[index].textContent.trim();
            }
        });
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);
        const action = form.getAttribute('data-action'); // Determine if it's 'add' or 'edit'
        const tableId = form.getAttribute('data-table-id');

        fetch(`/api/${action}_${tableId}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Operation successful!');
                location.reload(); // Reload the page to reflect changes
            } else {
                alert('Operation failed: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tableId = this.getAttribute('onclick').match(/'(.*?)'/)[1];
            form.setAttribute('data-action', 'edit');
            form.setAttribute('data-table-id', tableId);
            const row = document.querySelector(`#${tableId} tr.selected`);
            if (!row) {
                alert('Please select a row to edit.');
                return;
            }

            let fields = [];
            let fieldNames = [];
            switch (tableId) {
                case 'resourcesTable':
                    fields = [
                        { label: 'Resource ID', type: 'text', name: 'resource_id' },
                        { label: 'Type', type: 'text', name: 'resource_type' },
                        { label: 'Name', type: 'text', name: 'resource_name' },
                        { label: 'Status', type: 'text', name: 'status' },
                        { label: 'Quantity', type: 'number', name: 'quantity' }
                    ];
                    fieldNames = ['resource_id', 'resource_type', 'resource_name', 'status', 'quantity'];
                    break;
                case 'equipmentTable':
                    fields = [
                        { label: 'Equipment ID', type: 'text', name: 'equipment_id' },
                        { label: 'Name', type: 'text', name: 'equipment_name' },
                        { label: 'Purchase Date', type: 'date', name: 'purchase_date' },
                        { label: 'Warranty End Date', type: 'date', name: 'warranty_end_date' },
                        { label: 'Status', type: 'text', name: 'status' }
                    ];
                    fieldNames = ['equipment_id', 'equipment_name', 'purchase_date', 'warranty_end_date', 'status'];
                    break;
                case 'roomsTable':
                    fields = [
                        { label: 'Room ID', type: 'text', name: 'room_id' },
                        { label: 'Type', type: 'text', name: 'room_type' },
                        { label: 'Bed Count', type: 'number', name: 'bed_count' },
                        { label: 'Status', type: 'text', name: 'status' }
                    ];
                    fieldNames = ['room_id', 'room_type', 'bed_count', 'status'];
                    break;
                case 'suppliesTable':
                    fields = [
                        { label: 'Supply ID', type: 'text', name: 'supply_id' },
                        { label: 'Name', type: 'text', name: 'supply_name' },
                        { label: 'Quantity', type: 'number', name: 'quantity' },
                        { label: 'Unit', type: 'text', name: 'unit' },
                        { label: 'Last Restock Date', type: 'date', name: 'last_restock_date' }
                    ];
                    fieldNames = ['supply_id', 'supply_name', 'quantity', 'unit', 'last_restock_date'];
                    break;
            }

            createFields(fields);
            populateForm(row, fieldNames);
        });
    });

    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tableId = this.getAttribute('onclick').match(/'(.*?)'/)[1];
            form.setAttribute('data-action', 'add');
            form.setAttribute('data-table-id', tableId);

            let fields = [];
            switch (tableId) {
                case 'resourcesTable':
                    fields = [
                        { label: 'Resource ID', type: 'text', name: 'resource_id' },
                        { label: 'Type', type: 'text', name: 'resource_type' },
                        { label: 'Name', type: 'text', name: 'resource_name' },
                        { label: 'Status', type: 'text', name: 'status' },
                        { label: 'Quantity', type: 'number', name: 'quantity' }
                    ];
                    break;
                case 'equipmentTable':
                    fields = [
                        { label: 'Equipment ID', type: 'text', name: 'equipment_id' },
                        { label: 'Name', type: 'text', name: 'equipment_name' },
                        { label: 'Purchase Date', type: 'date', name: 'purchase_date' },
                        { label: 'Warranty End Date', type: 'date', name: 'warranty_end_date' },
                        { label: 'Status', type: 'text', name: 'status' }
                    ];
                    break;
                case 'roomsTable':
                    fields = [
                        { label: 'Room ID', type: 'text', name: 'room_id' },
                        { label: 'Type', type: 'text', name: 'room_type' },
                        { label: 'Bed Count', type: 'number', name: 'bed_count' },
                        { label: 'Status', type: 'text', name: 'status' }
                    ];
                    break;
                case 'suppliesTable':
                    fields = [
                        { label: 'Supply ID', type: 'text', name: 'supply_id' },
                        { label: 'Name', type: 'text', name: 'supply_name' },
                        { label: 'Quantity', type: 'number', name: 'quantity' },
                        { label: 'Unit', type: 'text', name: 'unit' },
                        { label: 'Last Restock Date', type: 'date', name: 'last_restock_date' }
                    ];
                    break;
            }

            createFields(fields);
        });
    });

    // Add event listeners to table rows for selection
    document.querySelectorAll('table tbody tr').forEach(row => {
        row.addEventListener('click', function() {
            document.querySelectorAll('table tbody tr').forEach(r => r.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
});
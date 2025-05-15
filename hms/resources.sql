CREATE TABLE Resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_type VARCHAR(50) NOT NULL,
    resource_name VARCHAR(100) NOT NULL,
    status ENUM('available', 'in use', 'under maintenance') DEFAULT 'available',
    quantity INT NOT NULL
);
INSERT INTO Resources (resource_type, resource_name, status, quantity)
VALUES ('equipment', 'MRI Machine', 'available', 1),
    ('room', 'ICU Room', 'in use', 10),
    ('supplies', 'Surgical Gloves', 'available', 200);
CREATE TABLE Equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    purchase_date DATE,
    warranty_end_date DATE,
    status ENUM('available', 'in use', 'under maintenance') DEFAULT 'available'
);
INSERT INTO Equipment (
        equipment_name,
        purchase_date,
        warranty_end_date,
        status
    )
VALUES (
        'Ventilator',
        '2020-05-10',
        '2025-05-10',
        'available'
    ),
    (
        'X-ray Machine',
        '2021-03-15',
        '2026-03-15',
        'under maintenance'
    );
CREATE TABLE Rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_type ENUM('ICU', 'General Ward', 'Private Room') NOT NULL,
    bed_count INT NOT NULL,
    status ENUM('occupied', 'available', 'under maintenance') DEFAULT 'available'
);
INSERT INTO Rooms (room_type, bed_count, status)
VALUES ('ICU', 5, 'available'),
    ('Private Room', 1, 'occupied'),
    ('General Ward', 20, 'available');
CREATE TABLE Supplies (
    supply_id INT AUTO_INCREMENT PRIMARY KEY,
    supply_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    last_restock_date DATE
);
INSERT INTO Supplies (supply_name, quantity, unit, last_restock_date)
VALUES ('Syringes', 500, 'box', '2024-10-01'),
    ('Face Masks', 1000, 'pack', '2024-09-20'),
    ('Surgical Gloves', 200, 'box', '2024-10-15');
CREATE TABLE Staff_Assignment (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    staffID INT NOT NULL,
    resource_id INT NOT NULL,
    assigned_on DATE NOT NULL,
    shift_start_time TIME,
    shift_end_time TIME,
    FOREIGN KEY (staffID) REFERENCES hospital_staff(staffID),
    -- Assuming Staff table exists
    FOREIGN KEY (resource_id) REFERENCES Resources(resource_id)
);
INSERT INTO Staff_Assignment (
        staffID,
        resource_id,
        assigned_on,
        shift_start_time,
        shift_end_time
    )
VALUES (1, 2, '2024-10-23', '08:00:00', '16:00:00'),
    -- Assign staff to ICU Room
    (2, 1, '2024-10-23', '16:00:00', '00:00:00');
-- Assign another staff to MRI Machine
CREATE TABLE Resource_Usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    used_by INT NOT NULL,
    -- Could be either patient or staff, depending on your design
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    status ENUM('completed', 'in use', 'pending') DEFAULT 'pending',
    FOREIGN KEY (resource_id) REFERENCES Resources(resource_id)
);
INSERT INTO Resource_Usage (
        resource_id,
        used_by,
        start_time,
        end_time,
        status
    )
VALUES (
        1,
        1001,
        '2024-10-23 08:00:00',
        '2024-10-23 10:00:00',
        'completed'
    ),
    -- MRI Machine used by Patient ID 1001
    (2, 1002, '2024-10-23 09:00:00', NULL, 'in use');
-- ICU Room used by Patient ID 1002
CREATE TABLE Resource_Maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    maintenance_type VARCHAR(100) NOT NULL,
    maintenance_date DATE NOT NULL,
    next_maintenance_due DATE,
    FOREIGN KEY (resource_id) REFERENCES Resources(resource_id)
);
INSERT INTO Resource_Maintenance (
        resource_id,
        maintenance_type,
        maintenance_date,
        next_maintenance_due
    )
VALUES (
        1,
        'Annual Servicing',
        '2024-10-15',
        '2025-10-15'
    ),
    -- MRI Machine maintenance
    (2, 'Repair', '2024-10-01', '2024-12-01');
-- ICU Room repair
CREATE TABLE Resource_Requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    requested_by INT NOT NULL,
    -- Assuming it's a staff member requesting the resource
    resource_id INT NOT NULL,
    request_date DATETIME NOT NULL,
    status ENUM('pending', 'approved', 'denied') DEFAULT 'pending',
    FOREIGN KEY (requested_by) REFERENCES hospital_staff(staffID),
    -- Assuming Staff table exists
    FOREIGN KEY (resource_id) REFERENCES Resources(resource_id)
);
INSERT INTO Resource_Requests (requested_by, resource_id, request_date, status)
VALUES (3, 1, '2024-10-23 07:45:00', 'approved'),
    -- Staff ID 3 requested MRI Machine
    (4, 2, '2024-10-23 09:00:00', 'pending');
-- Staff ID 4 requested ICU Room
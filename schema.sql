CREATE DATABASE IF NOT EXISTS blood_bank_db;
USE blood_bank_db;

CREATE TABLE IF NOT EXISTS donors (
    donor_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    age TINYINT UNSIGNED NOT NULL,
    gender ENUM('Female','Male','Other') NOT NULL,
    blood_group ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-') NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    city VARCHAR(80) NOT NULL,
    email VARCHAR(120),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_donor_age CHECK (age BETWEEN 18 AND 65)
);

CREATE TABLE IF NOT EXISTS blood_stock (
    blood_group ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-') PRIMARY KEY,
    units_available INT UNSIGNED NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS donations (
    donation_id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    donation_date DATE NOT NULL,
    units INT UNSIGNED NOT NULL DEFAULT 1,
    FOREIGN KEY (donor_id) REFERENCES donors(donor_id),
    CONSTRAINT chk_donation_units CHECK (units > 0)
);

CREATE TABLE IF NOT EXISTS blood_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    requester_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(15) NOT NULL,
    blood_group ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-') NOT NULL,
    units_needed INT UNSIGNED NOT NULL,
    hospital VARCHAR(120),
    notes VARCHAR(500),
    status ENUM('Pending','Approved','Fulfilled','Rejected') NOT NULL DEFAULT 'Pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_request_units CHECK (units_needed > 0)
);

INSERT IGNORE INTO blood_stock (blood_group, units_available) VALUES
('A+',0),('A-',0),('B+',0),('B-',0),('AB+',0),('AB-',0),('O+',0),('O-',0);

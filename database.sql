CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL
);

-- Example data:
INSERT INTO students (roll_no, name, course) VALUES
('12', 'Bhargav', 'Python'),
('13', 'Rahul', 'Java'),
('14', 'Priya', 'AIML'),
('15', 'Neha', 'Web Development');

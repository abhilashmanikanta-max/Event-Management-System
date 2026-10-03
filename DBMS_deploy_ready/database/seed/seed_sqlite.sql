-- ========================================================
-- EVENT MANAGEMENT SYSTEM
-- SQLite Seed Data
-- ========================================================

PRAGMA foreign_keys = ON;

-- Clear existing data if any (in reverse FK order)
DELETE FROM Payment;
DELETE FROM Registration;
DELETE FROM Event;
DELETE FROM Participant;
DELETE FROM Category;
DELETE FROM Venue;
DELETE FROM Organizer;

-- Reset Auto-Increment
DELETE FROM sqlite_sequence WHERE name IN ('Organizer', 'Venue', 'Category', 'Participant', 'Event', 'Registration', 'Payment');

-- 1. Insert Organizers
INSERT INTO Organizer (Organizer_ID, Name, Email, Phone) VALUES
(1, 'TechNova Innovations', 'contact@technova.org', '+1-555-0101'),
(2, 'Global Academic Summits', 'info@academicsummits.edu', '+1-555-0102'),
(3, 'Creative Pulse Media', 'hello@creativepulse.io', '+1-555-0103'),
(4, 'GreenEarth Environmental Forum', 'events@greenearth.org', '+1-555-0104'),
(5, 'Apex Esports & Gaming', 'tournaments@apexesports.com', '+1-555-0105');

-- 2. Insert Venues
INSERT INTO Venue (Venue_ID, Venue_Name, Location, Capacity) VALUES
(1, 'Grand Horizon Convention Center', 'Hall A, 100 Waterfront Blvd, Metropolis', 1200),
(2, 'Silicon Auditorium & Tech Park', 'Bldg 4, 450 Innovation Way, Tech Valley', 500),
(3, 'Emerald Botanical Gardens', 'Outdoor Pavilion, 22 Nature Park Rd', 350),
(4, 'Pinnacle Arena & Stadium', 'Gate 2, 77 Championship Ave, Sports City', 5000),
(5, 'University Central Lecture Hall', 'Campus Quadrangle, Block C, Room 101', 250);

-- 3. Insert Categories
INSERT INTO Category (Category_ID, Category_Name, Description) VALUES
(1, 'Technology & AI', 'Conferences, hackathons, and symposiums exploring cutting-edge computing, machine learning, and software engineering.'),
(2, 'Business & Leadership', 'Workshops, networking sessions, and executive panels focusing on startup growth, finance, and enterprise innovation.'),
(3, 'Arts & Culture', 'Exhibitions, music showcases, literary festivals, and visual creative arts.'),
(4, 'Environmental & Science', 'Conferences addressing sustainability, climate solutions, renewable energy, and biological sciences.'),
(5, 'Sports & Esports', 'Live tournaments, competitive gaming, athletic meets, and physical fitness challenges.');

-- 4. Insert Participants
INSERT INTO Participant (Participant_ID, Name, Email, Phone) VALUES
(1, 'Aarav Sharma', 'aarav.sharma@example.com', '+1-555-0201'),
(2, 'Elena Rostova', 'elena.rostova@example.com', '+1-555-0202'),
(3, 'Marcus Vance', 'marcus.vance@example.com', '+1-555-0203'),
(4, 'Priya Patel', 'priya.patel@example.com', '+1-555-0204'),
(5, 'David Kim', 'david.kim@example.com', '+1-555-0205'),
(6, 'Sophia Chen', 'sophia.chen@example.com', '+1-555-0206'),
(7, 'Liam O''Connor', 'liam.oconnor@example.com', '+1-555-0207'),
(8, 'Zara Al-Mansoor', 'zara.almansoor@example.com', '+1-555-0208');

-- 5. Insert Events
INSERT INTO Event (Event_ID, Event_Name, Date, Time, Organizer_ID, Venue_ID, Category_ID) VALUES
(1, 'AI & Cloud Summit 2026', '2026-11-15', '09:00 AM', 1, 2, 1),
(2, 'NextGen Web Architecture Hackathon', '2026-11-20', '10:00 AM', 1, 1, 1),
(3, 'Global Startup Founders Forum', '2026-12-05', '01:30 PM', 2, 1, 2),
(4, 'International Eco-Sustainability Expo', '2026-10-25', '09:30 AM', 4, 3, 4),
(5, 'National Indie Game Championship', '2026-12-12', '11:00 AM', 5, 4, 5),
(6, 'Modern Digital Media & Design Expo', '2026-11-28', '02:00 PM', 3, 5, 3),
(7, 'Clean Energy Future Symposium', '2026-12-18', '10:30 AM', 4, 2, 4),
(8, 'Leadership in Enterprise AI Seminar', '2026-11-08', '03:00 PM', 2, 5, 2);

-- 6. Insert Registrations
INSERT INTO Registration (Registration_ID, Participant_ID, Event_ID, Registration_Date, Status) VALUES
(1, 1, 1, '2026-10-01', 'Confirmed'),
(2, 2, 1, '2026-10-02', 'Confirmed'),
(3, 3, 2, '2026-10-03', 'Confirmed'),
(4, 4, 2, '2026-10-04', 'Confirmed'),
(5, 5, 3, '2026-10-05', 'Confirmed'),
(6, 6, 3, '2026-10-06', 'Pending'),
(7, 7, 4, '2026-10-07', 'Confirmed'),
(8, 8, 5, '2026-10-08', 'Confirmed'),
(9, 1, 5, '2026-10-09', 'Cancelled'),
(10, 2, 6, '2026-10-10', 'Confirmed'),
(11, 3, 7, '2026-10-11', 'Confirmed'),
(12, 4, 8, '2026-10-12', 'Confirmed');

-- 7. Insert Payments (1:1 with Registration)
INSERT INTO Payment (Payment_ID, Registration_ID, Amount, Payment_Date, Payment_Status) VALUES
(1, 1, 150.00, '2026-10-01', 'Completed'),
(2, 2, 150.00, '2026-10-02', 'Completed'),
(3, 3, 75.00, '2026-10-03', 'Completed'),
(4, 4, 75.00, '2026-10-04', 'Completed'),
(5, 5, 200.00, '2026-10-05', 'Completed'),
(6, 6, 200.00, '2026-10-06', 'Pending'),
(7, 7, 50.00, '2026-10-07', 'Completed'),
(8, 8, 120.00, '2026-10-08', 'Completed'),
(9, 9, 120.00, '2026-10-09', 'Failed'),
(10, 10, 85.00, '2026-10-10', 'Completed'),
(11, 11, 60.00, '2026-10-11', 'Completed'),
(12, 12, 110.00, '2026-10-12', 'Completed');

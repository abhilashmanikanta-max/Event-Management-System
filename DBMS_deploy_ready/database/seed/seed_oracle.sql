-- ========================================================
-- EVENT MANAGEMENT SYSTEM
-- Oracle SQL Seed Data
-- ========================================================

-- Clear existing data
DELETE FROM Payment;
DELETE FROM Registration;
DELETE FROM Event;
DELETE FROM Participant;
DELETE FROM Category;
DELETE FROM Venue;
DELETE FROM Organizer;
COMMIT;

-- 1. Insert Organizers
INSERT INTO Organizer (Name, Email, Phone) VALUES ('TechNova Innovations', 'contact@technova.org', '+1-555-0101');
INSERT INTO Organizer (Name, Email, Phone) VALUES ('Global Academic Summits', 'info@academicsummits.edu', '+1-555-0102');
INSERT INTO Organizer (Name, Email, Phone) VALUES ('Creative Pulse Media', 'hello@creativepulse.io', '+1-555-0103');
INSERT INTO Organizer (Name, Email, Phone) VALUES ('GreenEarth Environmental Forum', 'events@greenearth.org', '+1-555-0104');
INSERT INTO Organizer (Name, Email, Phone) VALUES ('Apex Esports & Gaming', 'tournaments@apexesports.com', '+1-555-0105');
COMMIT;

-- 2. Insert Venues
INSERT INTO Venue (Venue_Name, Location, Capacity) VALUES ('Grand Horizon Convention Center', 'Hall A, 100 Waterfront Blvd, Metropolis', 1200);
INSERT INTO Venue (Venue_Name, Location, Capacity) VALUES ('Silicon Auditorium & Tech Park', 'Bldg 4, 450 Innovation Way, Tech Valley', 500);
INSERT INTO Venue (Venue_Name, Location, Capacity) VALUES ('Emerald Botanical Gardens', 'Outdoor Pavilion, 22 Nature Park Rd', 350);
INSERT INTO Venue (Venue_Name, Location, Capacity) VALUES ('Pinnacle Arena & Stadium', 'Gate 2, 77 Championship Ave, Sports City', 5000);
INSERT INTO Venue (Venue_Name, Location, Capacity) VALUES ('University Central Lecture Hall', 'Campus Quadrangle, Block C, Room 101', 250);
COMMIT;

-- 3. Insert Categories
INSERT INTO Category (Category_Name, Description) VALUES ('Technology & AI', 'Conferences, hackathons, and symposiums exploring cutting-edge computing, machine learning, and software engineering.');
INSERT INTO Category (Category_Name, Description) VALUES ('Business & Leadership', 'Workshops, networking sessions, and executive panels focusing on startup growth, finance, and enterprise innovation.');
INSERT INTO Category (Category_Name, Description) VALUES ('Arts & Culture', 'Exhibitions, music showcases, literary festivals, and visual creative arts.');
INSERT INTO Category (Category_Name, Description) VALUES ('Environmental & Science', 'Conferences addressing sustainability, climate solutions, renewable energy, and biological sciences.');
INSERT INTO Category (Category_Name, Description) VALUES ('Sports & Esports', 'Live tournaments, competitive gaming, athletic meets, and physical fitness challenges.');
COMMIT;

-- 4. Insert Participants
INSERT INTO Participant (Name, Email, Phone) VALUES ('Aarav Sharma', 'aarav.sharma@example.com', '+1-555-0201');
INSERT INTO Participant (Name, Email, Phone) VALUES ('Elena Rostova', 'elena.rostova@example.com', '+1-555-0202');
INSERT INTO Participant (Name, Email, Phone) VALUES ('Marcus Vance', 'marcus.vance@example.com', '+1-555-0203');
INSERT INTO Participant (Name, Email, Phone) VALUES ('Priya Patel', 'priya.patel@example.com', '+1-555-0204');
INSERT INTO Participant (Name, Email, Phone) VALUES ('David Kim', 'david.kim@example.com', '+1-555-0205');
INSERT INTO Participant (Name, Email, Phone) VALUES ('Sophia Chen', 'sophia.chen@example.com', '+1-555-0206');
INSERT INTO Participant (Name, Email, Phone) VALUES ('Liam O''Connor', 'liam.oconnor@example.com', '+1-555-0207');
INSERT INTO Participant (Name, Email, Phone) VALUES ('Zara Al-Mansoor', 'zara.almansoor@example.com', '+1-555-0208');
COMMIT;

-- 5. Insert Events
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('AI & Cloud Summit 2026', DATE '2026-11-15', '09:00 AM', 1, 2, 1);
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('NextGen Web Architecture Hackathon', DATE '2026-11-20', '10:00 AM', 1, 1, 1);
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('Global Startup Founders Forum', DATE '2026-12-05', '01:30 PM', 2, 1, 2);
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('International Eco-Sustainability Expo', DATE '2026-10-25', '09:30 AM', 4, 3, 4);
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('National Indie Game Championship', DATE '2026-12-12', '11:00 AM', 5, 4, 5);
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('Modern Digital Media & Design Expo', DATE '2026-11-28', '02:00 PM', 3, 5, 3);
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('Clean Energy Future Symposium', DATE '2026-12-18', '10:30 AM', 4, 2, 4);
INSERT INTO Event (Event_Name, "Date", "Time", Organizer_ID, Venue_ID, Category_ID) VALUES ('Leadership in Enterprise AI Seminar', DATE '2026-11-08', '03:00 PM', 2, 5, 2);
COMMIT;

-- 6. Insert Registrations
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (1, 1, DATE '2026-10-01', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (2, 1, DATE '2026-10-02', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (3, 2, DATE '2026-10-03', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (4, 2, DATE '2026-10-04', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (5, 3, DATE '2026-10-05', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (6, 3, DATE '2026-10-06', 'Pending');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (7, 4, DATE '2026-10-07', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (8, 5, DATE '2026-10-08', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (1, 5, DATE '2026-10-09', 'Cancelled');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (2, 6, DATE '2026-10-10', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (3, 7, DATE '2026-10-11', 'Confirmed');
INSERT INTO Registration (Participant_ID, Event_ID, Registration_Date, Status) VALUES (4, 8, DATE '2026-10-12', 'Confirmed');
COMMIT;

-- 7. Insert Payments
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (1, 150.00, DATE '2026-10-01', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (2, 150.00, DATE '2026-10-02', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (3, 75.00, DATE '2026-10-03', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (4, 75.00, DATE '2026-10-04', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (5, 200.00, DATE '2026-10-05', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (6, 200.00, DATE '2026-10-06', 'Pending');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (7, 50.00, DATE '2026-10-07', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (8, 120.00, DATE '2026-10-08', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (9, 120.00, DATE '2026-10-09', 'Failed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (10, 85.00, DATE '2026-10-10', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (11, 60.00, DATE '2026-10-11', 'Completed');
INSERT INTO Payment (Registration_ID, Amount, Payment_Date, Payment_Status) VALUES (12, 110.00, DATE '2026-10-12', 'Completed');
COMMIT;

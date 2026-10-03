-- ========================================================
-- EVENT MANAGEMENT SYSTEM
-- SQLite Database Schema DDL
-- College DBMS Project
-- ========================================================

PRAGMA foreign_keys = ON;

-- 1. Organizer Table
CREATE TABLE IF NOT EXISTS Organizer (
    Organizer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20) NOT NULL
);

-- 2. Venue Table
CREATE TABLE IF NOT EXISTS Venue (
    Venue_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Venue_Name VARCHAR(100) NOT NULL,
    Location VARCHAR(200) NOT NULL,
    Capacity INTEGER NOT NULL CHECK (Capacity > 0)
);

-- 3. Category Table
CREATE TABLE IF NOT EXISTS Category (
    Category_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Category_Name VARCHAR(100) UNIQUE NOT NULL,
    Description TEXT
);

-- 4. Participant Table
CREATE TABLE IF NOT EXISTS Participant (
    Participant_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(20) NOT NULL
);

-- 5. Event Table
-- Foreign Keys: Organizer_ID -> Organizer, Venue_ID -> Venue, Category_ID -> Category
CREATE TABLE IF NOT EXISTS Event (
    Event_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Event_Name VARCHAR(150) NOT NULL,
    Date DATE NOT NULL,
    Time VARCHAR(10) NOT NULL,
    Organizer_ID INTEGER NOT NULL,
    Venue_ID INTEGER NOT NULL,
    Category_ID INTEGER NOT NULL,
    FOREIGN KEY (Organizer_ID) REFERENCES Organizer(Organizer_ID) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (Venue_ID) REFERENCES Venue(Venue_ID) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 6. Registration Table
-- Foreign Keys: Participant_ID -> Participant, Event_ID -> Event
CREATE TABLE IF NOT EXISTS Registration (
    Registration_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Participant_ID INTEGER NOT NULL,
    Event_ID INTEGER NOT NULL,
    Registration_Date DATE NOT NULL,
    Status VARCHAR(20) DEFAULT 'Confirmed' CHECK (Status IN ('Confirmed', 'Pending', 'Cancelled')),
    FOREIGN KEY (Participant_ID) REFERENCES Participant(Participant_ID) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (Event_ID) REFERENCES Event(Event_ID) ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE (Participant_ID, Event_ID)
);

-- 7. Payment Table
-- Foreign Key: Registration_ID -> Registration (1:1 Relationship via UNIQUE constraint)
CREATE TABLE IF NOT EXISTS Payment (
    Payment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Registration_ID INTEGER UNIQUE NOT NULL,
    Amount DECIMAL(10,2) NOT NULL CHECK (Amount >= 0),
    Payment_Date DATE NOT NULL,
    Payment_Status VARCHAR(20) DEFAULT 'Completed' CHECK (Payment_Status IN ('Completed', 'Pending', 'Failed', 'Refunded')),
    FOREIGN KEY (Registration_ID) REFERENCES Registration(Registration_ID) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Indexes for performance & foreign key lookups
CREATE INDEX IF NOT EXISTS idx_event_organizer ON Event(Organizer_ID);
CREATE INDEX IF NOT EXISTS idx_event_venue ON Event(Venue_ID);
CREATE INDEX IF NOT EXISTS idx_event_category ON Event(Category_ID);
CREATE INDEX IF NOT EXISTS idx_reg_participant ON Registration(Participant_ID);
CREATE INDEX IF NOT EXISTS idx_reg_event ON Registration(Event_ID);
CREATE INDEX IF NOT EXISTS idx_payment_reg ON Payment(Registration_ID);

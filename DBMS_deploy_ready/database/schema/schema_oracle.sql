-- ========================================================
-- EVENT MANAGEMENT SYSTEM
-- Oracle SQL Database Schema DDL
-- College DBMS Project
-- Compatible with Oracle 12c, 19c, 21c, 23ai
-- ========================================================

-- Drop tables in reverse dependency order if recreating
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Payment CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Registration CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Event CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Participant CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Category CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Venue CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Organizer CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

-- 1. Organizer Table
CREATE TABLE Organizer (
    Organizer_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
    Name VARCHAR2(100) NOT NULL,
    Email VARCHAR2(100) NOT NULL UNIQUE,
    Phone VARCHAR2(20) NOT NULL
);

-- 2. Venue Table
CREATE TABLE Venue (
    Venue_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
    Venue_Name VARCHAR2(100) NOT NULL,
    Location VARCHAR2(200) NOT NULL,
    Capacity NUMBER(8) NOT NULL CHECK (Capacity > 0)
);

-- 3. Category Table
CREATE TABLE Category (
    Category_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
    Category_Name VARCHAR2(100) NOT NULL UNIQUE,
    Description VARCHAR2(500)
);

-- 4. Participant Table
CREATE TABLE Participant (
    Participant_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
    Name VARCHAR2(100) NOT NULL,
    Email VARCHAR2(100) NOT NULL UNIQUE,
    Phone VARCHAR2(20) NOT NULL
);

-- 5. Event Table
CREATE TABLE Event (
    Event_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
    Event_Name VARCHAR2(150) NOT NULL,
    "Date" DATE NOT NULL,
    "Time" VARCHAR2(10) NOT NULL,
    Organizer_ID NUMBER NOT NULL,
    Venue_ID NUMBER NOT NULL,
    Category_ID NUMBER NOT NULL,
    CONSTRAINT fk_event_organizer FOREIGN KEY (Organizer_ID) REFERENCES Organizer(Organizer_ID),
    CONSTRAINT fk_event_venue FOREIGN KEY (Venue_ID) REFERENCES Venue(Venue_ID),
    CONSTRAINT fk_event_category FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
);

-- 6. Registration Table
CREATE TABLE Registration (
    Registration_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
    Participant_ID NUMBER NOT NULL,
    Event_ID NUMBER NOT NULL,
    Registration_Date DATE NOT NULL,
    Status VARCHAR2(20) DEFAULT 'Confirmed' NOT NULL CHECK (Status IN ('Confirmed', 'Pending', 'Cancelled')),
    CONSTRAINT fk_reg_participant FOREIGN KEY (Participant_ID) REFERENCES Participant(Participant_ID),
    CONSTRAINT fk_reg_event FOREIGN KEY (Event_ID) REFERENCES Event(Event_ID),
    CONSTRAINT uk_participant_event UNIQUE (Participant_ID, Event_ID)
);

-- 7. Payment Table (1:1 with Registration)
CREATE TABLE Payment (
    Payment_ID NUMBER GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1) PRIMARY KEY,
    Registration_ID NUMBER NOT NULL UNIQUE,
    Amount NUMBER(10,2) NOT NULL CHECK (Amount >= 0),
    Payment_Date DATE NOT NULL,
    Payment_Status VARCHAR2(20) DEFAULT 'Completed' NOT NULL CHECK (Payment_Status IN ('Completed', 'Pending', 'Failed', 'Refunded')),
    CONSTRAINT fk_payment_registration FOREIGN KEY (Registration_ID) REFERENCES Registration(Registration_ID)
);

-- Indexes for performance
CREATE INDEX idx_ora_event_org ON Event(Organizer_ID);
CREATE INDEX idx_ora_event_ven ON Event(Venue_ID);
CREATE INDEX idx_ora_event_cat ON Event(Category_ID);
CREATE INDEX idx_ora_reg_part ON Registration(Participant_ID);
CREATE INDEX idx_ora_reg_ev ON Registration(Event_ID);
CREATE INDEX idx_ora_pay_reg ON Payment(Registration_ID);

COMMIT;

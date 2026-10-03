-- ========================================================
-- EVENT MANAGEMENT SYSTEM
-- College DBMS Project - Core SQL Queries & Demonstrations
-- Demonstrates: Joins, Aggregations, Subqueries, Group By, Having
-- ========================================================

-- Query 1: Comprehensive Event Overview with 4-Table JOIN
SELECT 
    e.Event_ID,
    e.Event_Name,
    e.Date,
    e.Time,
    o.Name AS Organizer_Name,
    o.Email AS Organizer_Email,
    v.Venue_Name,
    v.Location AS Venue_Location,
    v.Capacity,
    c.Category_Name
FROM Event e
INNER JOIN Organizer o ON e.Organizer_ID = o.Organizer_ID
INNER JOIN Venue v ON e.Venue_ID = v.Venue_ID
INNER JOIN Category c ON e.Category_ID = c.Category_ID
ORDER BY e.Date ASC;

-- Query 2: Event Registration & Attendance Statistics (LEFT JOIN + Aggregation)
SELECT 
    e.Event_ID,
    e.Event_Name,
    v.Capacity,
    COUNT(r.Registration_ID) AS Total_Registered,
    ROUND((COUNT(r.Registration_ID) * 100.0 / v.Capacity), 2) AS Occupancy_Percentage,
    COALESCE(SUM(p.Amount), 0) AS Total_Revenue_Collected
FROM Event e
JOIN Venue v ON e.Venue_ID = v.Venue_ID
LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status != 'Cancelled'
LEFT JOIN Payment p ON r.Registration_ID = p.Registration_ID AND p.Payment_Status = 'Completed'
GROUP BY e.Event_ID, e.Event_Name, v.Capacity
ORDER BY Total_Registered DESC;

-- Query 3: Participant Detailed Registration & Payment History (5-Table JOIN)
SELECT 
    p.Participant_ID,
    p.Name AS Participant_Name,
    p.Email AS Participant_Email,
    e.Event_Name,
    e.Date AS Event_Date,
    r.Registration_Date,
    r.Status AS Registration_Status,
    COALESCE(pay.Amount, 0) AS Paid_Amount,
    COALESCE(pay.Payment_Status, 'Not Paid') AS Payment_Status
FROM Participant p
INNER JOIN Registration r ON p.Participant_ID = r.Participant_ID
INNER JOIN Event e ON r.Event_ID = e.Event_ID
LEFT JOIN Payment pay ON r.Registration_ID = pay.Registration_ID
ORDER BY r.Registration_Date DESC;

-- Query 4: Category Performance Report (GROUP BY + HAVING)
SELECT 
    c.Category_ID,
    c.Category_Name,
    COUNT(DISTINCT e.Event_ID) AS Event_Count,
    COUNT(r.Registration_ID) AS Total_Registrations,
    COALESCE(SUM(p.Amount), 0) AS Total_Revenue
FROM Category c
LEFT JOIN Event e ON c.Category_ID = e.Category_ID
LEFT JOIN Registration r ON e.Event_ID = r.Event_ID
LEFT JOIN Payment p ON r.Registration_ID = p.Registration_ID AND p.Payment_Status = 'Completed'
GROUP BY c.Category_ID, c.Category_Name
HAVING COUNT(DISTINCT e.Event_ID) > 0
ORDER BY Total_Revenue DESC;

-- Query 5: Subquery - Find Participants who have registered for high-capacity events (>400)
SELECT 
    Participant_ID, 
    Name, 
    Email 
FROM Participant
WHERE Participant_ID IN (
    SELECT DISTINCT r.Participant_ID
    FROM Registration r
    JOIN Event e ON r.Event_ID = e.Event_ID
    JOIN Venue v ON e.Venue_ID = v.Venue_ID
    WHERE v.Capacity > 400
);

-- Query 6: Correlated Subquery - Events with registration counts above average
SELECT 
    e1.Event_ID,
    e1.Event_Name,
    (SELECT COUNT(*) FROM Registration r WHERE r.Event_ID = e1.Event_ID) AS Reg_Count
FROM Event e1
WHERE (SELECT COUNT(*) FROM Registration r WHERE r.Event_ID = e1.Event_ID) >= (
    SELECT AVG(event_reg_count)
    FROM (
        SELECT COUNT(*) AS event_reg_count 
        FROM Registration 
        GROUP BY Event_ID
    )
);

-- Query 7: Venue Utilization Analysis
SELECT 
    v.Venue_ID,
    v.Venue_Name,
    v.Capacity,
    COUNT(DISTINCT e.Event_ID) AS Events_Hosted,
    COUNT(r.Registration_ID) AS Total_Attendees
FROM Venue v
LEFT JOIN Event e ON v.Venue_ID = e.Venue_ID
LEFT JOIN Registration r ON e.Event_ID = r.Event_ID AND r.Status = 'Confirmed'
GROUP BY v.Venue_ID, v.Venue_Name, v.Capacity
ORDER BY Events_Hosted DESC;

-- Query 8: Payment Reconciliation & Audit Log
SELECT 
    pay.Payment_ID,
    pay.Payment_Date,
    pay.Amount,
    pay.Payment_Status,
    r.Registration_ID,
    part.Name AS Participant_Name,
    e.Event_Name
FROM Payment pay
JOIN Registration r ON pay.Registration_ID = r.Registration_ID
JOIN Participant part ON r.Participant_ID = part.Participant_ID
JOIN Event e ON r.Event_ID = e.Event_ID
ORDER BY pay.Payment_Date DESC;

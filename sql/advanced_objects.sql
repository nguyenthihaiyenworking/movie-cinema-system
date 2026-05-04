-- Switch to your database
USE cinemadb;

-- 1. CLEANUP (Drop existing objects to avoid "Already Exists" errors)
DROP VIEW IF EXISTS AvailableSeats;
DROP FUNCTION IF EXISTS GetMovieRevenue;
DROP PROCEDURE IF EXISTS BookTicket;
DROP PROCEDURE IF EXISTS CancelTicket;
DROP PROCEDURE IF EXISTS AddScreeningWithCheck;
DROP TRIGGER IF EXISTS trg_ProtectActiveMovies;
DROP TRIGGER IF EXISTS trg_LogMovieChanges;
DROP TRIGGER IF EXISTS PreventOverbooking;
DROP TRIGGER IF EXISTS trg_LogTicketInsert;
DROP TRIGGER IF EXISTS trg_LogRoomUpdate;
DROP TRIGGER IF EXISTS trg_LogRoomDelete;
DROP TRIGGER IF EXISTS trg_LogSeatStatusChange;
DROP TRIGGER IF EXISTS trg_LogAccountSecurity;

-- 2. INDEXES (Boost query performance for the GUI)
CREATE INDEX idx_movie_title ON movies(MovieTitle);
CREATE INDEX idx_customer_phone ON customers(PhoneNumber);

-- 3. VIEWS (Abstraction layer for Streamlit display)
CREATE OR REPLACE VIEW AvailableSeats AS
SELECT 
    s.ScreeningID,
    m.MovieTitle,
    r.RoomName,
    s.ShowDate,
    r.Capacity - (SELECT COUNT(*) FROM tickets t WHERE t.ScreeningID = s.ScreeningID) AS RemainingSeats,
    ((SELECT COUNT(*) FROM tickets t WHERE t.ScreeningID = s.ScreeningID) / r.Capacity) * 100 AS OccupancyRate
FROM screenings s
JOIN movies m ON s.MovieID = m.MovieID
JOIN cinemarooms r ON s.RoomID = r.RoomID;

-- 4. USER DEFINED FUNCTIONS (For revenue reporting)
DELIMITER //
CREATE FUNCTION GetMovieRevenue(p_MovieID INT) 
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total_rev DECIMAL(10,2);
    SELECT SUM(t.TotalPrice) INTO total_rev
    FROM tickets t
    JOIN screenings s ON t.ScreeningID = s.ScreeningID
    WHERE s.MovieID = p_MovieID;
    RETURN IFNULL(total_rev, 0);
END //
DELIMITER ;

-- 5. STORED PROCEDURES (System Business Logic)
DELIMITER //

-- A. Add screening with schedule overlap check
CREATE PROCEDURE AddScreeningWithCheck(
    IN p_MovieID INT,
    IN p_RoomID INT,
    IN p_ShowDate DATETIME
)
BEGIN
    DECLARE v_Duration INT;
    DECLARE v_EndTime DATETIME;
    
    SELECT DurationMinutes INTO v_Duration FROM movies WHERE MovieID = p_MovieID;
    SET v_EndTime = DATE_ADD(p_ShowDate, INTERVAL v_Duration MINUTE);

    IF EXISTS (
        SELECT 1 FROM screenings s
        JOIN movies m ON s.MovieID = m.MovieID
        WHERE s.RoomID = p_RoomID 
        AND (
            (p_ShowDate BETWEEN s.ShowDate AND DATE_ADD(s.ShowDate, INTERVAL m.DurationMinutes MINUTE))
            OR (v_EndTime BETWEEN s.ShowDate AND DATE_ADD(s.ShowDate, INTERVAL m.DurationMinutes MINUTE))
        )
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Room is already occupied during this time.';
    ELSE
        INSERT INTO screenings (MovieID, RoomID, ShowDate) VALUES (p_MovieID, p_RoomID, p_ShowDate);
    END IF;
END //

-- B. Secure ticket booking (Using Transaction)
CREATE PROCEDURE BookTicket(
    IN p_CustomerID INT,
    IN p_ScreeningID INT,
    IN p_SeatID INT,
    IN p_Price DECIMAL(10,2),
    IN p_AccountID INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking failed: Transaction rolled back.';
    END;

    START TRANSACTION;
        IF EXISTS (SELECT 1 FROM tickets WHERE ScreeningID = p_ScreeningID AND SeatID = p_SeatID) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Seat already sold.';
        END IF;

        INSERT INTO tickets (ScreeningID, SeatID, CustomerID, TotalPrice, AccountID, BookingDate)
        VALUES (p_ScreeningID, p_SeatID, p_CustomerID, p_Price, p_AccountID, NOW());
        
        UPDATE seats SET Status = 'Booked' WHERE SeatID = p_SeatID;
    COMMIT;
END //

-- C. Cancel ticket and release seat
CREATE PROCEDURE CancelTicket(IN p_TicketID INT)
BEGIN
    DECLARE v_SeatID INT;
    SELECT SeatID INTO v_SeatID FROM tickets WHERE TicketID = p_TicketID;

    IF v_SeatID IS NOT NULL THEN
        DELETE FROM tickets WHERE TicketID = p_TicketID;
        UPDATE seats SET Status = 'Available', LockedUntil = NULL WHERE SeatID = v_SeatID;
        
        INSERT INTO logs (ActionType, TableName, LogDetails)
        VALUES ('DELETE', 'tickets', CONCAT('Cancelled Ticket ID: ', p_TicketID, ' and released Seat ID: ', v_SeatID));
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Ticket ID not found.';
    END IF;
END //

DELIMITER ;

-- 6. TRIGGERS (Data Protection & Automated Logging)
DELIMITER //

-- Prevent deleting a movie that has existing screenings
CREATE TRIGGER trg_ProtectActiveMovies
BEFORE DELETE ON movies
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM screenings WHERE MovieID = OLD.MovieID AND ShowDate >= NOW()) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Error: Cannot delete movie. It has active or future screenings.';
    END IF;
END //

-- Prevent booking beyond room capacity
CREATE TRIGGER PreventOverbooking
BEFORE INSERT ON tickets
FOR EACH ROW
BEGIN
    DECLARE v_current_booked INT;
    DECLARE v_max_capacity INT;

    SELECT COUNT(*) INTO v_current_booked FROM tickets WHERE ScreeningID = NEW.ScreeningID;
    SELECT r.Capacity INTO v_max_capacity 
    FROM screenings s 
    JOIN cinemarooms r ON s.RoomID = r.RoomID 
    WHERE s.ScreeningID = NEW.ScreeningID;

    IF v_current_booked >= v_max_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: Room capacity reached!';
    END IF;
END //

-- Log changes to movie information
CREATE TRIGGER trg_LogMovieChanges
AFTER UPDATE ON movies
FOR EACH ROW
BEGIN
    INSERT INTO logs (ActionType, TableName, LogDetails)
    VALUES ('UPDATE', 'movies', CONCAT('MovieID: ', OLD.MovieID, ' changed Title from "', OLD.MovieTitle, '" to "', NEW.MovieTitle, '"'));
END //

-- Log ticket sales
CREATE TRIGGER trg_LogTicketInsert
AFTER INSERT ON tickets
FOR EACH ROW
BEGIN
    INSERT INTO logs (AccountID, ActionType, TableName, LogDetails)
    VALUES (NEW.AccountID, 'INSERT', 'tickets', 
            CONCAT('New ticket issued: ID ', NEW.TicketID, ', Screening: ', NEW.ScreeningID, ', Price: $', NEW.TotalPrice));
END //

-- Log changes to cinema rooms
CREATE TRIGGER trg_LogRoomUpdate
AFTER UPDATE ON cinemarooms
FOR EACH ROW
BEGIN
    INSERT INTO logs (ActionType, TableName, LogDetails)
    VALUES ('UPDATE', 'cinemarooms', 
            CONCAT('Room ID ', OLD.RoomID, ' modified: ', OLD.RoomName, ' -> ', NEW.RoomName));
END //

CREATE TRIGGER trg_LogRoomDelete
AFTER DELETE ON cinemarooms
FOR EACH ROW
BEGIN
    INSERT INTO logs (ActionType, TableName, LogDetails)
    VALUES ('DELETE', 'cinemarooms', CONCAT('Deleted Room: ', OLD.RoomName));
END //

-- Log seat status changes
CREATE TRIGGER trg_LogSeatStatusChange
AFTER UPDATE ON seats
FOR EACH ROW
BEGIN
    IF OLD.Status <> NEW.Status THEN
        INSERT INTO logs (ActionType, TableName, LogDetails)
        VALUES ('UPDATE', 'seats', CONCAT('Seat ID ', OLD.SeatID, ' status changed: ', OLD.Status, ' -> ', NEW.Status));
    END IF;
END //

-- Log account security updates
CREATE TRIGGER trg_LogAccountSecurity
AFTER UPDATE ON accounts
FOR EACH ROW
BEGIN
    INSERT INTO logs (ActionType, TableName, LogDetails)
    VALUES ('UPDATE', 'accounts', CONCAT('Security update for user: ', OLD.Username, '. Role changed: ', OLD.Role, ' -> ', NEW.Role));
END //

DELIMITER ;

SELECT 
    st.TypeName AS Seat_Tier,
    COUNT(t.TicketID) AS Tickets_Sold,
    SUM(t.TotalPrice) AS Total_Revenue
FROM seat_types st
JOIN seats s ON st.TypeID = s.TypeID
JOIN tickets t ON s.SeatID = t.SeatID
GROUP BY st.TypeID
ORDER BY Total_Revenue DESC;

SELECT 
    -- This logic extracts "Standard Hall", "VIP Screen", etc. from your RoomName
    LEFT(r.RoomName, LOCATE(' ', r.RoomName, LOCATE(' ', r.RoomName) + 1) - 1) AS Room_Type,
    COUNT(t.TicketID) AS Tickets_Sold,
    SUM(t.TotalPrice) AS Total_Revenue
FROM cinemarooms r
JOIN screenings scr ON r.RoomID = scr.RoomID
JOIN tickets t ON scr.ScreeningID = t.ScreeningID
GROUP BY Room_Type
ORDER BY Total_Revenue DESC;

INSERT IGNORE INTO seat_types (TypeID, TypeName, BasePrice) VALUES 
(1, 'Standard', 75000),
(2, 'VIP', 110000),
(3, 'Sweetbox', 150000);
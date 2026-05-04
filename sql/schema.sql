-- 1. Drop existing tables and views (ordered to avoid Foreign Key constraints)
DROP VIEW IF EXISTS AvailableSeats;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS seats;
DROP TABLE IF EXISTS seat_types;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS cinemarooms;
DROP TABLE IF EXISTS movie_genres;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS accounts;

-- 2. Account Management & Permissions
CREATE TABLE accounts (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL, -- Should store hashes in production
    FullName VARCHAR(100),
    Role ENUM('Admin', 'Staff') DEFAULT 'Staff'
);
ALTER TABLE logs MODIFY COLUMN ActionType VARCHAR(50) NOT NULL;

-- 3. Log Management
CREATE TABLE logs (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    LogTimestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    AccountID INT,
    ActionType ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    TableName VARCHAR(50) NOT NULL,
    LogDetails TEXT, -- Stores change information (Old -> New)
    FOREIGN KEY (AccountID) REFERENCES accounts(AccountID) ON DELETE SET NULL
);

-- 4. Genres & Movies (M-N Relationship)
CREATE TABLE genres (
    GenreID INT AUTO_INCREMENT PRIMARY KEY,
    GenreName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE movies (
    MovieID INT AUTO_INCREMENT PRIMARY KEY,
    MovieTitle VARCHAR(255) NOT NULL,
    DurationMinutes INT NOT NULL CHECK (DurationMinutes > 0),
    ReleaseDate DATE NOT NULL,
    Rating VARCHAR(10) NOT NULL, -- e.g., G, PG, R, NC-17
    Description TEXT
);

-- Junction table for Movies & Genres
CREATE TABLE movie_genres (
    MovieID INT NOT NULL,
    GenreID INT NOT NULL,
    PRIMARY KEY (MovieID, GenreID),
    FOREIGN KEY (MovieID) REFERENCES movies(MovieID) ON DELETE CASCADE,
    FOREIGN KEY (GenreID) REFERENCES genres(GenreID) ON DELETE CASCADE
);

-- 5. Cinema Rooms & Seats (Pricing and Seat Types)
CREATE TABLE cinemarooms (
    RoomID INT AUTO_INCREMENT PRIMARY KEY,
    RoomName VARCHAR(100) NOT NULL,
    Capacity INT NOT NULL CHECK (Capacity > 0)
);

CREATE TABLE seat_types (
    TypeID INT AUTO_INCREMENT PRIMARY KEY,
    TypeName VARCHAR(50) NOT NULL, -- e.g., Standard, VIP, Sweetbox
    BasePrice DECIMAL(10, 2) NOT NULL CHECK (BasePrice >= 0)
);

CREATE TABLE seats (
    SeatID INT AUTO_INCREMENT PRIMARY KEY,
    RoomID INT NOT NULL,
    TypeID INT NOT NULL,
    RowChar CHAR(1) NOT NULL, -- Row (A, B, C...)
    SeatNumber INT NOT NULL, -- Seat Number (1, 2, 3...)
    Status ENUM('Available', 'Booked', 'Locked') DEFAULT 'Available',
    LockedUntil DATETIME NULL, -- 15-minute hold/lock
    FOREIGN KEY (RoomID) REFERENCES cinemarooms(RoomID) ON DELETE CASCADE,
    FOREIGN KEY (TypeID) REFERENCES seat_types(TypeID) ON DELETE CASCADE
);
ALTER TABLE seats MODIFY COLUMN SeatNumber VARCHAR(10);

-- 6. Screenings
CREATE TABLE screenings (
    ScreeningID INT AUTO_INCREMENT PRIMARY KEY,
    MovieID INT NOT NULL,
    RoomID INT NOT NULL,
    ShowDate DATETIME NOT NULL, -- Combined date and time for schedule management
    FOREIGN KEY (MovieID) REFERENCES movies(MovieID) ON DELETE CASCADE,
    FOREIGN KEY (RoomID) REFERENCES cinemarooms(RoomID) ON DELETE CASCADE
);

-- 7. Customers & Tickets
CREATE TABLE customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerName VARCHAR(255) NOT NULL,
    PhoneNumber VARCHAR(15) NOT NULL,
    Email VARCHAR(100)
);

CREATE TABLE tickets (
    TicketID INT AUTO_INCREMENT PRIMARY KEY,
    ScreeningID INT NOT NULL,
    SeatID INT NOT NULL,
    CustomerID INT NOT NULL,
    BookingDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    TotalPrice DECIMAL(10, 2) NOT NULL,
    AccountID INT, -- Staff member who processed the sale
    FOREIGN KEY (ScreeningID) REFERENCES screenings(ScreeningID) ON DELETE CASCADE,
    FOREIGN KEY (SeatID) REFERENCES seats(SeatID) ON DELETE CASCADE,
    FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (AccountID) REFERENCES accounts(AccountID) ON DELETE SET NULL,
    UNIQUE (ScreeningID, SeatID) -- Constraint: One seat per screening can only have one ticket
);

-- 8. Reports & Statistics Views
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

DELIMITER //

-- Admin account
INSERT INTO accounts (Username, Password, FullName, Role) 
VALUES ('admin', '123', 'Nguyen Thi Hai Yen', 'Admin');

-- Staff account
INSERT INTO accounts (Username, Password, FullName, Role) 
VALUES ('clerk01', '123', 'Nguyen Van A', 'Staff');


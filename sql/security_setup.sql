-- ======================================================
-- DATABASE SECURITY & ACCESS CONTROL
-- ======================================================

-- 1. Create a read-only user for the Reporting Team
CREATE USER 'reporter'@'localhost' IDENTIFIED BY '2026';
GRANT SELECT ON cinemadb.* TO 'reporter'@'localhost';

-- 2. Create a manager user for Movie/Screening updates
CREATE USER 'manager'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT, INSERT, UPDATE, DELETE ON cinemadb.movies TO 'manager'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON cinemadb.screenings TO 'manager'@'localhost';

-- 3. Apply changes
FLUSH PRIVILEGES;

-- ======================================================
-- BACKUP & RESTORE DOCUMENTATION
-- ======================================================
-- This file serves as a reference for the 2026 Backup Strategy.
-- Daily Full Backup Schedule: 02:00 AM
-- Storage: Local Server & Cloud Replication (GitHub/Drive)

-- =====================================================================
-- USER MANAGEMENT AND PRIVILEGES (SECURITY & RBAC)
-- =====================================================================

-- 1. Create New Users (if they do not already exist)
CREATE USER IF NOT EXISTS 'admin_user'@'localhost' IDENTIFIED BY 'admin';
CREATE USER IF NOT EXISTS 'clerk_user'@'localhost' IDENTIFIED BY 'clerk';

-- 2. Grant Privileges to Admin (Full system administration rights)
GRANT ALL PRIVILEGES ON cinemadb.* TO 'admin_user'@'localhost';

-- 3. Grant Privileges to Ticket Clerk (Restricted access for sales staff)
-- Basic read access for displaying data on the UI
GRANT SELECT ON cinemadb.Genres TO 'clerk_user'@'localhost'; 
GRANT SELECT ON cinemadb.movies TO 'clerk_user'@'localhost';
GRANT SELECT ON cinemadb.screenings TO 'clerk_user'@'localhost';
GRANT SELECT ON cinemadb.cinemarooms TO 'clerk_user'@'localhost';
GRANT SELECT ON cinemadb.seats TO 'clerk_user'@'localhost'; -- Required to check seat status
GRANT SELECT ON cinemadb.AvailableSeats TO 'clerk_user'@'localhost'; -- View for available seat counts

-- Data manipulation rights for customers and tickets
GRANT SELECT, INSERT, UPDATE ON cinemadb.customers TO 'clerk_user'@'localhost';
GRANT SELECT, INSERT ON cinemadb.tickets TO 'clerk_user'@'localhost';
GRANT UPDATE ON cinemadb.seats TO 'clerk_user'@'localhost'; -- Required to update Status/LockedUntil

-- Execution rights for encapsulated business logic (Procedures & Functions)
GRANT EXECUTE ON PROCEDURE cinemadb.BookTicket TO 'clerk_user'@'localhost';
GRANT EXECUTE ON PROCEDURE cinemadb.CancelTicket TO 'clerk_user'@'localhost';
GRANT EXECUTE ON FUNCTION cinemadb.GetMovieRevenue TO 'clerk_user'@'localhost';

-- Rights to write and view basic logs
GRANT SELECT, INSERT ON cinemadb.logs TO 'clerk_user'@'localhost';

-- 4. Apply privilege changes
FLUSH PRIVILEGES;
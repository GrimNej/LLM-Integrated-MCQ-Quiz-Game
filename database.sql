-- ============================================================================
-- database.sql
-- This file contains all SQL commands to set up the MCQ Quiz Game database
-- Run this file in phpMyAdmin or MySQL command line to create the database
-- ============================================================================

-- ============================================
-- STEP 1: Create the database
-- ============================================

-- Create a new database named 'mcq_game_db' if it doesn't already exist
CREATE DATABASE IF NOT EXISTS mcq_game_db;

-- Switch to use the newly created database for all following commands
USE mcq_game_db;

-- ============================================
-- STEP 2: Create the 'users' table
-- ============================================

-- This table stores all user account information
-- Each user has a unique ID, username, password, and game statistics
CREATE TABLE IF NOT EXISTS users (
    
    -- user_id: Unique identifier for each user
    -- INT: Stores whole numbers
    -- PRIMARY KEY: Makes this the main identifier for each row
    -- AUTO_INCREMENT: Automatically assigns the next number for new users
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- username: The display name for the user
    -- VARCHAR(50): Can store up to 50 characters
    -- UNIQUE: No two users can have the same username
    -- NOT NULL: This field cannot be left empty
    username VARCHAR(50) UNIQUE NOT NULL,
    
    -- password: The user's password stored as plain text
    -- VARCHAR(50): Can store up to 50 characters
    -- NOT NULL: This field cannot be left empty
    -- Note: Plain text storage is only for this school project, not for production
    password VARCHAR(50) NOT NULL,
    
    -- games_played: Counter for total number of games the user has played
    -- INT: Stores whole numbers
    -- DEFAULT 0: New users start with 0 games played
    games_played INT DEFAULT 0,
    
    -- games_won: Counter for games where user scored 7 or more out of 10
    -- INT: Stores whole numbers
    -- DEFAULT 0: New users start with 0 wins
    games_won INT DEFAULT 0,
    
    -- created_at: Timestamp of when the account was created
    -- DATETIME: Stores both date and time
    -- DEFAULT CURRENT_TIMESTAMP: Automatically records the current date and time
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STEP 3: Create the 'game_history' table
-- ============================================

-- This table stores the history of all games played by all users
-- Each entry is linked to a user via foreign key and contains game details
CREATE TABLE IF NOT EXISTS game_history (
    
    -- history_id: Unique identifier for each game history entry
    -- INT: Stores whole numbers
    -- PRIMARY KEY: Makes this the main identifier for each row
    -- AUTO_INCREMENT: Automatically assigns the next number for new entries
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- user_id: Links this game entry to a specific user in the users table
    -- INT: Stores whole numbers (must match a user_id in users table)
    -- NOT NULL: Every game must belong to a user
    user_id INT NOT NULL,
    
    -- topic: The subject/topic that the user chose for this quiz game
    -- VARCHAR(100): Can store up to 100 characters for the topic name
    -- NOT NULL: Every game must have a topic
    topic VARCHAR(100) NOT NULL,
    
    -- score: The number of correct answers the user got (out of 10)
    -- INT: Stores whole numbers from 0 to 10
    -- NOT NULL: Every game must have a score recorded
    score INT NOT NULL,
    
    -- result: Text indicating whether the user won or lost
    -- VARCHAR(10): Stores either 'WON' or 'LOST'
    -- NOT NULL: Every game must have a result
    result VARCHAR(10) NOT NULL,
    
    -- played_at: Timestamp of when this game was played
    -- DATETIME: Stores both date and time
    -- DEFAULT CURRENT_TIMESTAMP: Automatically records when the game was saved
    played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- FOREIGN KEY constraint: Ensures data integrity between tables
    -- user_id must reference an existing user_id in the users table
    -- ON DELETE CASCADE: When a user is deleted, all their game history is also deleted
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- STEP 4: Create indexes for better query performance
-- ============================================

-- Index on user_id in game_history table
-- This speeds up queries that fetch all games for a specific user
CREATE INDEX idx_game_history_user_id ON game_history(user_id);

-- Index on played_at in game_history table
-- This speeds up queries that sort games by date (most recent first)
CREATE INDEX idx_game_history_played_at ON game_history(played_at);

-- ============================================
-- STEP 5: Verification queries (optional)
-- ============================================

-- Display all tables in the database to confirm they were created
SHOW TABLES;

-- Display the structure of the users table to verify columns
DESCRIBE users;

-- Display the structure of the game_history table to verify columns
DESCRIBE game_history;
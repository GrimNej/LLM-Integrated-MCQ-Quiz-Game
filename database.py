# ============================================================================
# database.py
# This file handles all database connections and SQL queries for the MCQ Quiz Game
# It contains functions for all CRUD (Create, Read, Update, Delete) operations
# ============================================================================

# Import the MySQL connector library to communicate with MySQL database
import mysql.connector

# Import mysql.connector.Error to handle database-specific errors
from mysql.connector import Error

# ============================================================================
# DATABASE CONNECTION FUNCTION
# ============================================================================

def get_db_connection():
    """
    Creates and returns a connection to the MySQL database.
    This function is called every time we need to interact with the database.
    
    Returns:
        connection: A MySQL database connection object if successful
        None: If the connection fails
    """
    
    try:
        # Create a connection to the MySQL database using the connector
        # host: The server where MySQL is running (localhost means this computer)
        # user: The MySQL username (root is the default XAMPP user)
        # password: The MySQL password (empty string is default for XAMPP)
        # database: The name of our database we created in database.sql
        connection = mysql.connector.connect(
            host="localhost",        # MySQL server location
            user="root",             # Default XAMPP MySQL username
            password="",             # Default XAMPP MySQL password (empty)
            database="mcq_game_db"   # Our database name
        )
        
        # Check if the connection was successful
        if connection.is_connected():
            # Return the connection object so other functions can use it
            return connection
            
    except Error as e:
        # If connection fails, print the error message for debugging
        print(f"Error connecting to MySQL database: {e}")
        # Return None to indicate the connection failed
        return None

# ============================================================================
# CREATE OPERATIONS
# ============================================================================

def create_user(username, password):
    """
    Creates a new user account in the database.
    This is called when a new user signs up.
    
    Args:
        username: The desired username for the new account
        password: The password for the new account (stored as plain text)
    
    Returns:
        dict: Contains 'success' (bool) and 'message' (str) keys
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor object to execute SQL queries
        # A cursor is like a pointer that helps us run commands and fetch results
        cursor = connection.cursor()
        
        # First, check if the username already exists in the database
        # We use %s as a placeholder to prevent SQL injection attacks
        check_query = "SELECT user_id FROM users WHERE username = %s"
        
        # Execute the query with the username as a parameter
        # The second argument must be a tuple, hence the comma after username
        cursor.execute(check_query, (username,))
        
        # Fetch one result from the query
        existing_user = cursor.fetchone()
        
        # If a user with this username already exists
        if existing_user is not None:
            # Close the cursor and connection to free up resources
            cursor.close()
            connection.close()
            # Return error message indicating username is taken
            return {"success": False, "message": "Username already exists"}
        
        # If username is available, insert the new user into the database
        # games_played and games_won will default to 0 as defined in the table
        # created_at will automatically be set to the current timestamp
        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        
        # Execute the insert query with username and password as parameters
        cursor.execute(insert_query, (username, password))
        
        # Commit the transaction to save the changes to the database
        # Without commit, the changes would not be permanently saved
        connection.commit()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Return success message
        return {"success": True, "message": "Account created successfully"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error creating user: {e}")
        # Return error message
        return {"success": False, "message": "Failed to create account"}

def create_game_history(user_id, topic, score, result):
    """
    Creates a new game history entry after a user finishes a game.
    Also updates the user's games_played and games_won statistics.
    
    Args:
        user_id: The ID of the user who played the game
        topic: The topic/subject of the quiz
        score: The number of correct answers (out of 10)
        result: Either 'WON' or 'LOST'
    
    Returns:
        dict: Contains 'success' (bool) and 'message' (str) keys
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()
        
        # Insert the game history entry into the game_history table
        # played_at will automatically be set to the current timestamp
        insert_query = """
            INSERT INTO game_history (user_id, topic, score, result) 
            VALUES (%s, %s, %s, %s)
        """
        
        # Execute the insert query with all the game details
        cursor.execute(insert_query, (user_id, topic, score, result))
        
        # Update the user's games_played counter by adding 1
        update_games_played_query = """
            UPDATE users 
            SET games_played = games_played + 1 
            WHERE user_id = %s
        """
        
        # Execute the update query for games_played
        cursor.execute(update_games_played_query, (user_id,))
        
        # If the user won the game (score >= 7), also update games_won
        if result == "WON":
            # Update the user's games_won counter by adding 1
            update_games_won_query = """
                UPDATE users 
                SET games_won = games_won + 1 
                WHERE user_id = %s
            """
            
            # Execute the update query for games_won
            cursor.execute(update_games_won_query, (user_id,))
        
        # Commit all the transactions to save changes to the database
        connection.commit()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Return success message
        return {"success": True, "message": "Game history saved successfully"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error creating game history: {e}")
        # Return error message
        return {"success": False, "message": "Failed to save game history"}

# ============================================================================
# READ OPERATIONS
# ============================================================================

def verify_user_login(username, password):
    """
    Verifies user credentials for login.
    Checks if the username exists and if the password matches.
    
    Args:
        username: The username entered by the user
        password: The password entered by the user
    
    Returns:
        dict: Contains 'success' (bool), 'message' (str), and 'user_id' (int) if successful
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed", "user_id": None}
    
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()
        
        # Query to find a user with the given username and password
        # If both match, the user's credentials are correct
        login_query = "SELECT user_id FROM users WHERE username = %s AND password = %s"
        
        # Execute the query with username and password as parameters
        cursor.execute(login_query, (username, password))
        
        # Fetch one result from the query
        user = cursor.fetchone()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # If a matching user was found
        if user is not None:
            # Return success with the user's ID
            # user[0] contains the user_id from the query result
            return {"success": True, "message": "Login successful", "user_id": user[0]}
        else:
            # No matching user found - either username or password is wrong
            return {"success": False, "message": "Invalid username or password", "user_id": None}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error verifying login: {e}")
        # Return error message
        return {"success": False, "message": "Login failed", "user_id": None}

def get_user_stats(user_id):
    """
    Retrieves the statistics for a specific user.
    Used to display on the home page.
    
    Args:
        user_id: The ID of the user whose stats we want to retrieve
    
    Returns:
        dict: Contains user statistics or error information
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor with dictionary=True to get results as dictionaries
        # This makes it easier to access columns by name instead of index
        cursor = connection.cursor(dictionary=True)
        
        # Query to get user's username, games_played, and games_won
        stats_query = """
            SELECT username, games_played, games_won 
            FROM users 
            WHERE user_id = %s
        """
        
        # Execute the query with user_id as parameter
        cursor.execute(stats_query, (user_id,))
        
        # Fetch the result
        user_stats = cursor.fetchone()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # If user was found
        if user_stats is not None:
            # Calculate win rate percentage
            # Avoid division by zero if no games have been played
            if user_stats["games_played"] > 0:
                # Calculate percentage: (wins / total) * 100, rounded to 1 decimal
                win_rate = round((user_stats["games_won"] / user_stats["games_played"]) * 100, 1)
            else:
                # If no games played, win rate is 0
                win_rate = 0
            
            # Return the stats with calculated win rate
            return {
                "success": True,
                "username": user_stats["username"],
                "games_played": user_stats["games_played"],
                "games_won": user_stats["games_won"],
                "win_rate": win_rate
            }
        else:
            # User not found in database
            return {"success": False, "message": "User not found"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error getting user stats: {e}")
        # Return error message
        return {"success": False, "message": "Failed to retrieve stats"}

def get_game_history(user_id):
    """
    Retrieves all game history entries for a specific user.
    Results are ordered by most recent game first.
    
    Args:
        user_id: The ID of the user whose history we want to retrieve
    
    Returns:
        dict: Contains list of game history entries or error information
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed", "history": []}
    
    try:
        # Create a cursor with dictionary=True to get results as dictionaries
        cursor = connection.cursor(dictionary=True)
        
        # Query to get all game history for this user
        # ORDER BY played_at DESC means most recent games appear first
        history_query = """
            SELECT history_id, topic, score, result, played_at 
            FROM game_history 
            WHERE user_id = %s 
            ORDER BY played_at DESC
        """
        
        # Execute the query with user_id as parameter
        cursor.execute(history_query, (user_id,))
        
        # Fetch all results (not just one)
        history_list = cursor.fetchall()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Convert datetime objects to strings for JSON serialization
        # JSON cannot directly serialize Python datetime objects
        for entry in history_list:
            # Convert the played_at datetime to a formatted string
            entry["played_at"] = entry["played_at"].strftime("%Y-%m-%d %H:%M")
        
        # Return the history list
        return {"success": True, "history": history_list}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error getting game history: {e}")
        # Return error message with empty history list
        return {"success": False, "message": "Failed to retrieve history", "history": []}

def get_leaderboard():
    """
    Retrieves all users ranked by their win rate.
    Used to display the leaderboard page.
    
    Returns:
        dict: Contains list of users with their rankings or error information
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed", "leaderboard": []}
    
    try:
        # Create a cursor with dictionary=True to get results as dictionaries
        cursor = connection.cursor(dictionary=True)
        
        # Query to get all users with their stats
        # We calculate win_rate in the query itself
        # CASE WHEN prevents division by zero when games_played is 0
        # ORDER BY win_rate DESC puts highest win rates first
        # If win rates are equal, sort by games_played DESC (more games = higher rank)
        leaderboard_query = """
            SELECT 
                user_id,
                username, 
                games_played, 
                games_won,
                CASE 
                    WHEN games_played > 0 
                    THEN ROUND((games_won / games_played) * 100, 1) 
                    ELSE 0 
                END as win_rate
            FROM users 
            ORDER BY win_rate DESC, games_played DESC
        """
        
        # Execute the query
        cursor.execute(leaderboard_query)
        
        # Fetch all results
        leaderboard_list = cursor.fetchall()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Add rank numbers to each entry
        # Enumerate starts at 1 for proper ranking (1st, 2nd, 3rd, etc.)
        for index, entry in enumerate(leaderboard_list, start=1):
            # Add a 'rank' key to each entry
            entry["rank"] = index
        
        # Return the leaderboard list
        return {"success": True, "leaderboard": leaderboard_list}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error getting leaderboard: {e}")
        # Return error message with empty leaderboard list
        return {"success": False, "message": "Failed to retrieve leaderboard", "leaderboard": []}

def get_user_info(user_id):
    """
    Retrieves basic information for a specific user.
    Used for the account page display.
    
    Args:
        user_id: The ID of the user whose info we want to retrieve
    
    Returns:
        dict: Contains user info or error information
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor with dictionary=True to get results as dictionaries
        cursor = connection.cursor(dictionary=True)
        
        # Query to get user's basic information
        info_query = """
            SELECT username, created_at 
            FROM users 
            WHERE user_id = %s
        """
        
        # Execute the query with user_id as parameter
        cursor.execute(info_query, (user_id,))
        
        # Fetch the result
        user_info = cursor.fetchone()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # If user was found
        if user_info is not None:
            # Convert created_at datetime to string for JSON serialization
            user_info["created_at"] = user_info["created_at"].strftime("%Y-%m-%d %H:%M")
            
            # Return the user info
            return {"success": True, "user": user_info}
        else:
            # User not found in database
            return {"success": False, "message": "User not found"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error getting user info: {e}")
        # Return error message
        return {"success": False, "message": "Failed to retrieve user info"}

# ============================================================================
# UPDATE OPERATIONS
# ============================================================================

def update_username(user_id, new_username):
    """
    Updates the username for a specific user.
    Checks if the new username is already taken before updating.
    
    Args:
        user_id: The ID of the user who wants to change their username
        new_username: The new desired username
    
    Returns:
        dict: Contains 'success' (bool) and 'message' (str) keys
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()
        
        # First, check if the new username already exists (but not for this user)
        check_query = "SELECT user_id FROM users WHERE username = %s AND user_id != %s"
        
        # Execute the query with new_username and user_id as parameters
        cursor.execute(check_query, (new_username, user_id))
        
        # Fetch one result from the query
        existing_user = cursor.fetchone()
        
        # If someone else already has this username
        if existing_user is not None:
            # Close the cursor and connection to free up resources
            cursor.close()
            connection.close()
            # Return error message indicating username is taken
            return {"success": False, "message": "Username already taken"}
        
        # If username is available, update the user's username
        update_query = "UPDATE users SET username = %s WHERE user_id = %s"
        
        # Execute the update query
        cursor.execute(update_query, (new_username, user_id))
        
        # Commit the transaction to save the changes
        connection.commit()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Return success message
        return {"success": True, "message": "Username updated successfully"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error updating username: {e}")
        # Return error message
        return {"success": False, "message": "Failed to update username"}

def update_password(user_id, current_password, new_password):
    """
    Updates the password for a specific user.
    Verifies the current password before allowing the change.
    
    Args:
        user_id: The ID of the user who wants to change their password
        current_password: The user's current password for verification
        new_password: The new desired password
    
    Returns:
        dict: Contains 'success' (bool) and 'message' (str) keys
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()
        
        # First, verify that the current password is correct
        verify_query = "SELECT user_id FROM users WHERE user_id = %s AND password = %s"
        
        # Execute the query with user_id and current_password as parameters
        cursor.execute(verify_query, (user_id, current_password))
        
        # Fetch one result from the query
        verified_user = cursor.fetchone()
        
        # If current password does not match
        if verified_user is None:
            # Close the cursor and connection to free up resources
            cursor.close()
            connection.close()
            # Return error message
            return {"success": False, "message": "Current password is incorrect"}
        
        # If current password is correct, update to the new password
        update_query = "UPDATE users SET password = %s WHERE user_id = %s"
        
        # Execute the update query
        cursor.execute(update_query, (new_password, user_id))
        
        # Commit the transaction to save the changes
        connection.commit()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Return success message
        return {"success": True, "message": "Password updated successfully"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error updating password: {e}")
        # Return error message
        return {"success": False, "message": "Failed to update password"}

# ============================================================================
# DELETE OPERATIONS
# ============================================================================

def delete_game_history_entry(history_id, user_id):
    """
    Deletes a specific game history entry.
    Only allows deletion if the entry belongs to the specified user.
    Note: This does NOT change the user's stats (games_played, games_won).
    
    Args:
        history_id: The ID of the history entry to delete
        user_id: The ID of the user requesting the deletion (for security)
    
    Returns:
        dict: Contains 'success' (bool) and 'message' (str) keys
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()
        
        # Delete the history entry only if it belongs to this user
        # This prevents users from deleting other users' history
        delete_query = "DELETE FROM game_history WHERE history_id = %s AND user_id = %s"
        
        # Execute the delete query
        cursor.execute(delete_query, (history_id, user_id))
        
        # Check how many rows were affected
        # If 0 rows affected, either the entry doesn't exist or doesn't belong to this user
        rows_affected = cursor.rowcount
        
        # Commit the transaction to save the changes
        connection.commit()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Check if a row was actually deleted
        if rows_affected > 0:
            # Return success message
            return {"success": True, "message": "History entry deleted successfully"}
        else:
            # No rows were deleted
            return {"success": False, "message": "History entry not found"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error deleting history entry: {e}")
        # Return error message
        return {"success": False, "message": "Failed to delete history entry"}

def delete_user_account(user_id):
    """
    Deletes a user account and all associated data.
    The game_history entries are automatically deleted due to CASCADE.
    
    Args:
        user_id: The ID of the user account to delete
    
    Returns:
        dict: Contains 'success' (bool) and 'message' (str) keys
    """
    
    # Get a connection to the database
    connection = get_db_connection()
    
    # Check if the connection was successful
    if connection is None:
        # Return error if we cannot connect to the database
        return {"success": False, "message": "Database connection failed"}
    
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()
        
        # Delete the user from the users table
        # Due to ON DELETE CASCADE in the foreign key, all game_history entries
        # for this user will also be automatically deleted
        delete_query = "DELETE FROM users WHERE user_id = %s"
        
        # Execute the delete query
        cursor.execute(delete_query, (user_id,))
        
        # Check how many rows were affected
        rows_affected = cursor.rowcount
        
        # Commit the transaction to save the changes
        connection.commit()
        
        # Close the cursor and connection to free up resources
        cursor.close()
        connection.close()
        
        # Check if the user was actually deleted
        if rows_affected > 0:
            # Return success message
            return {"success": True, "message": "Account deleted successfully"}
        else:
            # No user was deleted (user might not exist)
            return {"success": False, "message": "Account not found"}
        
    except Error as e:
        # If any database error occurs, print it for debugging
        print(f"Error deleting user account: {e}")
        # Return error message
        return {"success": False, "message": "Failed to delete account"}
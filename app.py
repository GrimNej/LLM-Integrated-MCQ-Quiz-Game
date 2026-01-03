# ============================================================================
# app.py
# This is the main Flask application file for the MCQ Quiz Game
# It handles all routes, session management, and connects frontend with backend
# ============================================================================

# Import the Flask class to create our web application
from flask import Flask

# Import render_template to serve HTML pages
from flask import render_template

# Import request to access data sent from the frontend (forms, JSON, etc.)
from flask import request

# Import jsonify to convert Python dictionaries to JSON responses
from flask import jsonify

# Import session to store user data between requests (like login status)
from flask import session

# Import redirect to send users to different pages
from flask import redirect

# Import url_for to generate URLs for routes
from flask import url_for

# Import our database functions from database.py
import database

# Import our MCQ generator function from mcq_generator.py
from mcq_generator import generate_quiz

# ============================================================================
# FLASK APP CONFIGURATION
# ============================================================================

# Create a Flask application instance
# __name__ tells Flask where to look for templates and static files
app = Flask(__name__)

# Set a secret key for session management
# This key is used to encrypt session data stored in cookies
# In production, this should be a long random string kept secret
app.secret_key = "mcq_quiz_game_secret_key_2024"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_logged_in():
    """
    Checks if a user is currently logged in.
    A user is logged in if their user_id is stored in the session.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    
    # Check if 'user_id' key exists in the session
    # If it exists and has a value, the user is logged in
    return "user_id" in session and session["user_id"] is not None

def get_current_user_id():
    """
    Gets the user_id of the currently logged in user.
    
    Returns:
        int: The user_id if logged in, None otherwise
    """
    
    # Return the user_id from session, or None if not logged in
    return session.get("user_id", None)

# ============================================================================
# PAGE ROUTES (Serve HTML Templates)
# ============================================================================

@app.route("/")
def index():
    """
    Root route - redirects to appropriate page based on login status.
    If logged in, go to home page. If not, go to login page.
    """
    
    # Check if user is logged in
    if is_logged_in():
        # Redirect to home page if logged in
        return redirect(url_for("home_page"))
    else:
        # Redirect to login page if not logged in
        return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    """
    Serves the login/signup page.
    If user is already logged in, redirect to home page.
    """
    
    # Check if user is already logged in
    if is_logged_in():
        # Redirect to home page since they're already logged in
        return redirect(url_for("home_page"))
    
    # Serve the login.html template
    return render_template("login.html")

@app.route("/home")
def home_page():
    """
    Serves the home page with user stats and game history.
    Requires user to be logged in.
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Redirect to login page if not logged in
        return redirect(url_for("login_page"))
    
    # Serve the home.html template
    return render_template("home.html")

@app.route("/play")
def play_page():
    """
    Serves the game setup page where user enters a topic.
    Requires user to be logged in.
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Redirect to login page if not logged in
        return redirect(url_for("login_page"))
    
    # Serve the play.html template
    return render_template("play.html")

@app.route("/quiz")
def quiz_page():
    """
    Serves the quiz page where user answers questions.
    Requires user to be logged in.
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Redirect to login page if not logged in
        return redirect(url_for("login_page"))
    
    # Serve the quiz.html template
    return render_template("quiz.html")

@app.route("/results")
def results_page():
    """
    Serves the results page showing the user's score.
    Requires user to be logged in.
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Redirect to login page if not logged in
        return redirect(url_for("login_page"))
    
    # Serve the results.html template
    return render_template("results.html")

@app.route("/leaderboard")
def leaderboard_page():
    """
    Serves the leaderboard page showing all players ranked.
    Requires user to be logged in.
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Redirect to login page if not logged in
        return redirect(url_for("login_page"))
    
    # Serve the leaderboard.html template
    return render_template("leaderboard.html")

@app.route("/account")
def account_page():
    """
    Serves the account settings page.
    Requires user to be logged in.
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Redirect to login page if not logged in
        return redirect(url_for("login_page"))
    
    # Serve the account.html template
    return render_template("account.html")

# ============================================================================
# AUTHENTICATION API ROUTES
# ============================================================================

@app.route("/api/signup", methods=["POST"])
def api_signup():
    """
    API endpoint to create a new user account.
    Expects JSON with 'username' and 'password' fields.
    
    Returns:
        JSON response with success status and message
    """
    
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # Check if data was received
    if data is None:
        # Return error if no data received
        return jsonify({"success": False, "message": "No data received"}), 400
    
    # Extract username from the data
    username = data.get("username", "")
    
    # Extract password from the data
    password = data.get("password", "")
    
    # Validate that username is not empty
    if not username or not username.strip():
        # Return error if username is empty
        return jsonify({"success": False, "message": "Username is required"}), 400
    
    # Validate that password is not empty
    if not password or not password.strip():
        # Return error if password is empty
        return jsonify({"success": False, "message": "Password is required"}), 400
    
    # Clean up the username by removing extra whitespace
    username = username.strip()
    
    # Clean up the password by removing extra whitespace
    password = password.strip()
    
    # Check minimum length for username (at least 3 characters)
    if len(username) < 3:
        # Return error if username is too short
        return jsonify({"success": False, "message": "Username must be at least 3 characters"}), 400
    
    # Check minimum length for password (at least 4 characters)
    if len(password) < 4:
        # Return error if password is too short
        return jsonify({"success": False, "message": "Password must be at least 4 characters"}), 400
    
    # Call the database function to create the user
    result = database.create_user(username, password)
    
    # Check if user creation was successful
    if result["success"]:
        # Return success response with 201 status (Created)
        return jsonify(result), 201
    else:
        # Return error response with 400 status (Bad Request)
        return jsonify(result), 400

@app.route("/api/login", methods=["POST"])
def api_login():
    """
    API endpoint to verify user credentials and start a session.
    Expects JSON with 'username' and 'password' fields.
    
    Returns:
        JSON response with success status and message
    """
    
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # Check if data was received
    if data is None:
        # Return error if no data received
        return jsonify({"success": False, "message": "No data received"}), 400
    
    # Extract username from the data
    username = data.get("username", "")
    
    # Extract password from the data
    password = data.get("password", "")
    
    # Validate that username is not empty
    if not username or not username.strip():
        # Return error if username is empty
        return jsonify({"success": False, "message": "Username is required"}), 400
    
    # Validate that password is not empty
    if not password or not password.strip():
        # Return error if password is empty
        return jsonify({"success": False, "message": "Password is required"}), 400
    
    # Clean up the username and password
    username = username.strip()
    password = password.strip()
    
    # Call the database function to verify credentials
    result = database.verify_user_login(username, password)
    
    # Check if login was successful
    if result["success"]:
        # Store the user_id in the session to keep them logged in
        session["user_id"] = result["user_id"]
        
        # Store the username in the session for display purposes
        session["username"] = username
        
        # Return success response
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        # Return error response with 401 status (Unauthorized)
        return jsonify(result), 401

@app.route("/api/logout", methods=["POST"])
def api_logout():
    """
    API endpoint to end the user session and log out.
    Clears all session data.
    
    Returns:
        JSON response with success status
    """
    
    # Clear the user_id from the session
    session.pop("user_id", None)
    
    # Clear the username from the session
    session.pop("username", None)
    
    # Clear any other session data that might exist
    session.clear()
    
    # Return success response
    return jsonify({"success": True, "message": "Logged out successfully"}), 200

# ============================================================================
# USER API ROUTES
# ============================================================================

@app.route("/api/user/stats", methods=["GET"])
def api_get_user_stats():
    """
    API endpoint to get the current user's statistics.
    Returns username, games played, games won, and win rate.
    
    Returns:
        JSON response with user stats or error message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Call the database function to get user stats
    result = database.get_user_stats(user_id)
    
    # Check if retrieval was successful
    if result["success"]:
        # Return the stats with 200 status (OK)
        return jsonify(result), 200
    else:
        # Return error with 404 status (Not Found)
        return jsonify(result), 404

@app.route("/api/user/info", methods=["GET"])
def api_get_user_info():
    """
    API endpoint to get the current user's account information.
    Used for the account settings page.
    
    Returns:
        JSON response with user info or error message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Call the database function to get user info
    result = database.get_user_info(user_id)
    
    # Check if retrieval was successful
    if result["success"]:
        # Return the info with 200 status (OK)
        return jsonify(result), 200
    else:
        # Return error with 404 status (Not Found)
        return jsonify(result), 404

@app.route("/api/user/username", methods=["PUT"])
def api_update_username():
    """
    API endpoint to update the current user's username.
    Expects JSON with 'new_username' field.
    
    Returns:
        JSON response with success status and message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # Check if data was received
    if data is None:
        # Return error if no data received
        return jsonify({"success": False, "message": "No data received"}), 400
    
    # Extract the new username from the data
    new_username = data.get("new_username", "")
    
    # Validate that new username is not empty
    if not new_username or not new_username.strip():
        # Return error if new username is empty
        return jsonify({"success": False, "message": "New username is required"}), 400
    
    # Clean up the new username
    new_username = new_username.strip()
    
    # Check minimum length for username (at least 3 characters)
    if len(new_username) < 3:
        # Return error if username is too short
        return jsonify({"success": False, "message": "Username must be at least 3 characters"}), 400
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Call the database function to update username
    result = database.update_username(user_id, new_username)
    
    # Check if update was successful
    if result["success"]:
        # Update the username in the session as well
        session["username"] = new_username
        
        # Return success response
        return jsonify(result), 200
    else:
        # Return error response
        return jsonify(result), 400

@app.route("/api/user/password", methods=["PUT"])
def api_update_password():
    """
    API endpoint to update the current user's password.
    Expects JSON with 'current_password' and 'new_password' fields.
    
    Returns:
        JSON response with success status and message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # Check if data was received
    if data is None:
        # Return error if no data received
        return jsonify({"success": False, "message": "No data received"}), 400
    
    # Extract the current password from the data
    current_password = data.get("current_password", "")
    
    # Extract the new password from the data
    new_password = data.get("new_password", "")
    
    # Validate that current password is not empty
    if not current_password or not current_password.strip():
        # Return error if current password is empty
        return jsonify({"success": False, "message": "Current password is required"}), 400
    
    # Validate that new password is not empty
    if not new_password or not new_password.strip():
        # Return error if new password is empty
        return jsonify({"success": False, "message": "New password is required"}), 400
    
    # Clean up the passwords
    current_password = current_password.strip()
    new_password = new_password.strip()
    
    # Check minimum length for new password (at least 4 characters)
    if len(new_password) < 4:
        # Return error if new password is too short
        return jsonify({"success": False, "message": "New password must be at least 4 characters"}), 400
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Call the database function to update password
    result = database.update_password(user_id, current_password, new_password)
    
    # Check if update was successful
    if result["success"]:
        # Return success response
        return jsonify(result), 200
    else:
        # Return error response
        return jsonify(result), 400

@app.route("/api/user/delete", methods=["DELETE"])
def api_delete_user():
    """
    API endpoint to delete the current user's account.
    This permanently removes the user and all their game history.
    
    Returns:
        JSON response with success status and message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Call the database function to delete the user account
    result = database.delete_user_account(user_id)
    
    # Check if deletion was successful
    if result["success"]:
        # Clear the session since the account no longer exists
        session.clear()
        
        # Return success response
        return jsonify(result), 200
    else:
        # Return error response
        return jsonify(result), 400

# ============================================================================
# GAME API ROUTES
# ============================================================================

@app.route("/api/game/generate", methods=["POST"])
def api_generate_game():
    """
    API endpoint to generate a new quiz with 10 MCQ questions.
    Expects JSON with 'topic' field.
    
    Returns:
        JSON response with questions or error message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # Check if data was received
    if data is None:
        # Return error if no data received
        return jsonify({"success": False, "message": "No data received"}), 400
    
    # Extract the topic from the data
    topic = data.get("topic", "")
    
    # Validate that topic is not empty
    if not topic or not topic.strip():
        # Return error if topic is empty
        return jsonify({"success": False, "message": "Topic is required"}), 400
    
    # Clean up the topic
    topic = topic.strip()
    
    # Call the MCQ generator function to create questions
    result = generate_quiz(topic)
    
    # Check if generation was successful
    if result["success"]:
        # Store the topic in the session for later use (results page)
        session["current_topic"] = topic
        
        # Store the questions in the session for answer verification
        session["current_questions"] = result["questions"]
        
        # Return the questions with 200 status (OK)
        return jsonify(result), 200
    else:
        # Return error response
        return jsonify(result), 500

@app.route("/api/game/submit", methods=["POST"])
def api_submit_game():
    """
    API endpoint to submit game results after completing a quiz.
    Expects JSON with 'answers' (list of user's answers) and 'topic' fields.
    
    Returns:
        JSON response with score, result, and detailed feedback
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the JSON data sent from the frontend
    data = request.get_json()
    
    # Check if data was received
    if data is None:
        # Return error if no data received
        return jsonify({"success": False, "message": "No data received"}), 400
    
    # Extract the user's answers from the data
    user_answers = data.get("answers", [])
    
    # Extract the topic from the data
    topic = data.get("topic", "")
    
    # Get the questions from the session (stored when quiz was generated)
    questions = session.get("current_questions", [])
    
    # Check if questions exist in the session
    if not questions:
        # Return error if no questions found
        return jsonify({"success": False, "message": "No active quiz found"}), 400
    
    # Check if the number of answers matches the number of questions
    if len(user_answers) != len(questions):
        # Return error if answer count doesn't match
        return jsonify({
            "success": False, 
            "message": f"Expected {len(questions)} answers but received {len(user_answers)}"
        }), 400
    
    # Initialize score counter
    score = 0
    
    # Create a list to store detailed results for each question
    detailed_results = []
    
    # Loop through each question and check the answer
    for i, question in enumerate(questions):
        # Get the user's answer for this question (convert to lowercase)
        user_answer = user_answers[i].lower() if i < len(user_answers) else ""
        
        # Get the correct answer (convert to lowercase for comparison)
        correct_answer = question["correct"].lower()
        
        # Check if the answer is correct
        is_correct = (user_answer == correct_answer)
        
        # If correct, increment the score
        if is_correct:
            score += 1
        
        # Add detailed result for this question
        detailed_results.append({
            "question_number": i + 1,                    # Question number (1-10)
            "user_answer": user_answer,                  # What the user selected
            "correct_answer": correct_answer,            # The correct answer
            "is_correct": is_correct,                    # Whether user was correct
            "question": question["question"],            # The question text
            "difficulty": question["difficulty"]         # The difficulty level
        })
    
    # Determine if the user won (score >= 7)
    result = "WON" if score >= 7 else "LOST"
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Use the topic from session if not provided in the request
    if not topic:
        topic = session.get("current_topic", "Unknown Topic")
    
    # Save the game to history and update user stats
    save_result = database.create_game_history(user_id, topic, score, result)
    
    # Clear the current quiz from the session
    session.pop("current_questions", None)
    session.pop("current_topic", None)
    
    # Return the results
    return jsonify({
        "success": True,
        "score": score,                      # Number of correct answers
        "total": 10,                         # Total questions
        "result": result,                    # "WON" or "LOST"
        "topic": topic,                      # The quiz topic
        "detailed_results": detailed_results, # Per-question breakdown
        "saved": save_result["success"]      # Whether history was saved
    }), 200

# ============================================================================
# HISTORY API ROUTES
# ============================================================================

@app.route("/api/history", methods=["GET"])
def api_get_history():
    """
    API endpoint to get the current user's game history.
    Returns a list of all past games.
    
    Returns:
        JSON response with history list or error message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Call the database function to get game history
    result = database.get_game_history(user_id)
    
    # Return the history (always returns 200, even if empty)
    return jsonify(result), 200

@app.route("/api/history/<int:history_id>", methods=["DELETE"])
def api_delete_history(history_id):
    """
    API endpoint to delete a specific game history entry.
    The history_id is passed as part of the URL.
    
    Args:
        history_id: The ID of the history entry to delete
    
    Returns:
        JSON response with success status and message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the current user's ID from the session
    user_id = get_current_user_id()
    
    # Call the database function to delete the history entry
    # Pass both history_id and user_id for security
    result = database.delete_game_history_entry(history_id, user_id)
    
    # Check if deletion was successful
    if result["success"]:
        # Return success response
        return jsonify(result), 200
    else:
        # Return error response with 404 status (Not Found)
        return jsonify(result), 404

# ============================================================================
# LEADERBOARD API ROUTES
# ============================================================================

@app.route("/api/leaderboard", methods=["GET"])
def api_get_leaderboard():
    """
    API endpoint to get the leaderboard data.
    Returns all users ranked by win rate.
    
    Returns:
        JSON response with leaderboard data or error message
    """
    
    # Check if user is logged in
    if not is_logged_in():
        # Return error if not logged in
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    # Get the current user's ID to highlight their row
    current_user_id = get_current_user_id()
    
    # Call the database function to get leaderboard data
    result = database.get_leaderboard()
    
    # Add current_user_id to the response so frontend can highlight the user
    result["current_user_id"] = current_user_id
    
    # Return the leaderboard data
    return jsonify(result), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """
    Handles 404 errors (page not found).
    Returns a JSON error message for API routes, or redirects for pages.
    """
    
    # Check if the request was for an API endpoint
    if request.path.startswith("/api/"):
        # Return JSON error for API requests
        return jsonify({"success": False, "message": "Endpoint not found"}), 404
    else:
        # Redirect to home page for regular page requests
        return redirect(url_for("index"))

@app.errorhandler(500)
def internal_error(error):
    """
    Handles 500 errors (internal server error).
    Returns a JSON error message.
    """
    
    # Return JSON error message
    return jsonify({"success": False, "message": "Internal server error"}), 500

# ============================================================================
# RUN THE APPLICATION
# ============================================================================

# This block only runs if this file is executed directly (not imported)
if __name__ == "__main__":
    # Run the Flask development server
    # debug=True enables auto-reload and detailed error messages
    # host="0.0.0.0" allows access from other devices on the network
    # port=5000 is the default Flask port
    app.run(debug=True, host="0.0.0.0", port=5000)
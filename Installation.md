# MCQ Quiz Game - Complete Installation Guide

Welcome! This guide will walk you through setting up the MCQ Quiz Game project from scratch. 
Follow each step carefully, and you will have the game running in no time.

---

## Table of Contents

1. [What You Need Before Starting](#what-you-need-before-starting)
2. [Folder Structure Overview](#folder-structure-overview)
3. [Step 1: Install Required Software](#step-1-install-required-software)
4. [Step 2: Get Your Google API Key](#step-2-get-your-google-api-key)
5. [Step 3: Set Up the Project Folder](#step-3-set-up-the-project-folder)
6. [Step 4: Create a Virtual Environment](#step-4-create-a-virtual-environment)
7. [Step 5: Install Python Packages](#step-5-install-python-packages)
8. [Step 6: Set Up the Database](#step-6-set-up-the-database)
9. [Step 7: Create the Environment File](#step-7-create-the-environment-file)
10. [Step 8: Run the Application](#step-8-run-the-application)



---

## What You Need Before Starting

Before we begin, make sure you have the following:

- A computer running Windows(my preference), Mac, or Linux
- Internet connection 
- Basic knowledge of using the command line/terminal

---

## Folder Structure Overview

Here is what your project folder will look like when we are done:

```sh
mcq_quiz_game/
|
|-- app.py
|-- database.py
|-- mcq_generator.py
|-- database.sql
|-- .env (create this with your GOOGLE_API_KEY)
|
|-- static/
|   |-- css/
|   |   |-- style.css
|   |-- js/
|       |-- script.js
|
|-- templates/
    |-- login.html
    |-- home.html
    |-- play.html
    |-- quiz.html
    |-- results.html
    |-- leaderboard.html
    |-- account.html
```

---

## Step 1: Install Required Software

We need these software installed on your computer.

### 1.1 Install Python

Python is the programming language we use for the backend.

**For Windows:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow "Download Python 3.x.x" button
3. Run the downloaded installer
4. IMPORTANT: Check the box that says "Add Python to PATH" at the bottom
5. Click "Install Now"
6. Wait for installation to complete
7. Click "Close"

Ps: I dont own a mac so you will have to figure out mac installation on your own

**To verify Python is installed:**
1. Open Command Prompt on Windows.
2. Type this command and press Enter:
```sh
python --version
```
3. You should see something like "Python 3.11.5"

### 1.2 Install XAMPP

XAMPP gives us MySQL database and Apache web server.

1. Go to https://www.apachefriends.org/
2. Click "Download" for your operating system
3. Run the downloaded installer
4. When asked which components to install, make sure these are checked:
   - Apache
   - MySQL
   - PHP
   - phpMyAdmin
5. Choose the installation folder (default is fine)
6. Complete the installation
7. Launch XAMPP Control Panel when done

---

## Step 2: Get Your Google API Key

We need an API key to use Google's Gemini AI for generating questions.

### 2.1 Create a Google Cloud Account

1. Go to https://aistudio.google.com/app/api-keys
2. Sign in with your Google account
3. If asked, agree to the terms of service

### 2.2 Generate an API Key

1. Click "Create API Key"
2. Select "Create API key in new project" or choose an existing project
3. Your API key will be displayed
4. IMPORTANT: Copy this key and save it somewhere safe
5. You will need this key in Step 7

**Note:** Keep your API key secret. Never share it publicly or commit it to GitHub.

---

## Step 3: Set Up the Project Folder

Now we will create the folder structure for our project.

### 3.1 Create the Main Project Folder

**For Windows:**
1. Open File Explorer
2. Navigate to where you want to create the project (like Desktop or Documents)
3. Right-click and select "New" > "Folder"
4. Name it `mcq_quiz_game`
5. Follow the above pattern and create your files (source: Folder Structure Overview)


---
## Step 4: Create a Virtual Environment
### 4.1 Create a Virtual Environment
A virtual environment keeps our project packages separate from other Python projects.

- I create my virtual env using conda

### 4.2 Open Anaconda prompt
### 4.3: run 
```sh
conda create -n myenv python=3.11.0
```
### 4.4: activate the env
```sh
conda activate myenv
```
---
## Step 5: Install Python Packages
Now we will install all the required Python packages.

### 5.1 Create requirements.txt

In your mcq_quiz_game folder, create a new file named requirements.txt

Copy and paste this content:
```sh
Flask==3.0.0
mysql-connector-python==8.2.0
python-dotenv==1.0.0
langchain-google-genai==1.0.10
langchain-core==0.2.10
Werkzeug==3.0.1
Jinja2==3.1.2
```
Save the file

### 5.2 Install All Packages

Make sure your virtual environment is activated (you see your("venv name") in the command line).

Run this command:
```sh
pip install -r requirements.txt
```

### 5.3 Verify Installation
```sh
pip list
```
You should see Flask, mysql-connector-python, and other packages in the list.

---
## Step 6: Set Up the Database
Now we will create the MySQL database for our game.

### 6.1 Start XAMPP
- open XAMPP Control Panel

- Click "Start" next to Apache (it will turn green)

- Click "Start" next to MySQL (it will turn green)

- Both should show "Running" status
- If you see errors:

- - Make sure no other program is using ports 80 or 3306

- - Try running XAMPP as Administrator (Windows)

### 6.2 Open phpMyAdmin
- Open your web browser
- Go to: http://localhost/phpmyadmin
- phpMyAdmin should load (it is a database management tool)
## 6.3 Create the Database
- In phpMyAdmin, click "New" in the left sidebar

- In the "Database name" field, type: mcq_game_db

- Click "Create"

- You should see mcq_game_db appear in the left sidebar
### 6.4 Create the Tables
- Click on mcq_game_db in the left sidebar

- Click the "SQL" tab at the top

- Copy and paste all the SQL code from your database.sql file

- Click "Go" at the bottom

The SQL code to paste:

```sh
-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    games_played INT DEFAULT 0,
    games_won INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the game_history table
CREATE TABLE IF NOT EXISTS game_history (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    topic VARCHAR(100) NOT NULL,
    score INT NOT NULL,
    result VARCHAR(10) NOT NULL,
    played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_game_history_user_id ON game_history(user_id);
CREATE INDEX idx_game_history_played_at ON game_history(played_at);
```
- You should see a green success message

- Click on mcq_game_db again and verify you see users and game_history tables
---
## Step 7: Create the Environment File

### 7.1 Create .env File
- In your mcq_quiz_game folder, create a new file named .env

- Add this line (replace with your actual API key from Step 2):
```sh
GOOGLE_API_KEY="your_actual_api_key_here"
```
Note: make sure to surround your api key with " "

For example:
```sh
GOOGLE_API_KEY="AIzaSyBxxxxxxajdjkh"
```
- Save the file
---
## Step 8: Run the Application
### 8.1 Verify Everything is Ready
Before running, check that:

- XAMPP is running (Apache and MySQL are green)
- Virtual environment is activated (you see (venv))
- All files are in the correct locations
- The .env file has your API key
### 8.2 Start the Flask Application
- In your command prompt (with virtual environment activated), run:
```sh
python app.py
```
What you should see:

```sh
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
 * Restarting with stat
 * Debugger is active!
 ```
### 8.3 Open the Application
- Open your web browser
- Go to: http://localhost:5000
- You should see the login page with "MCQ Quiz Game" title
- Congratulations! The application is running!
---
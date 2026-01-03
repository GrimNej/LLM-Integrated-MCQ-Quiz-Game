/* ============================================================================ */
/* script.js */
/* Main JavaScript file for the MCQ Quiz Game */
/* Contains shared utility functions used across multiple pages */
/* ============================================================================ */

/* ============================================================================ */
/* GLOBAL CONFIGURATION */
/* ============================================================================ */

// API base URL - used for all fetch requests
// Empty string means same origin (current domain)
const API_BASE_URL = '';

// Timeout duration for API requests (in milliseconds)
const API_TIMEOUT = 30000; // 30 seconds

/* ============================================================================ */
/* UTILITY FUNCTIONS */
/* Helper functions used throughout the application */
/* ============================================================================ */

/**
 * Escapes HTML special characters to prevent XSS attacks.
 * This function converts special characters like <, >, &, ", and '
 * into their HTML entity equivalents.
 * 
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text safe for HTML insertion
 * 
 * @example
 * escapeHTML('<script>alert("XSS")</script>')
 * // Returns: '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
 */
function escapeHTML(text) {
    
    // Check if text is null or undefined
    if (text === null || text === undefined) {
        // Return empty string for null/undefined values
        return '';
    }
    
    // Convert to string if not already
    const str = String(text);
    
    // Create a temporary div element
    const div = document.createElement('div');
    
    // Set the text content (this automatically escapes HTML)
    div.textContent = str;
    
    // Return the escaped HTML from innerHTML
    return div.innerHTML;
    
}

/**
 * Formats a date string into a more readable format.
 * Converts ISO date strings or MySQL datetime strings to a friendly format.
 * 
 * @param {string} dateString - The date string to format
 * @returns {string} - The formatted date string
 * 
 * @example
 * formatDate('2024-01-15 14:30:00')
 * // Returns: 'Jan 15, 2024 at 2:30 PM'
 */
function formatDate(dateString) {
    
    // Check if dateString is empty or invalid
    if (!dateString) {
        return 'Unknown date';
    }
    
    try {
        
        // Create a Date object from the string
        const date = new Date(dateString);
        
        // Check if the date is valid
        if (isNaN(date.getTime())) {
            // Return the original string if parsing failed
            return dateString;
        }
        
        // Define options for date formatting
        const options = {
            year: 'numeric',      // Full year (e.g., 2024)
            month: 'short',       // Abbreviated month (e.g., Jan)
            day: 'numeric',       // Day of month (e.g., 15)
            hour: 'numeric',      // Hour
            minute: '2-digit',    // Minutes with leading zero
            hour12: true          // Use 12-hour format with AM/PM
        };
        
        // Format the date using the user's locale
        return date.toLocaleDateString('en-US', options);
        
    } catch (error) {
        
        // Log error for debugging
        console.error('Error formatting date:', error);
        
        // Return the original string if formatting failed
        return dateString;
        
    }
    
}

/**
 * Calculates the win rate percentage from games played and games won.
 * Returns 0 if no games have been played to avoid division by zero.
 * 
 * @param {number} gamesPlayed - Total number of games played
 * @param {number} gamesWon - Number of games won
 * @returns {number} - Win rate as a percentage (0-100), rounded to 1 decimal
 * 
 * @example
 * calculateWinRate(10, 7)
 * // Returns: 70.0
 */
function calculateWinRate(gamesPlayed, gamesWon) {
    
    // Check if gamesPlayed is zero or invalid
    if (!gamesPlayed || gamesPlayed <= 0) {
        // Return 0 to avoid division by zero
        return 0;
    }
    
    // Calculate the win rate as a percentage
    const winRate = (gamesWon / gamesPlayed) * 100;
    
    // Round to 1 decimal place and return
    return Math.round(winRate * 10) / 10;
    
}

/**
 * Validates an email address format.
 * Note: This is a basic validation - not used in current app but useful for future.
 * 
 * @param {string} email - The email address to validate
 * @returns {boolean} - True if valid format, false otherwise
 * 
 * @example
 * validateEmail('user@example.com')
 * // Returns: true
 */
function validateEmail(email) {
    
    // Regular expression for basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    // Test the email against the regex and return result
    return emailRegex.test(email);
    
}

/**
 * Validates username format and length.
 * Username must be 3-50 characters, alphanumeric with underscores allowed.
 * 
 * @param {string} username - The username to validate
 * @returns {object} - Object with 'valid' boolean and 'message' string
 * 
 * @example
 * validateUsername('player_one')
 * // Returns: { valid: true, message: 'Username is valid' }
 */
function validateUsername(username) {
    
    // Check if username is empty
    if (!username || username.trim() === '') {
        return {
            valid: false,
            message: 'Username is required'
        };
    }
    
    // Trim whitespace
    const trimmedUsername = username.trim();
    
    // Check minimum length (3 characters)
    if (trimmedUsername.length < 3) {
        return {
            valid: false,
            message: 'Username must be at least 3 characters'
        };
    }
    
    // Check maximum length (50 characters)
    if (trimmedUsername.length > 50) {
        return {
            valid: false,
            message: 'Username must be less than 50 characters'
        };
    }
    
    // Username is valid
    return {
        valid: true,
        message: 'Username is valid'
    };
    
}

/**
 * Validates password format and length.
 * Password must be at least 4 characters.
 * 
 * @param {string} password - The password to validate
 * @returns {object} - Object with 'valid' boolean and 'message' string
 * 
 * @example
 * validatePassword('mypassword')
 * // Returns: { valid: true, message: 'Password is valid' }
 */
function validatePassword(password) {
    
    // Check if password is empty
    if (!password || password.trim() === '') {
        return {
            valid: false,
            message: 'Password is required'
        };
    }
    
    // Check minimum length (4 characters)
    if (password.length < 4) {
        return {
            valid: false,
            message: 'Password must be at least 4 characters'
        };
    }
    
    // Password is valid
    return {
        valid: true,
        message: 'Password is valid'
    };
    
}

/* ============================================================================ */
/* API HELPER FUNCTIONS */
/* Functions for making API requests to the backend */
/* ============================================================================ */

/**
 * Makes a GET request to the specified API endpoint.
 * Handles errors and returns parsed JSON response.
 * 
 * @param {string} endpoint - The API endpoint (e.g., '/api/user/stats')
 * @returns {Promise<object>} - Promise resolving to the JSON response
 * 
 * @example
 * const stats = await apiGet('/api/user/stats');
 */
async function apiGet(endpoint) {
    
    try {
        
        // Make the GET request
        const response = await fetch(API_BASE_URL + endpoint, {
            
            // Use GET method
            method: 'GET',
            
            // Set headers
            headers: {
                'Content-Type': 'application/json'
            }
            
        });
        
        // Parse the JSON response
        const data = await response.json();
        
        // Check for authentication error
        if (response.status === 401) {
            // Redirect to login page
            window.location.href = '/login';
            return null;
        }
        
        // Return the parsed data
        return data;
        
    } catch (error) {
        
        // Log the error for debugging
        console.error('API GET Error:', error);
        
        // Return error object
        return {
            success: false,
            message: 'Network error. Please check your connection.'
        };
        
    }
    
}

/**
 * Makes a POST request to the specified API endpoint.
 * Sends JSON data and returns parsed JSON response.
 * 
 * @param {string} endpoint - The API endpoint (e.g., '/api/login')
 * @param {object} data - The data to send in the request body
 * @returns {Promise<object>} - Promise resolving to the JSON response
 * 
 * @example
 * const result = await apiPost('/api/login', { username: 'user', password: 'pass' });
 */
async function apiPost(endpoint, data) {
    
    try {
        
        // Make the POST request
        const response = await fetch(API_BASE_URL + endpoint, {
            
            // Use POST method
            method: 'POST',
            
            // Set headers
            headers: {
                'Content-Type': 'application/json'
            },
            
            // Convert data to JSON string
            body: JSON.stringify(data)
            
        });
        
        // Parse the JSON response
        const responseData = await response.json();
        
        // Check for authentication error
        if (response.status === 401) {
            // Redirect to login page
            window.location.href = '/login';
            return null;
        }
        
        // Return the parsed data
        return responseData;
        
    } catch (error) {
        
        // Log the error for debugging
        console.error('API POST Error:', error);
        
        // Return error object
        return {
            success: false,
            message: 'Network error. Please check your connection.'
        };
        
    }
    
}

/**
 * Makes a PUT request to the specified API endpoint.
 * Sends JSON data and returns parsed JSON response.
 * 
 * @param {string} endpoint - The API endpoint (e.g., '/api/user/username')
 * @param {object} data - The data to send in the request body
 * @returns {Promise<object>} - Promise resolving to the JSON response
 * 
 * @example
 * const result = await apiPut('/api/user/username', { new_username: 'newname' });
 */
async function apiPut(endpoint, data) {
    
    try {
        
        // Make the PUT request
        const response = await fetch(API_BASE_URL + endpoint, {
            
            // Use PUT method
            method: 'PUT',
            
            // Set headers
            headers: {
                'Content-Type': 'application/json'
            },
            
            // Convert data to JSON string
            body: JSON.stringify(data)
            
        });
        
        // Parse the JSON response
        const responseData = await response.json();
        
        // Check for authentication error
        if (response.status === 401) {
            // Redirect to login page
            window.location.href = '/login';
            return null;
        }
        
        // Return the parsed data
        return responseData;
        
    } catch (error) {
        
        // Log the error for debugging
        console.error('API PUT Error:', error);
        
        // Return error object
        return {
            success: false,
            message: 'Network error. Please check your connection.'
        };
        
    }
    
}

/**
 * Makes a DELETE request to the specified API endpoint.
 * Returns parsed JSON response.
 * 
 * @param {string} endpoint - The API endpoint (e.g., '/api/history/123')
 * @returns {Promise<object>} - Promise resolving to the JSON response
 * 
 * @example
 * const result = await apiDelete('/api/history/123');
 */
async function apiDelete(endpoint) {
    
    try {
        
        // Make the DELETE request
        const response = await fetch(API_BASE_URL + endpoint, {
            
            // Use DELETE method
            method: 'DELETE',
            
            // Set headers
            headers: {
                'Content-Type': 'application/json'
            }
            
        });
        
        // Parse the JSON response
        const data = await response.json();
        
        // Check for authentication error
        if (response.status === 401) {
            // Redirect to login page
            window.location.href = '/login';
            return null;
        }
        
        // Return the parsed data
        return data;
        
    } catch (error) {
        
        // Log the error for debugging
        console.error('API DELETE Error:', error);
        
        // Return error object
        return {
            success: false,
            message: 'Network error. Please check your connection.'
        };
        
    }
    
}

/* ============================================================================ */
/* UI HELPER FUNCTIONS */
/* Functions for common UI operations */
/* ============================================================================ */

/**
 * Shows a message in a message box element.
 * Updates the text, applies the appropriate class, and makes it visible.
 * 
 * @param {string} boxId - The ID of the message box container element
 * @param {string} textId - The ID of the message text element
 * @param {string} message - The message text to display
 * @param {string} type - The type of message ('success' or 'error')
 * 
 * @example
 * showMessageInBox('message-box', 'message-text', 'Login successful!', 'success');
 */
function showMessageInBox(boxId, textId, message, type) {
    
    // Get reference to the message box container
    const messageBox = document.getElementById(boxId);
    
    // Get reference to the message text element
    const messageText = document.getElementById(textId);
    
    // Check if elements exist
    if (!messageBox || !messageText) {
        // Log warning and return
        console.warn('Message box elements not found:', boxId, textId);
        return;
    }
    
    // Set the message text content
    messageText.textContent = message;
    
    // Remove any existing type classes
    messageBox.classList.remove('success', 'error');
    
    // Add the appropriate type class
    messageBox.classList.add(type);
    
    // Add the 'show' class to make the message visible
    messageBox.classList.add('show');
    
}

/**
 * Hides a message box element.
 * Removes the 'show' class to hide the message.
 * 
 * @param {string} boxId - The ID of the message box container element
 * 
 * @example
 * hideMessageBox('message-box');
 */
function hideMessageBox(boxId) {
    
    // Get reference to the message box container
    const messageBox = document.getElementById(boxId);
    
    // Check if element exists
    if (!messageBox) {
        // Log warning and return
        console.warn('Message box element not found:', boxId);
        return;
    }
    
    // Remove the 'show' class to hide the message
    messageBox.classList.remove('show');
    
}

/**
 * Sets a button to loading state.
 * Disables the button and changes its text to show loading.
 * 
 * @param {string} buttonId - The ID of the button element
 * @param {string} loadingText - The text to display while loading
 * 
 * @example
 * setButtonLoading('submit-button', 'Submitting...');
 */
function setButtonLoadingById(buttonId, loadingText) {
    
    // Get reference to the button element
    const button = document.getElementById(buttonId);
    
    // Check if element exists
    if (!button) {
        // Log warning and return
        console.warn('Button element not found:', buttonId);
        return;
    }
    
    // Disable the button
    button.disabled = true;
    
    // Store the original text in a data attribute
    button.dataset.originalText = button.textContent;
    
    // Change the button text to loading text
    button.textContent = loadingText;
    
    // Add loading class for styling
    button.classList.add('loading');
    
}

/**
 * Resets a button from loading state to normal state.
 * Re-enables the button and restores its original text.
 * 
 * @param {string} buttonId - The ID of the button element
 * 
 * @example
 * resetButtonById('submit-button');
 */
function resetButtonById(buttonId) {
    
    // Get reference to the button element
    const button = document.getElementById(buttonId);
    
    // Check if element exists
    if (!button) {
        // Log warning and return
        console.warn('Button element not found:', buttonId);
        return;
    }
    
    // Re-enable the button
    button.disabled = false;
    
    // Restore the original text from data attribute
    if (button.dataset.originalText) {
        button.textContent = button.dataset.originalText;
    }
    
    // Remove loading class
    button.classList.remove('loading');
    
}

/**
 * Shows a modal dialog by removing the 'hidden' class.
 * 
 * @param {string} modalId - The ID of the modal overlay element
 * 
 * @example
 * showModal('delete-modal');
 */
function showModal(modalId) {
    
    // Get reference to the modal element
    const modal = document.getElementById(modalId);
    
    // Check if element exists
    if (!modal) {
        // Log warning and return
        console.warn('Modal element not found:', modalId);
        return;
    }
    
    // Remove the 'hidden' class to show the modal
    modal.classList.remove('hidden');
    
}

/**
 * Hides a modal dialog by adding the 'hidden' class.
 * 
 * @param {string} modalId - The ID of the modal overlay element
 * 
 * @example
 * hideModal('delete-modal');
 */
function hideModal(modalId) {
    
    // Get reference to the modal element
    const modal = document.getElementById(modalId);
    
    // Check if element exists
    if (!modal) {
        // Log warning and return
        console.warn('Modal element not found:', modalId);
        return;
    }
    
    // Add the 'hidden' class to hide the modal
    modal.classList.add('hidden');
    
}

/* ============================================================================ */
/* STORAGE HELPER FUNCTIONS */
/* Functions for working with sessionStorage and localStorage */
/* ============================================================================ */

/**
 * Saves data to sessionStorage as JSON.
 * sessionStorage data persists only for the current browser tab.
 * 
 * @param {string} key - The key to store the data under
 * @param {any} data - The data to store (will be converted to JSON)
 * 
 * @example
 * saveToSession('quizData', { questions: [], topic: 'Science' });
 */
function saveToSession(key, data) {
    
    try {
        
        // Convert data to JSON string and save to sessionStorage
        sessionStorage.setItem(key, JSON.stringify(data));
        
    } catch (error) {
        
        // Log error for debugging
        console.error('Error saving to sessionStorage:', error);
        
    }
    
}

/**
 * Retrieves data from sessionStorage and parses it from JSON.
 * 
 * @param {string} key - The key to retrieve data from
 * @returns {any} - The parsed data, or null if not found or error
 * 
 * @example
 * const quizData = getFromSession('quizData');
 */
function getFromSession(key) {
    
    try {
        
        // Get the item from sessionStorage
        const item = sessionStorage.getItem(key);
        
        // Check if item exists
        if (item === null) {
            return null;
        }
        
        // Parse JSON and return
        return JSON.parse(item);
        
    } catch (error) {
        
        // Log error for debugging
        console.error('Error reading from sessionStorage:', error);
        
        // Return null on error
        return null;
        
    }
    
}

/**
 * Removes data from sessionStorage.
 * 
 * @param {string} key - The key to remove
 * 
 * @example
 * removeFromSession('quizData');
 */
function removeFromSession(key) {
    
    try {
        
        // Remove the item from sessionStorage
        sessionStorage.removeItem(key);
        
    } catch (error) {
        
        // Log error for debugging
        console.error('Error removing from sessionStorage:', error);
        
    }
    
}

/**
 * Clears all data from sessionStorage.
 * Use with caution as this removes all stored data.
 * 
 * @example
 * clearSession();
 */
function clearSession() {
    
    try {
        
        // Clear all sessionStorage data
        sessionStorage.clear();
        
    } catch (error) {
        
        // Log error for debugging
        console.error('Error clearing sessionStorage:', error);
        
    }
    
}

/* ============================================================================ */
/* MISCELLANEOUS HELPER FUNCTIONS */
/* Other utility functions */
/* ============================================================================ */

/**
 * Debounces a function to limit how often it can be called.
 * Useful for search inputs or resize handlers.
 * 
 * @param {Function} func - The function to debounce
 * @param {number} wait - The delay in milliseconds
 * @returns {Function} - The debounced function
 * 
 * @example
 * const debouncedSearch = debounce(searchFunction, 300);
 * input.addEventListener('input', debouncedSearch);
 */
function debounce(func, wait) {
    
    // Variable to hold the timeout reference
    let timeout;
    
    // Return a new function that wraps the original
    return function executedFunction(...args) {
        
        // Clear any existing timeout
        clearTimeout(timeout);
        
        // Set a new timeout
        timeout = setTimeout(() => {
            
            // Call the original function with the arguments
            func.apply(this, args);
            
        }, wait);
        
    };
    
}

/**
 * Generates a random string of specified length.
 * Useful for generating temporary IDs or tokens.
 * 
 * @param {number} length - The desired length of the string
 * @returns {string} - A random alphanumeric string
 * 
 * @example
 * const id = generateRandomString(8);
 * // Returns something like: 'a7Bx9kL2'
 */
function generateRandomString(length) {
    
    // Characters to use in the random string
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    
    // Variable to hold the result
    let result = '';
    
    // Loop for the specified length
    for (let i = 0; i < length; i++) {
        
        // Get a random index into the characters string
        const randomIndex = Math.floor(Math.random() * characters.length);
        
        // Add the character at that index to the result
        result += characters.charAt(randomIndex);
        
    }
    
    // Return the generated string
    return result;
    
}

/**
 * Checks if the user is on a mobile device.
 * Uses user agent detection (not always reliable but useful for basic checks).
 * 
 * @returns {boolean} - True if on mobile device, false otherwise
 * 
 * @example
 * if (isMobileDevice()) {
 *     // Show mobile-friendly UI
 * }
 */
function isMobileDevice() {
    
    // Regular expression to match mobile user agents
    const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i;
    
    // Test the user agent against the regex
    return mobileRegex.test(navigator.userAgent);
    
}

/**
 * Scrolls to an element smoothly.
 * 
 * @param {string} elementId - The ID of the element to scroll to
 * @param {string} position - Where to position the element ('start', 'center', 'end')
 * 
 * @example
 * scrollToElement('results-section', 'start');
 */
function scrollToElement(elementId, position = 'start') {
    
    // Get the element
    const element = document.getElementById(elementId);
    
    // Check if element exists
    if (!element) {
        console.warn('Element not found for scrolling:', elementId);
        return;
    }
    
    // Scroll to the element with smooth behavior
    element.scrollIntoView({
        behavior: 'smooth',
        block: position
    });
    
}

/**
 * Copies text to the clipboard.
 * Uses the modern Clipboard API with fallback.
 * 
 * @param {string} text - The text to copy to clipboard
 * @returns {Promise<boolean>} - Promise resolving to true if successful
 * 
 * @example
 * const success = await copyToClipboard('Text to copy');
 */
async function copyToClipboard(text) {
    
    try {
        
        // Check if Clipboard API is available
        if (navigator.clipboard && navigator.clipboard.writeText) {
            
            // Use modern Clipboard API
            await navigator.clipboard.writeText(text);
            return true;
            
        } else {
            
            // Fallback for older browsers
            // Create a temporary textarea element
            const textarea = document.createElement('textarea');
            textarea.value = text;
            
            // Make it invisible
            textarea.style.position = 'fixed';
            textarea.style.left = '-9999px';
            
            // Add to document
            document.body.appendChild(textarea);
            
            // Select the text
            textarea.select();
            
            // Execute copy command
            document.execCommand('copy');
            
            // Remove the textarea
            document.body.removeChild(textarea);
            
            return true;
            
        }
        
    } catch (error) {
        
        // Log error for debugging
        console.error('Error copying to clipboard:', error);
        
        return false;
        
    }
    
}

/* ============================================================================ */
/* INITIALIZATION */
/* Code that runs when the script loads */
/* ============================================================================ */

/**
 * Logs that the script has loaded successfully.
 * This helps with debugging to confirm the script is being included.
 */
console.log('MCQ Quiz Game - script.js loaded successfully');

/* ============================================================================ */
/* END OF SCRIPT */
/* ============================================================================ */
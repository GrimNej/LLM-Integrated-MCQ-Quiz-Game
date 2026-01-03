# ============================================================================
# mcq_generator.py
# This file handles the generation of MCQ questions using Google's Gemini API
# It generates questions at three difficulty levels: Easy, Medium, and Hard
# ============================================================================

# Import os module to access environment variables (like API keys)
import os

# Import json module to parse JSON responses from the AI
import json

# Import load_dotenv to load environment variables from a .env file
from dotenv import load_dotenv

# Import the Google Generative AI library for Gemini API
from langchain_google_genai import ChatGoogleGenerativeAI

# Import PromptTemplate to create structured prompts for the AI
from langchain_core.prompts import PromptTemplate

# Import StrOutputParser to convert AI responses to strings
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from the .env file
# This allows us to keep sensitive data like API keys out of our code
load_dotenv()

# Get the Google API key from environment variables
# This key is required to authenticate with the Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ============================================================================
# INITIALIZE THE AI MODEL
# ============================================================================

# Create an instance of the Gemini AI model with specific settings
# api_key: The authentication key for the Gemini API
# model: The specific Gemini model to use (gemini-2.0-flash is fast and capable)
# temperature: Controls randomness (0.3 = more focused, less random)
# max_output_tokens: Maximum length of the AI's response
llm = ChatGoogleGenerativeAI(
    api_key=GOOGLE_API_KEY,      # API key for authentication
    model="gemini-2.5-flash",     # The Gemini model version to use
    temperature=0.3,             # Low temperature for more consistent outputs
    max_output_tokens=2000       # Allow longer responses for multiple questions
)

# ============================================================================
# PROMPT TEMPLATE FOR GENERATING QUESTIONS
# ============================================================================

# This template tells the AI exactly how to format the questions
# We use placeholders {topic}, {number}, and {difficulty} that will be filled in
MCQ_GENERATION_TEMPLATE = """
You are an expert quiz creator. Generate exactly {number} multiple choice questions about the topic: {topic}

Difficulty Level: {difficulty}
- EASY: Basic knowledge questions that most people familiar with the topic would know
- MEDIUM: Intermediate questions requiring deeper understanding
- HARD: Challenging questions that require expert-level knowledge

STRICT REQUIREMENTS:
1. Generate EXACTLY {number} questions, no more, no less
2. Each question must have exactly 4 options labeled a, b, c, d
3. Only ONE option should be correct
4. Output ONLY valid JSON, no additional text or explanation
5. Do not include markdown code blocks or any formatting

OUTPUT FORMAT (follow this exactly):
{{
    "1": {{
        "question": "The question text goes here?",
        "options": {{
            "a": "First option",
            "b": "Second option",
            "c": "Third option",
            "d": "Fourth option"
        }},
        "correct": "a",
        "difficulty": "{difficulty}"
    }},
    "2": {{
        "question": "Second question text?",
        "options": {{
            "a": "First option",
            "b": "Second option",
            "c": "Third option",
            "d": "Fourth option"
        }},
        "correct": "b",
        "difficulty": "{difficulty}"
    }}
}}

Generate the questions now:
"""

# Create a PromptTemplate object from our template string
# input_variables: The placeholders that will be filled in when we use the template
mcq_prompt = PromptTemplate(
    input_variables=["topic", "number", "difficulty"],  # Variables to fill in
    template=MCQ_GENERATION_TEMPLATE                     # The template text
)

# Create a chain that connects the prompt, AI model, and output parser
# The | operator chains them together: prompt -> AI -> parse output as string
mcq_chain = mcq_prompt | llm | StrOutputParser()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clean_json_response(response_text):
    """
    Cleans the AI response to extract valid JSON.
    Sometimes the AI includes markdown code blocks or extra text.
    
    Args:
        response_text: The raw text response from the AI
    
    Returns:
        str: Cleaned text that should be valid JSON
    """
    
    # Remove markdown code block markers if present
    # The AI sometimes wraps JSON in ```json ... ``` blocks
    cleaned = response_text.replace("```json", "")  # Remove opening json marker
    cleaned = cleaned.replace("```", "")             # Remove closing marker
    
    # Remove any leading or trailing whitespace
    cleaned = cleaned.strip()
    
    # Return the cleaned JSON string
    return cleaned

def generate_questions_by_difficulty(topic, number, difficulty):
    """
    Generates a specific number of questions at a given difficulty level.
    
    Args:
        topic: The subject/topic for the questions
        number: How many questions to generate
        difficulty: The difficulty level (EASY, MEDIUM, or HARD)
    
    Returns:
        dict: A dictionary of questions, or None if generation failed
    """
    
    try:
        # Invoke the AI chain with our parameters
        # This sends the prompt to Gemini and gets the response
        raw_response = mcq_chain.invoke({
            "topic": topic,           # The quiz topic
            "number": number,         # Number of questions to generate
            "difficulty": difficulty  # Difficulty level
        })
        
        # Clean the response to get valid JSON
        cleaned_response = clean_json_response(raw_response)
        
        # Parse the JSON string into a Python dictionary
        questions_dict = json.loads(cleaned_response)
        
        # Return the dictionary of questions
        return questions_dict
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, print error for debugging
        print(f"JSON parsing error for {difficulty} questions: {e}")
        print(f"Raw response was: {raw_response}")
        # Return None to indicate failure
        return None
        
    except Exception as e:
        # Catch any other errors (API errors, network issues, etc.)
        print(f"Error generating {difficulty} questions: {e}")
        # Return None to indicate failure
        return None

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_quiz(topic):
    """
    Generates a complete quiz with 10 questions at mixed difficulty levels.
    - 5 Easy questions (questions 1-5)
    - 3 Medium questions (questions 6-8)
    - 2 Hard questions (questions 9-10)
    
    Args:
        topic: The subject/topic for the quiz
    
    Returns:
        dict: Contains 'success' (bool), 'questions' (list), and 'message' (str)
    """
    
    # Check if the topic is empty or just whitespace
    if not topic or not topic.strip():
        # Return error if no topic provided
        return {
            "success": False,
            "message": "Please provide a topic for the quiz",
            "questions": []
        }
    
    # Clean up the topic string by removing extra whitespace
    topic = topic.strip()
    
    # Initialize an empty list to hold all questions
    all_questions = []
    
    # ========================================
    # STEP 1: Generate 5 Easy Questions
    # ========================================
    
    print(f"Generating 5 EASY questions about: {topic}")
    
    # Call the helper function to generate easy questions
    easy_questions = generate_questions_by_difficulty(topic, 5, "EASY")
    
    # Check if generation was successful
    if easy_questions is None:
        # Return error if easy questions failed to generate
        return {
            "success": False,
            "message": "Failed to generate easy questions. Please try again.",
            "questions": []
        }
    
    # Add each easy question to our list
    # The questions are numbered 1-5 in the response
    for key in sorted(easy_questions.keys(), key=lambda x: int(x)):
        # Get the question data
        question_data = easy_questions[key]
        
        # Create a standardized question object
        question_obj = {
            "question_number": len(all_questions) + 1,  # Sequential number (1-5)
            "question": question_data["question"],       # The question text
            "options": question_data["options"],         # The four options
            "correct": question_data["correct"],         # The correct answer letter
            "difficulty": "EASY"                         # Difficulty level
        }
        
        # Add to our list of all questions
        all_questions.append(question_obj)
    
    # ========================================
    # STEP 2: Generate 3 Medium Questions
    # ========================================
    
    print(f"Generating 3 MEDIUM questions about: {topic}")
    
    # Call the helper function to generate medium questions
    medium_questions = generate_questions_by_difficulty(topic, 3, "MEDIUM")
    
    # Check if generation was successful
    if medium_questions is None:
        # Return error if medium questions failed to generate
        return {
            "success": False,
            "message": "Failed to generate medium questions. Please try again.",
            "questions": []
        }
    
    # Add each medium question to our list
    for key in sorted(medium_questions.keys(), key=lambda x: int(x)):
        # Get the question data
        question_data = medium_questions[key]
        
        # Create a standardized question object
        question_obj = {
            "question_number": len(all_questions) + 1,  # Sequential number (6-8)
            "question": question_data["question"],       # The question text
            "options": question_data["options"],         # The four options
            "correct": question_data["correct"],         # The correct answer letter
            "difficulty": "MEDIUM"                       # Difficulty level
        }
        
        # Add to our list of all questions
        all_questions.append(question_obj)
    
    # ========================================
    # STEP 3: Generate 2 Hard Questions
    # ========================================
    
    print(f"Generating 2 HARD questions about: {topic}")
    
    # Call the helper function to generate hard questions
    hard_questions = generate_questions_by_difficulty(topic, 2, "HARD")
    
    # Check if generation was successful
    if hard_questions is None:
        # Return error if hard questions failed to generate
        return {
            "success": False,
            "message": "Failed to generate hard questions. Please try again.",
            "questions": []
        }
    
    # Add each hard question to our list
    for key in sorted(hard_questions.keys(), key=lambda x: int(x)):
        # Get the question data
        question_data = hard_questions[key]
        
        # Create a standardized question object
        question_obj = {
            "question_number": len(all_questions) + 1,  # Sequential number (9-10)
            "question": question_data["question"],       # The question text
            "options": question_data["options"],         # The four options
            "correct": question_data["correct"],         # The correct answer letter
            "difficulty": "HARD"                         # Difficulty level
        }
        
        # Add to our list of all questions
        all_questions.append(question_obj)
    
    # ========================================
    # STEP 4: Verify we have exactly 10 questions
    # ========================================
    
    # Check if we successfully generated all 10 questions
    if len(all_questions) != 10:
        # Return error if we don't have exactly 10 questions
        return {
            "success": False,
            "message": f"Expected 10 questions but got {len(all_questions)}. Please try again.",
            "questions": []
        }
    
    # Log success message
    print(f"Successfully generated 10 questions about: {topic}")
    
    # Return the complete quiz
    return {
        "success": True,
        "message": "Quiz generated successfully",
        "questions": all_questions,
        "topic": topic
    }

# ============================================================================
# TEST FUNCTION (for development/debugging)
# ============================================================================

def test_quiz_generation():
    """
    A simple test function to verify the quiz generation is working.
    Run this file directly to test: python mcq_generator.py
    """
    
    # Print a header for the test
    print("=" * 60)
    print("TESTING MCQ GENERATOR")
    print("=" * 60)
    
    # Define a test topic
    test_topic = "Python Programming"
    
    # Generate a quiz
    print(f"\nGenerating quiz about: {test_topic}\n")
    result = generate_quiz(test_topic)
    
    # Check if generation was successful
    if result["success"]:
        # Print success message
        print("\nQuiz generated successfully!")
        print(f"Total questions: {len(result['questions'])}")
        print("-" * 60)
        
        # Print each question
        for q in result["questions"]:
            # Print question number and difficulty
            print(f"\nQ{q['question_number']} [{q['difficulty']}]:")
            # Print the question text
            print(f"   {q['question']}")
            # Print each option
            for option_key, option_text in q["options"].items():
                print(f"      {option_key.upper()}. {option_text}")
            # Print the correct answer
            print(f"   Correct Answer: {q['correct'].upper()}")
            print("-" * 40)
    else:
        # Print error message
        print(f"\nQuiz generation failed: {result['message']}")
    
    # Print footer
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

# ============================================================================
# RUN TEST IF FILE IS EXECUTED DIRECTLY
# ============================================================================

# This block only runs if this file is executed directly (not imported)
if __name__ == "__main__":
    # Run the test function
    test_quiz_generation()
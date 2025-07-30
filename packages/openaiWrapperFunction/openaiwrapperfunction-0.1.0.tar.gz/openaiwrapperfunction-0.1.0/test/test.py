import os
from openAiWrapper import openai_function, OpenAIWrapper

# Set your Gemini API key from Google AI Studio
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
if GEMINI_API_KEY == "your-gemini-api-key-here":
    print("WARNING: Using placeholder API key. Replace with actual Gemini API key from Google AI Studio.")
OpenAIWrapper.set_api_key(GEMINI_API_KEY)

# Explicitly set Gemini endpoint
OpenAIWrapper.set_base_url("https://generativelanguage.googleapis.com/v1beta/openai/")

# Define a simple math function
@openai_function(model="gemini-1.5-flash-latest")
def calculate_sum(a: int, b: int) -> int:
    """Sum two integers and return the result"""
    return a + b

# Define a text processing function
@openai_function(temperature=0.5)
def format_text(text: str, style: str) -> str:
    """Format text in specified style: uppercase, lowercase, capitalize, or title"""
    if style == "uppercase":
        return text.upper()
    elif style == "lowercase":
        return text.lower()
    elif style == "capitalize":
        return text.capitalize()
    elif style == "title":
        return text.title()
    return text

# Define a programming helper function
@openai_function(max_tokens=300)
def explain_code(code: str) -> str:
    """Explain what the given code does in simple terms"""
    return f"Explanation: {code} performs..."

if __name__ == "__main__":
    print("\n=== Gemini Function Decorator Test ===\n")
    
    # Direct function call - bypasses Gemini
    print("1. Direct call:", calculate_sum(5, 3))  # Should print: 8
    
    # Simulated Gemini call
    print("\n2. Testing Gemini-powered calculation...")
    try:
        # Run with a valid Gemini API key to see actual results
        result = calculate_sum.query("What is 17 plus 24?")
        print("   Gemini calculated sum:", result)
    except Exception as e:
        print(f"   Error: {e}\n   Set a valid Gemini API key to test properly")
    
    # Text formatting example
    print("\n3. Text formatting with direct call:")
    print("   Formatted text:", format_text(text="hello world", style="uppercase"))
    
    # Gemini-powered formatting
    print("\n4. Gemini-powered text formatting:")
    try:
        # Ask Gemini to format text in title case
        formatted = format_text.query("Format this text in title case: the lord of the rings")
        print("   Formatted text:", formatted)
    except Exception as e:
        print(f"   Format error: {e}")
    
    # Code explanation
    print("\n5. Code explanation with Gemini:")
    try:
        # Ask Gemini to explain some code
        code = "def factorial(n): return 1 if n == 0 else n * factorial(n-1)"
        explanation = explain_code.query(f"Explain this code: {code}")
        print("   Code explanation:", explanation)
    except Exception as e:
        print(f"   Explanation error: {e}")
    
    print("\n=== Test Complete ===")

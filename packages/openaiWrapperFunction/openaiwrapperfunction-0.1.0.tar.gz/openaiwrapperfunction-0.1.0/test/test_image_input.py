import os
from openAiWrapper import openai_function, OpenAIWrapper
import base64

def base64_urlencode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Set your Gemini API key from Google AI Studio
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
if GEMINI_API_KEY == "your-gemini-api-key-here":
    print("WARNING: Using placeholder API key. Replace with actual Gemini API key from Google AI Studio.")
OpenAIWrapper.set_api_key(GEMINI_API_KEY)

# Explicitly set Gemini endpoint
OpenAIWrapper.set_base_url("https://generativelanguage.googleapis.com/v1beta/openai/")

@openai_function(temperature=0.7)
def clasify_animal(animal_type: str) -> str:
    """
    Present the lassified animal
    
    :param animal_type: The type of animal
    :return: The prinable name of the main animal in the image
    """

    return f"Animal type: {animal_type}"

if __name__ == "__main__":
    print("=== Testing Image Input with Parameter Description ===")
    
    try:
                
        # Call with image input
        result = clasify_animal.query(
            "What animal is in this image?",
            input_image_url=f"data:image/jpeg;base64,{base64_urlencode_image('./dog.jpeg')}"
        )
        print("\nImage analysis result:", result)
    except Exception as e:
        print(f"Error: {e}")
        print("Ensure you've set a valid Gemini API key and the image URL is accessible")
    
    print("=== Test Complete ===")

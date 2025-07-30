import unittest
import os
from openAiWrapper.decorator import openai_function, AgentOrchestrator, OpenAIWrapper
from dotenv import load_dotenv;

load_dotenv()

# Get API key from environment for tests
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY", "test_api_key")

class TestAgentOrchestration(unittest.TestCase):
    def setUp(self):
        # Set up API configurations
        OpenAIWrapper.set_api_key(API_KEY)
    
    def test_agent_orchestration(self):
        # Define test functions
        @openai_function()
        def add(a: int, b: int) -> int:
            """Add two numbers"""
            return a + b
            
        @openai_function()
        def subtract(a: int, b: int) -> int:
            """Subtract two numbers"""
            return a - b
            
        # Create an orchestrator instance
        orchestrator = AgentOrchestrator(model="gemini-2.5-flash")
        
        # Test with a simple arithmetic expression
        context = "Calculate the result of (8 + 3) - 5"
        result = orchestrator.run(context)
        
        # We expect (8 + 3) - 5 = 6
        self.assertEqual(int(result), 6, f"Expected 6 but got {result}")
        
        # Test with multiple operations
        context = "First add 10 and 20, then subtract 5 from the result"
        result = orchestrator.run(context)
        self.assertEqual(int(result), 25, f"Expected 25 but got {result}")
        
    def test_query_agent_mode(self):
        @openai_function()
        def square(x: int) -> int:
            """Calculate the square of a number"""
            return x * x
            
        @openai_function()
        def add(a: int, b: int) -> int:
            """Add two numbers"""
            return a + b
            
        # Use agent mode through the query method
        context = "First compute the sum of 3 and 4, then calculate the square of that result"
        result = square.query(context, agent_mode=True)
        
        # (3 + 4) = 7, 7^2 = 49
        self.assertEqual(int(result), 49, f"Expected 49 but got {result}")

if __name__ == "__main__":
    unittest.main()

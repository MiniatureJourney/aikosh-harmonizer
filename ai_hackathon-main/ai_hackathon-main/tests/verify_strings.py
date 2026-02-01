import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_service.metadata_generator import generate_metadata


try:
    from harmonizer import get_aikosh_metadata
    
    # We don't need to actually call the API, just importing the modules 
    # might not trigger the error if it's inside a function.
    # But since the error is a ValueError/SyntaxError on f-string evaluation, 
    # it usually happens at runtime when the line is executed.
    
    # Let's try to mock the arguments and call the functions until the point of failure.
    # However, we can just check if the strings are valid.
    
    print("Imports successful. Now checking f-string evaluation (safely)...")

    
    # Check metadata_generator prompt construction
    # We can inspect the code object or just try to trigger the f-string construction.
    # Ideally, we'd mock the client to avoid making API calls.
    
    import pdf_service.metadata_generator as mg
    mg.client = "mock" # Disable client check
    
    # Mock data for generate_metadata
    pages_data = [{"text": "sample text"}]
    
    # Redefine generate_metadata_with_retry to return dummy response so we don't hit API
    class MockResponse:
        text = '{"mock": "response"}'
        
    mg.generate_metadata_with_retry = lambda model, prompt: MockResponse()
    
    # This calls the function which builds the prompt
    mg.generate_metadata(pages_data)
    print("metadata_generator pass: f-string valid.")
    
    import harmonizer as hz
    hz.client = "mock"
    
    class MockRawData:
        filename = "test.csv"
        columns = ["a", "b"]
        sample_data = "1,2"
        
    # Mock client call
    class MockClient:
        class models:
            def generate_content(model, contents):
                return MockResponse()
                
    hz.client = MockClient()
    
    hz.get_aikosh_metadata(MockRawData())
    print("harmonizer pass: f-string valid.")
    
except Exception as e:
    print(f"FAILED: {e}")

# tests/test_integration.py
from src.finbotics.query_processor import QueryProcessor
import json

def test_integrated_queries():
    """Test the integrated query processing system"""
    
    processor = QueryProcessor()
    
    test_queries = [
        "How much did I spend on OpenAI in February?",
        "What are my total expenses for last month?",
        "Show me top 5 vendors by spending",
        "How much did I spend on software?",
        "What's my current runway?",
        "What are my biggest recurring expenses?",
    ]
    
    print("=== Integrated Query Processing Tests ===\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 50)
        
        try:
            result, sources, data_found = processor.process_query(query)
            
            print(f"Data Found: {data_found}")
            print(f"Sources: {sources}")
            print(f"Result:\n{result}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    test_integrated_queries()
# test_classifier.py
from src.finbotics.crew import Finbotics

def test_query_classifier():
    """Test the query classifier with sample queries"""
    
    test_queries = [
        "How much did I spend on OpenAI in February?",
        "What's my current runway?",
        "Show me all Health Insurance expenses",
        "What happened with the Sevenn invoices?",
        "What are my biggest expenses last month?"
    ]
    
    crew = Finbotics().crew()
    
    for query in test_queries:
        print(f"\n\n{'='*50}")
        print(f"Testing query: {query}")
        print('='*50)
        
        result = crew.kickoff(inputs={"user_query": query})
        print(f"Classification Result: {result}")

if __name__ == "__main__":
    test_query_classifier()
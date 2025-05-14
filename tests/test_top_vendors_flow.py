# tests/test_top_vendors_flow.py
from src.finbotics.query_processor import QueryProcessor

def test_top_vendors_flow():
    """Test the complete flow for top vendors queries"""
    
    processor = QueryProcessor()
    
    queries = [
        "show me the top 5 vendors by spending",
        "show me the top 10 vendors by spending",
        "show me the top 15 vendors by spending",
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        
        result, sources, data_found = processor.process_query(query)
        
        print(f"Data found: {data_found}")
        print(f"Sources: {sources}")
        print(f"\nResult:")
        print(result)
        
        # Count how many vendors are in the result
        vendor_count = len([line for line in result.split('\n') if '. ' in line and ': $' in line])
        print(f"\nVendors returned: {vendor_count}")

if __name__ == "__main__":
    test_top_vendors_flow()
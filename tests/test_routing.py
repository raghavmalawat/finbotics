from src.finbotics.orchestrator import QueryOrchestrator

def test_sophisticated_routing():
    """Test the sophisticated query routing system"""
    
    orchestrator = QueryOrchestrator()
    
    test_queries = [
        "How much money did I spend on Health Insurance in February?",
        "What caused the spike in Licenses and Fees in January?",
        "What are notable fluctuations in spend from January to February?",
        "How many months of runway do I have?",
        "What ended up happening with the Sevenn invoices?",
        "What are my biggest recurring expenses?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = orchestrator.process_query(query)
        print(f"\nResult: {result}")

if __name__ == "__main__":
    test_sophisticated_routing()
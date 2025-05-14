# test_basic_csv.py
from crewai_tools import CSVSearchTool
from pathlib import Path
import pandas as pd

def test_csv_tool():
    """Test if CSVSearchTool works with our Excel files"""
    
    data_dir = Path("data/csv")
    ledger_file = data_dir / "Acme+AI_General+Ledger.csv"
    
    print(f"Testing file: {ledger_file}")
    print(f"File exists: {ledger_file.exists()}")
    
    # First try to read with pandas
    try:
        df = pd.read_csv(ledger_file)
        print(f"\nPandas read successful!")
        print(f"Columns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
    except Exception as e:
        print(f"Pandas error: {e}")
    
    # Now try CSVSearchTool
    try:
        csv_tool = CSVSearchTool(
            csv=str(ledger_file),
            config=dict(
				llm=dict(
					provider="google",
					config=dict(
						model="gemini/gemini-1.5-flash",
						# temperature=0.5,
						# top_p=1,
						# stream=true,
					),
				),
				embedder=dict(
					provider="google",
					config=dict(
						model="models/embedding-001",
						task_type="retrieval_document",
						# title="Embeddings",
					),
				),
			)
        )
        result = csv_tool._run("Show me all transactions")
        print(f"\nCSV Tool Result: {result}")
    except Exception as e:
        print(f"CSVSearchTool error: {e}")

if __name__ == "__main__":
    test_csv_tool()
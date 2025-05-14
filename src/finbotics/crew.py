from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import CSVSearchTool, FileReadTool, TXTSearchTool, DirectorySearchTool
from pathlib import Path

from src.finbotics.tools.financial_formatter import FinancialFormatterTool
from src.finbotics.tools.email_search_tool import EmailSearchTool
from src.finbotics.tools.security_tool import SecurityTool

@CrewBase
class Finbotics():
	"""Finbotics crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	data_dir = Path("data/csv")
	email_dir = Path("data/emails")


	def __init__(self):
        # Initialize tools
		self.general_ledger_csv = CSVSearchTool(
            csv=str(self.data_dir / "general_ledger.csv"),
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
		self.expense_summary_csv = CSVSearchTool(
            csv=str(self.data_dir / "expense_summary.csv"),
			config=dict(
				llm=dict(
					provider="google",
					config=dict(
						model="gemini/gemini-1.5-flash",
					),
				),
				embedder=dict(
					provider="google",
					config=dict(
						model="models/embedding-001",
						task_type="retrieval_document",
					),
				),
			)
        )
		self.balance_sheet_csv = CSVSearchTool(
            csv=str(self.data_dir / "balance_sheet.csv"),
			config=dict(
				llm=dict(
					provider="google",
					config=dict(
						model="gemini/gemini-1.5-flash",
					),
				),
				embedder=dict(
					provider="google",
					config=dict(
						model="models/embedding-001",
						task_type="retrieval_document",
					),
				),
			)
        )
		self.profit_loss_csv = CSVSearchTool(
            csv=str(self.data_dir / "profit_loss.csv"),
			config=dict(
				llm=dict(
					provider="google",
					config=dict(
						model="gemini/gemini-1.5-flash",
					),
				),
				embedder=dict(
					provider="google",
					config=dict(
						model="models/embedding-001",
						task_type="retrieval_document",
					),
				),
			)
        )
		self.formatter_tool = FinancialFormatterTool()
		self.file_reader = FileReadTool()
		self.txt_search = DirectorySearchTool(
            directory=str(self.email_dir),
			config=dict(
				llm=dict(
					provider="google",
					config=dict(
						model="gemini/gemini-1.5-flash",
					),
				),
				embedder=dict(
					provider="google",
					config=dict(
						model="models/embedding-001",
						task_type="retrieval_document",
					),
				),
			)
        )
		self.email_search = EmailSearchTool()
		self.security_tool = SecurityTool()

	@agent
	def query_classifier(self) -> Agent:
		return Agent(
            config=self.agents_config['query_classifier'],
            tools=[],  # No tools needed for classification
            verbose=True
        )
	
	@agent
	def query_router(self) -> Agent:
		return Agent(
            config=self.agents_config['query_router'],
            tools=[],
            verbose=True
        )

	@agent
	def expense_analyst(self) -> Agent:
		return Agent(
            config=self.agents_config['expense_analyst'],
            tools=[
                self.general_ledger_csv,
                self.expense_summary_csv,
                self.formatter_tool
            ],
            verbose=True
        )
	
	@agent
	def cash_flow_analyst(self) -> Agent:
		return Agent(
            config=self.agents_config['cash_flow_analyst'],
            tools=[
                self.general_ledger_csv,
                self.profit_loss_csv,
                self.balance_sheet_csv,
                self.formatter_tool
            ],
            verbose=True
        )

	@agent
	def email_context_agent(self) -> Agent:
		return Agent(
            config=self.agents_config['email_context_agent'],
            tools=[
                self.txt_search,
                self.email_search,
                self.file_reader
            ],
            verbose=True
        )

	@agent
	def security_guardian(self) -> Agent:
		return Agent(
            config=self.agents_config['security_guardian'],
            tools=[self.security_tool],
            verbose=True
        )

	@agent
	def report_generator(self) -> Agent:
		return Agent(
            config=self.agents_config['report_generator'],
            tools=[self.formatter_tool],
            verbose=True
        )
    
	@task
	def classify_query_task(self) -> Task:
		return Task(
            config=self.tasks_config['classify_query'],
            agent=self.query_classifier()
        )
	
	@task
	def route_query_task(self) -> Task:
		return Task(
            config=self.tasks_config['route_query'],
            agent=self.query_router()
        )

	@task
	def analyze_vendor_expenses_task(self) -> Task:
		return Task(
            config=self.tasks_config['analyze_vendor_expenses'],
            agent=self.expense_analyst()
        )
	
	@task
	def generate_expense_report_task(self) -> Task:
		return Task(
            config=self.tasks_config['generate_expense_report'],
            agent=self.report_generator()
        )

	@task
	def synthesize_final_response_task(self) -> Task:
		return Task(
            config=self.tasks_config['synthesize_final_response'],
            agent=self.report_generator()
        )
    
	@task
	def route_to_expense_analyst_task(self) -> Task:
		return Task(
            config=self.tasks_config['route_to_expense_analyst'],
            agent=self.query_classifier(),
            context=[self.classify_query_task()]
        )

	@task
	def calculate_burn_rate_task(self) -> Task:
		return Task(
            config=self.tasks_config['calculate_burn_rate'],
            agent=self.cash_flow_analyst()
        )
    
	@task
	def calculate_runway_task(self) -> Task:
		return Task(
            config=self.tasks_config['calculate_runway'],
            agent=self.cash_flow_analyst()
        )
    
	@task
	def search_email_context_task(self) -> Task:
		return Task(
            config=self.tasks_config['search_email_context'],
            agent=self.email_context_agent()
        )
    
	@task
	def validate_data_access_task(self) -> Task:
		return Task(
            config=self.tasks_config['validate_data_access'],
            agent=self.security_guardian()
        )
    
	@crew
	def crew(self) -> Crew:
		"""Creates the Finbotics crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

from typing import Dict, List, Any
from crewai import Crew, Task, Agent
from src.finbotics.crew import Finbotics
from src.finbotics.tools.query_analyzer import QueryAnalyzerTool

class QueryOrchestrator:
    """Orchestrates complex queries across multiple agents"""
    
    def __init__(self):
        self.finbotics = Finbotics()
        self.query_analyzer = QueryAnalyzerTool()
    
    def process_query(self, query: str) -> str:
        """Process a query with intelligent routing"""
        
        # Step 1: Analyze the query
        analysis = self._analyze_query(query)
        
        # Step 2: Create dynamic task flow based on analysis
        tasks = self._create_task_flow(query, analysis)
        
        # Step 3: Select required agents
        agents = self._select_agents(analysis)
        
        # Step 4: Execute crew with dynamic configuration
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process="sequential",
            verbose=True
        )
        
        result = crew.kickoff(inputs={"user_query": query})
        return result
    
    def _analyze_query(self, query: str) -> Dict:
        """Analyze query to understand requirements"""
        # This would use the QueryAnalyzerTool
        analysis_result = self.query_analyzer._run(query)
        
        # Parse the string result into structured data
        # In production, you'd return structured data from the tool
        return {
            "query_type": "expense_analysis",  # Parsed from result
            "entities": ["OpenAI"],
            "time_period": "February 2024",
            "needs_comparison": False,
            "needs_email": False,
            "agents_needed": ["expense_analyst", "report_generator"]
        }
    
    def _create_task_flow(self, query: str, analysis: Dict) -> List[Task]:
        """Create dynamic task flow based on analysis"""
        tasks = []
        
        # Always start with classification
        classify_task = Task(
            description=f"Classify and analyze the query: {query}",
            expected_output="Query classification and routing plan",
            agent=self.finbotics.query_router()
        )
        tasks.append(classify_task)
        
        # Add tasks based on query type
        if analysis["query_type"] == "expense_analysis":
            if len(analysis["entities"]) > 0:
                for entity in analysis["entities"]:
                    expense_task = Task(
                        description=f"Analyze expenses for {entity} in {analysis['time_period']}",
                        expected_output=f"Expense analysis for {entity}",
                        agent=self.finbotics.expense_analyst()
                    )
                    tasks.append(expense_task)
        
        elif analysis["query_type"] == "cash_flow_analysis":
            burn_task = Task(
                description="Calculate current burn rate",
                expected_output="Monthly burn rate",
                agent=self.finbotics.cash_flow_analyst()
            )
            tasks.append(burn_task)
            
            runway_task = Task(
                description="Calculate runway based on burn rate",
                expected_output="Runway in months",
                agent=self.finbotics.cash_flow_analyst(),
                context=[burn_task]
            )
            tasks.append(runway_task)
        
        elif analysis["query_type"] == "trend_analysis":
            trend_task = Task(
                description=f"Analyze spending trends for {analysis['entities'][0]} over time",
                expected_output="Trend analysis with anomalies",
                agent=self.finbotics.expense_analyst()
            )
            tasks.append(trend_task)
        
        # Add email search if needed
        if analysis.get("needs_email", False):
            email_task = Task(
                description=f"Search emails for context about {analysis['entities'][0]}",
                expected_output="Email context and findings",
                agent=self.finbotics.email_context_agent()
            )
            tasks.append(email_task)
        
        # Always end with report generation
        report_task = Task(
            description=f"Generate comprehensive report answering: {query}",
            expected_output="Final formatted report",
            agent=self.finbotics.report_generator(),
            context=[t for t in tasks[1:]]  # All previous tasks as context
        )
        tasks.append(report_task)
        
        return tasks
    
    def _select_agents(self, analysis: Dict) -> List[Agent]:
        """Select required agents based on analysis"""
        agents = [self.finbotics.query_router()]
        
        agent_map = {
            "expense_analyst": self.finbotics.expense_analyst(),
            "cash_flow_analyst": self.finbotics.cash_flow_analyst(),
            "email_context_agent": self.finbotics.email_context_agent(),
            "report_generator": self.finbotics.report_generator()
        }
        
        for agent_name in analysis.get("agents_needed", []):
            if agent_name in agent_map:
                agents.append(agent_map[agent_name])
        
        return agents
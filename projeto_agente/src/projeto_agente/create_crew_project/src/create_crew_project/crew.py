from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv



@CrewBase
class CreateCrewProject():
    """CreateCrewProject crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # 2. Instanciar a ferramenta de Scraping
    scrape_tool = ScrapeWebsiteTool()
    
    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'], # type: ignore[index]
            tools=[self.scrape_tool],  # Ferramenta de scraping para pesquisar URLs
            verbose=True
        )

    @agent
    def lead_copywriter(self) -> Agent:
        return Agent(
            config=self.agents_config['lead_copywriter'], # type: ignore[index]
            verbose=True
        )

    @agent
    def chief_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['chief_editor'], # type: ignore[index]
            verbose=True
        )

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_research_task'], # type: ignore[index]
            output_file='output/briefing.md'
        )

    @task
    def copywriting_task(self) -> Task:
        return Task(
            config=self.tasks_config['copywriting_task'], # type: ignore[index]
            output_file='output/rascunho_copy.md'
        )

    @task
    def editing_task(self) -> Task:
        return Task(
            config=self.tasks_config['editing_task'], # type: ignore[index]
            output_file='output/copy_final.md'
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            agent=self.market_researcher(),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CreateCrewProject crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

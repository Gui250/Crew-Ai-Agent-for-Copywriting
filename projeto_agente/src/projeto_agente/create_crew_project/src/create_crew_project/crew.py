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

    @agent
    def market_researcher(self) -> Agent:
        # Inicializa a ferramenta de scraping diretamente
        scrape_tool = ScrapeWebsiteTool()
        return Agent(
            config=self.agents_config['market_researcher'], # type: ignore[index]
            tools=[scrape_tool],  # Ferramenta de scraping para pesquisar URLs
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

    @agent
    def bi_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['bi_analyst'],
            verbose=True,
            llm="gpt-4o" # Recomendado GPT-4o ou Claude para gerar código de gráficos complexos
        )


    @task
    def dashboard_task(self) -> Task:
        return Task(
            config=self.tasks_config['dashboard_task'],
            agent=self.bi_analyst()
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
        """Creates the CreateCrewProject crew with all tasks"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # Habilitar tracing para debug (opcional)
            # tracing=True,  # Descomente para habilitar tracing detalhado
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
    
    def copywriting_crew(self) -> Crew:
        """Creates a crew specifically for copywriting (without dashboard_task)"""
        # Cria os agentes necessários para copywriting
        copywriting_agents = [
            self.market_researcher(),  # Para pesquisa
            self.lead_copywriter(),    # Para escrita
            self.chief_editor()        # Para revisão
        ]
        
        # Filtra apenas as tasks de copywriting na ordem correta:
        # 1. research_task - pesquisa com URL (se fornecida) ou conhecimento geral
        # 2. copywriting_task - escreve o copy baseado no briefing
        # 3. editing_task - revisa e finaliza o copy
        copywriting_tasks = [
            self.research_task(),      # Pesquisa inicial (com suporte a URL)
            self.copywriting_task(),   # Escrita do copy
            self.editing_task()        # Revisão final
        ]
        
        # Tenta desabilitar eventos problemáticos
        crew_kwargs = {
            "agents": copywriting_agents,
            "tasks": copywriting_tasks,
            "process": Process.sequential,
            "verbose": True,
        }
        
        # Tenta passar step_callback=None para desabilitar callbacks de eventos
        try:
            # Algumas versões do CrewAI suportam step_callback=None
            crew_kwargs["step_callback"] = None
        except (TypeError, ValueError):
            # Se não suportar, continua sem esse parâmetro
            pass
        
        return Crew(**crew_kwargs)
    
    def dashboard_crew(self) -> Crew:
        """Creates a crew specifically for dashboard generation"""
        return Crew(
            agents=[self.bi_analyst()],
            tasks=[self.dashboard_task()],
            process=Process.sequential,
            verbose=True,
        )

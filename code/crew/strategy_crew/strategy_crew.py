from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
openai_api_key = os.getenv("OPENAI_API_KEY")


class PlantState(BaseModel):
    # cot: str = Field(..., title="cot", description="chain of thought of the model, how it arrived to the answer.")
    suggestions: str = Field(
        ...,
        title="suggestions",
        description="suggestions of the model, what it thinks should be done.",
    )
    confirmation: str = Field(
        ...,
        title="confirmation",
        description="confirmation that the actions should be retried.",
    )


@CrewBase
class PlantStrategyCrew:
    """Plant Operator Crew"""

    ### Words only
    # agents_config = "config/strategy_agent.yaml"
    # tasks_config = "config/reprompting_task.yaml"

    ### Modelica code
    # agents_config = "config/strategy_agent_modelica_code.yaml"
    # tasks_config = "config/reprompting_task_modelica_code.yaml"

    ### P&ID
    agents_config = "config/strategy_agent_pnid.yaml"
    tasks_config = "config/reprompting_task_pnid.yaml"

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    @agent
    def reprompt_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["reprompt_agent"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def reprompt_strategy(self) -> Task:
        return Task(
            config=self.tasks_config["reprompt_strategy"],
            output_json=PlantState,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the crew to solve the plant model"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

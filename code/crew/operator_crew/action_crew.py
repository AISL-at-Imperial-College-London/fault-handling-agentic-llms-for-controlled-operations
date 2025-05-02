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
    valve_in0: float = Field(..., title="valve_in01", description="valve_in01 position")
    valve_in1: float = Field(..., title="valve_in02", description="valve_in02 position")
    valve_in2: float = Field(..., title="valve_in03", description="valve_in03 position")
    valve_out: float = Field(..., title="valve_out", description="valve_out position")
    valve_pump_tank_B201: float = Field(
        ..., title="valve_pump_tank_B201", description="valve_pump_tank_B201 position"
    )
    valve_pump_tank_B202: float = Field(
        ..., title="valve_pump_tank_B202", description="valve_pump_tank_B202 position"
    )
    valve_pump_tank_B203: float = Field(
        ..., title="valve_pump_tank_B203", description="valve_pump_tank_B203 position"
    )
    valve_pump_tank_B204: float = Field(
        ..., title="valve_pump_tank_B204", description="valve_pump_tank_B204 position"
    )
    pump_power: float = Field(
        ..., title="pump_power", description="pump_power position"
    )


@CrewBase
class PlantOperatorCrew:
    """Plant Operator Crew"""

    ### Words only
    # agents_config = "config/agents_words.yaml"
    # tasks_config = "config/tasks_words.yaml"

    ### Modelica code
    # agents_config = "config/agents_modelica_code.yaml"
    # tasks_config = "config/tasks_modelica_code.yaml"

    ### P&ID
    agents_config = "config/agents_pnid.yaml"
    tasks_config = "config/tasks_pnid.yaml"

    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    @agent
    def plant_operator(self) -> Agent:
        return Agent(
            config=self.agents_config["plant_operator"],
            llm=self.llm,
            # tools=[code_interpreter],
            verbose=True,
        )

    @task
    def plant_operation(self) -> Task:
        return Task(
            config=self.tasks_config["plant_operation"],
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

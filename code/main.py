import pandas as pd
from crewai.flow.flow import Flow, listen, router, start, or_
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import sys
import os

from crew.operator_crew.action_crew import PlantOperatorCrew
from crew.strategy_crew.strategy_crew import PlantStrategyCrew
from simulation.digital_twin_simulation import digital_twin
from validation_script import action_validation, power_validation
from simulation.mixer_plant import plant

sys.stdout.reconfigure(encoding="utf-8")
openai_api_key = os.getenv("OPENAI_API_KEY")


class ExampleState(BaseModel):
    B201_level: float = 0.022
    B202_level: float = 0.022
    B203_level: float = 0.022
    B204_level: float = 0.022
    valve_in0: int = 1
    valve_in1: int = 0
    valve_in2: int = 0
    valve_out: int = 0
    valve_pump_tank_B201: int = 0
    valve_pump_tank_B202: int = 0
    valve_pump_tank_B203: int = 0
    valve_pump_tank_B204: int = 0
    pump_power: float = 0.2
    init_state: int = 0

    message: list = []
    plant_message: list = []
    B201_level_list: list = []
    B202_level_list: list = []
    B203_level_list: list = []
    B204_level_list: list = []
    valve_in0_list: list = []
    valve_in1_list: list = []
    valve_in2_list: list = []
    valve_out_list: list = []
    valve_pump_tank_B201_list: list = []
    valve_pump_tank_B202_list: list = []
    valve_pump_tank_B203_list: list = []
    valve_pump_tank_B204_list: list = []
    pump_power_list: list = []

    plant_B201_level_list: list = []
    plant_B202_level_list: list = []
    plant_B203_level_list: list = []
    plant_B204_level_list: list = []
    plant_valve_in0_list: list = []
    plant_valve_in1_list: list = []
    plant_valve_in2_list: list = []
    plant_valve_out_list: list = []
    plant_valve_pump_tank_B201_list: list = []
    plant_valve_pump_tank_B202_list: list = []
    plant_valve_pump_tank_B203_list: list = []
    plant_valve_pump_tank_B204_list: list = []
    plant_pump_power_list: list = []

    plant_states: dict = {}
    digital_twin_states: dict = {}
    action_valid: bool = False
    action_required: str = ""
    power_valid: bool = False
    power_required: str = ""
    terminate: bool = False
    anom_clogging: int = 0
    anom_valve_in0: int = 0
    issue_flagged: str = ""
    confirmation: str = ""
    reprompting_suggestions: str = ""
    reprompt_cot: str = ""

    total_input_tokens_list: list = []
    total_output_tokens_list: list = []
    total_tokens_list: list = []
    itr_input_tokens_list: list = []
    itr_output_tokens_list: list = []
    itr_token_list: list = []
    init_state_list: list = []
    total_tokens: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    reprompt_counts: list = []
    max_itr: int = 3
    reprompt: int = 0
    fault_detected: str = ""
    iterations: int = 0
    plant_structure: dict = {}
    current_state: str = ""


class RouterFlow(Flow[ExampleState]):
    @start()
    def initialize(self):
        print("Initializing....")
        self.state.B201_level = plant_states["B201_level"]
        self.state.B202_level = plant_states["B202_level"]
        self.state.B203_level = plant_states["B203_level"]
        self.state.B204_level = plant_states["B204_level"]
        self.state.valve_in0 = plant_states["valve_in0"]
        self.state.valve_in1 = plant_states["valve_in1"]
        self.state.valve_in2 = plant_states["valve_in2"]
        self.state.valve_out = plant_states["valve_out"]
        self.state.valve_pump_tank_B201 = plant_states["valve_pump_tank_B201"]
        self.state.valve_pump_tank_B202 = plant_states["valve_pump_tank_B202"]
        self.state.valve_pump_tank_B203 = plant_states["valve_pump_tank_B203"]
        self.state.valve_pump_tank_B204 = plant_states["valve_pump_tank_B204"]
        self.state.pump_power = plant_states["pump_power"]
        self.state.anom_clogging = plant_states["anom_clogging"]
        self.state.anom_valve_in0 = plant_states["anom_valve_in0"]
        self.state.init_state = plant_states["init_state"]

        if self.state.anom_clogging == 1:
            self.state.fault_detected = "clogging"
        elif self.state.anom_valve_in0 == 1:
            self.state.fault_detected = "valve_in0 malfunction"
        self.state.plant_states = {
            "B201_level": 0.022,
            "B202_level": 0.022,
            "B203_level": 0.022,
            "B204_level": 0.022,
            "valve_in0": 1,
            "valve_in1": 0,
            "valve_in2": 0,
            "valve_out": 0,
            "valve_pump_tank_B201": 0,
            "valve_pump_tank_B202": 0,
            "valve_pump_tank_B203": 0,
            "valve_pump_tank_B204": 0,
            "pump_power": 0.2,
            "anom_clogging": 1,
            "anom_valve_in0": 0,
            "init_state": 0,
        }
        self.state.plant_structure = {
            "valve_in0": "tank_B201",
            "tank_B201": "valve_pump_tank_B201",
            "valve_in1": "tank_B202",
            "tank_B202": "valve_pump_tank_B202",
            "valve_in2": "tank_B203",
            "tank_B203": "valve_pump_tank_B203",
            "valve_pump_tank_B204": "tank_B204",
            "tank_B204": "valve_out",
            "valve_pump_tank_B201": "pump_n_in",
            "valve_pump_tank_B202": "pump_n_in",
            "valve_pump_tank_B203": "pump_n_in",
            "pump_n_in": "valve_pump_tank_B204",
        }

        self.state.current_state = "fill_tank_B201"

    @listen(or_(initialize, "next_itr"))
    def monitoring_agent(self):
        print("Monitoring....")
        self.state.B201_level = self.state.plant_states["B201_level"]
        self.state.B202_level = self.state.plant_states["B202_level"]
        self.state.B203_level = self.state.plant_states["B203_level"]
        self.state.B204_level = self.state.plant_states["B204_level"]
        self.state.valve_in0 = self.state.plant_states["valve_in0"]
        self.state.valve_in1 = self.state.plant_states["valve_in1"]
        self.state.valve_in2 = self.state.plant_states["valve_in2"]
        self.state.valve_out = self.state.plant_states["valve_out"]
        self.state.valve_pump_tank_B201 = self.state.plant_states[
            "valve_pump_tank_B201"
        ]
        self.state.valve_pump_tank_B202 = self.state.plant_states[
            "valve_pump_tank_B202"
        ]
        self.state.valve_pump_tank_B203 = self.state.plant_states[
            "valve_pump_tank_B203"
        ]
        self.state.valve_pump_tank_B204 = self.state.plant_states[
            "valve_pump_tank_B204"
        ]
        self.state.pump_power = self.state.plant_states["pump_power"]
        self.state.anom_clogging = self.state.plant_states["anom_clogging"]
        self.state.anom_valve_in0 = self.state.plant_states["anom_valve_in0"]
        self.state.init_state = self.state.plant_states["init_state"]

    @listen(or_(monitoring_agent, "iterate"))
    def action_agent(self):
        print("Taking Action...")
        output = (
            PlantOperatorCrew()
            .crew()
            .kickoff(
                inputs={
                    "B201_level": self.state.plant_states["B201_level"],
                    "B202_level": self.state.plant_states["B202_level"],
                    "B203_level": self.state.plant_states["B203_level"],
                    "B204_level": self.state.plant_states["B204_level"],
                    "valve_in0": self.state.plant_states["valve_in0"],
                    "valve_in1": self.state.plant_states["valve_in1"],
                    "valve_in2": self.state.plant_states["valve_in2"],
                    "valve_out": self.state.plant_states["valve_out"],
                    "valve_pump_tank_B201": self.state.plant_states[
                        "valve_pump_tank_B201"
                    ],
                    "valve_pump_tank_B202": self.state.plant_states[
                        "valve_pump_tank_B202"
                    ],
                    "valve_pump_tank_B203": self.state.plant_states[
                        "valve_pump_tank_B203"
                    ],
                    "valve_pump_tank_B204": self.state.plant_states[
                        "valve_pump_tank_B204"
                    ],
                    "pump_power": self.state.plant_states["pump_power"],
                    "fault_detected": self.state.fault_detected,
                    "reprompting_suggestions": self.state.reprompting_suggestions,
                    "plant_structure": self.state.plant_structure,
                }
            )
        )
        self.state.reprompting_suggestions = ""
        self.state.plant_states["valve_in0"] = output["valve_in0"]
        self.state.plant_states["valve_in1"] = output["valve_in1"]
        self.state.plant_states["valve_in2"] = output["valve_in2"]
        self.state.plant_states["valve_out"] = output["valve_out"]
        self.state.plant_states["valve_pump_tank_B201"] = output["valve_pump_tank_B201"]
        self.state.plant_states["valve_pump_tank_B202"] = output["valve_pump_tank_B202"]
        self.state.plant_states["valve_pump_tank_B203"] = output["valve_pump_tank_B203"]
        self.state.plant_states["valve_pump_tank_B204"] = output["valve_pump_tank_B204"]
        self.state.plant_states["pump_power"] = output["pump_power"]
        self.state.message.append(output.raw)

        self.state.valve_in0_list.append(self.state.plant_states["valve_in0"])
        self.state.valve_in1_list.append(self.state.plant_states["valve_in1"])
        self.state.valve_in2_list.append(self.state.plant_states["valve_in2"])
        self.state.valve_out_list.append(self.state.plant_states["valve_out"])
        self.state.valve_pump_tank_B201_list.append(
            self.state.plant_states["valve_pump_tank_B201"]
        )
        self.state.valve_pump_tank_B202_list.append(
            self.state.plant_states["valve_pump_tank_B202"]
        )
        self.state.valve_pump_tank_B203_list.append(
            self.state.plant_states["valve_pump_tank_B203"]
        )
        self.state.valve_pump_tank_B204_list.append(
            self.state.plant_states["valve_pump_tank_B204"]
        )

        self.state.total_input_tokens += output.token_usage.prompt_tokens
        self.state.total_output_tokens += output.token_usage.completion_tokens
        self.state.total_tokens += output.token_usage.total_tokens

    @listen(action_agent)
    def digital_twin_agent(self):
        self.state.digital_twin_states = self.state.plant_states.copy()
        self.state.digital_twin_states = digital_twin(self.state.digital_twin_states)
        self.state.init_state_list.append(self.state.digital_twin_states["init_state"])
        self.state.B201_level_list.append(self.state.digital_twin_states["B201_level"])
        self.state.B202_level_list.append(self.state.digital_twin_states["B202_level"])
        self.state.B203_level_list.append(self.state.digital_twin_states["B203_level"])
        self.state.B204_level_list.append(self.state.digital_twin_states["B204_level"])
        self.state.pump_power_list.append(self.state.digital_twin_states["pump_power"])

    @router(digital_twin_agent)
    def validation_agent(self):
        print("Validating....")
        if self.state.reprompt < self.state.max_itr:
            print("Validating....")
            self.state.action_valid, self.state.action_required = action_validation(
                self.state.digital_twin_states
            )
            self.state.power_valid, self.state.power_required = power_validation(
                self.state.digital_twin_states
            )
            print("Printing_validation....")
            print(self.state.action_valid, self.state.action_required)
            print(self.state.power_valid, self.state.power_required)

            if self.state.action_valid and self.state.power_valid:
                return "to_plant"
            else:
                if self.state.action_valid:
                    self.state.issue_flagged = self.state.power_required
                elif self.state.power_valid:
                    self.state.issue_flagged = self.state.action_required
                else:
                    self.state.issue_flagged = (
                        self.state.action_required + " and " + self.state.power_required
                    )
                return "reprompt"
        else:
            return "max_itr"

    @router("reprompt")
    def reprompting_agent(self):
        print("Reprompting....")
        self.state.reprompt += 1
        output = (
            PlantStrategyCrew()
            .crew()
            .kickoff(
                inputs={
                    "B201_level": self.state.plant_states["B201_level"],
                    "B202_level": self.state.plant_states["B202_level"],
                    "B203_level": self.state.plant_states["B203_level"],
                    "B204_level": self.state.plant_states["B204_level"],
                    "valve_in0": self.state.plant_states["valve_in0"],
                    "valve_in1": self.state.plant_states["valve_in1"],
                    "valve_in2": self.state.plant_states["valve_in2"],
                    "valve_out": self.state.plant_states["valve_out"],
                    "valve_pump_tank_B201": self.state.plant_states[
                        "valve_pump_tank_B201"
                    ],
                    "valve_pump_tank_B202": self.state.plant_states[
                        "valve_pump_tank_B202"
                    ],
                    "valve_pump_tank_B203": self.state.plant_states[
                        "valve_pump_tank_B203"
                    ],
                    "valve_pump_tank_B204": self.state.plant_states[
                        "valve_pump_tank_B204"
                    ],
                    "pump_power": self.state.plant_states["pump_power"],
                    "issue_flagged": self.state.issue_flagged,
                    "fault_detected": self.state.fault_detected,
                    "plant_structure": self.state.plant_structure,
                }
            )
        )
        self.state.total_input_tokens += output.token_usage.prompt_tokens
        self.state.total_output_tokens += output.token_usage.completion_tokens
        self.state.total_tokens += output.token_usage.total_tokens

        self.state.reprompt_cot = output.raw
        self.state.reprompting_suggestions = output["suggestions"]
        self.state.confirmation = output["confirmation"]
        return "iterate"

    @router(or_("to_plant", "max_itr"))
    def pass_to_plant(self):
        self.state.plant_states = plant(self.state.plant_states)
        ### Add bookkeeping here
        self.state.plant_valve_in0_list.append(self.state.plant_states["valve_in0"])
        self.state.plant_valve_in1_list.append(self.state.plant_states["valve_in1"])
        self.state.plant_valve_in2_list.append(self.state.plant_states["valve_in2"])
        self.state.plant_valve_out_list.append(self.state.plant_states["valve_out"])
        self.state.plant_valve_pump_tank_B201_list.append(
            self.state.plant_states["valve_pump_tank_B201"]
        )
        self.state.plant_valve_pump_tank_B202_list.append(
            self.state.plant_states["valve_pump_tank_B202"]
        )
        self.state.plant_valve_pump_tank_B203_list.append(
            self.state.plant_states["valve_pump_tank_B203"]
        )
        self.state.plant_valve_pump_tank_B204_list.append(
            self.state.plant_states["valve_pump_tank_B204"]
        )
        self.state.plant_B201_level_list.append(self.state.plant_states["B201_level"])
        self.state.plant_B202_level_list.append(self.state.plant_states["B202_level"])
        self.state.plant_B203_level_list.append(self.state.plant_states["B203_level"])
        self.state.plant_B204_level_list.append(self.state.plant_states["B204_level"])
        self.state.plant_pump_power_list.append(self.state.plant_states["pump_power"])
        self.state.total_input_tokens_list.append(self.state.total_input_tokens)
        self.state.total_output_tokens_list.append(self.state.total_output_tokens)
        self.state.total_tokens_list.append(self.state.total_tokens)
        self.state.reprompt_counts.append(self.state.reprompt)
        self.state.reprompt = 0

        df = pd.DataFrame(
            {
                "B201_level": self.state.plant_B201_level_list,
                "B202_level": self.state.plant_B202_level_list,
                "B203_level": self.state.plant_B203_level_list,
                "B204_level": self.state.plant_B204_level_list,
                "valve_in0": self.state.plant_valve_in0_list,
                "valve_in1": self.state.plant_valve_in1_list,
                "valve_in2": self.state.plant_valve_in2_list,
                "valve_out": self.state.plant_valve_out_list,
                "valve_pump_tank_B201": self.state.plant_valve_pump_tank_B201_list,
                "valve_pump_tank_B202": self.state.plant_valve_pump_tank_B202_list,
                "valve_pump_tank_B203": self.state.plant_valve_pump_tank_B203_list,
                "valve_pump_tank_B204": self.state.plant_valve_pump_tank_B204_list,
                "pump_power": self.state.plant_pump_power_list,
            }
        )
        df.to_csv("plant_op.csv", index=False)
        df = pd.DataFrame(
            {
                "reprompts": self.state.reprompt_counts,
                "total_input_tokens": self.state.total_input_tokens_list,
                "total_output_tokens": self.state.total_output_tokens_list,
                "total_tokens": self.state.total_tokens_list,
            }
        )
        df.to_csv("llm_plant_op.csv", index=False)
        df = pd.DataFrame(
            {
                "B201_level": self.state.B201_level_list,
                "B202_level": self.state.B202_level_list,
                "B203_level": self.state.B203_level_list,
                "B204_level": self.state.B204_level_list,
                "valve_in0": self.state.valve_in0_list,
                "valve_in1": self.state.valve_in1_list,
                "valve_in2": self.state.valve_in2_list,
                "valve_out": self.state.valve_out_list,
                "valve_pump_tank_B201": self.state.valve_pump_tank_B201_list,
                "valve_pump_tank_B202": self.state.valve_pump_tank_B202_list,
                "valve_pump_tank_B203": self.state.valve_pump_tank_B203_list,
                "valve_pump_tank_B204": self.state.valve_pump_tank_B204_list,
                "init_state": self.state.init_state_list,
                "pump_power": self.state.pump_power_list,
            }
        )
        df.to_csv("digital_twin_op.csv", index=False)

        if self.state.plant_states["B204_level"] > 0.055:
            self.state.terminate = True
        self.state.reprompt = 0
        if self.state.terminate:
            return "terminate"
        else:
            return "next_itr"

    @listen("terminate")
    def terminate_agent(self):
        print("Terminating....")


if __name__ == "__main__":
    flow = RouterFlow()
    plant_states = {
        "B201_level": 0.022,
        "B202_level": 0.033,
        "B203_level": 0.033,
        "B204_level": 0.044,
        "valve_in0": 0,
        "valve_in1": 0,
        "valve_in2": 0,
        "valve_out": 0,
        "valve_pump_tank_B201": 0,
        "valve_pump_tank_B202": 1,
        "valve_pump_tank_B203": 0,
        "valve_pump_tank_B204": 1,
        "pump_power": 0.2,
        "anom_clogging": 1,
        "anom_valve_in0": 0,
        "init_state": 4,
    }
    flow.kickoff(inputs=plant_states)
    flow.plot()

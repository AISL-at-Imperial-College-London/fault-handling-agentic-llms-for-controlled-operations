import pandas as pd
from simulation.mixer_sim import run_sim
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def digital_twin(plant_states):
    with open("simulation/mixer_digital_twin.json") as f:
        setup = json.load(f)

    B201_level = plant_states["B201_level"]
    B202_level = plant_states["B202_level"]
    B203_level = plant_states["B203_level"]
    B204_level = plant_states["B204_level"]
    if (
        B201_level < 0.032
        and B202_level < 0.032
        and B203_level < 0.032
        and B204_level < 0.023
    ):  #### Filling tank B201
        init_state = 0
    elif (
        B201_level > 0.032
        and B202_level < 0.032
        and B203_level < 0.032
        and B204_level < 0.023
    ):  #### Filling tank B202
        init_state = 1
    elif (
        B201_level > 0.032
        and B202_level > 0.032
        and B203_level < 0.032
        and B204_level < 0.023
    ):  #### Filling tank B203
        init_state = 2
    elif B204_level > 0.021 and B204_level < 0.032:  ### State emptying tank B201
        init_state = 3
    elif B204_level > 0.032 and B204_level < 0.044:  ### State emptying tank B202
        init_state = 4
    elif B204_level > 0.044 and B204_level < 0.055:  ### State emptying tank B203
        init_state = 5
    elif B204_level < 0.056:  ### State emptying tank B204
        init_state = 6

    plant_states["init_state"] = init_state
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["B201_level"] = (
        plant_states["B201_level"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["B202_level"] = (
        plant_states["B202_level"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["B203_level"] = (
        plant_states["B203_level"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["B204_level"] = (
        plant_states["B204_level"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["valve_in0_input"] = (
        plant_states["valve_in0"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["valve_in1_input"] = (
        plant_states["valve_in1"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["valve_in2_input"] = (
        plant_states["valve_in2"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["valve_out_input"] = (
        plant_states["valve_out"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"][
        "valve_pump_tank_B201_input"
    ] = plant_states["valve_pump_tank_B201"]
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"][
        "valve_pump_tank_B202_input"
    ] = plant_states["valve_pump_tank_B202"]
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"][
        "valve_pump_tank_B203_input"
    ] = plant_states["valve_pump_tank_B203"]
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"][
        "valve_pump_tank_B204_input"
    ] = plant_states["valve_pump_tank_B204"]
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["init_state"] = (
        plant_states["init_state"]
    )
    setup["ds2"]["model"]["modules"]["mixer0"]["init_states"]["pump_power"] = (
        plant_states["pump_power"]
    )
    if plant_states["anom_clogging"] == 1:
        setup["ds2"]["model"]["modules"]["mixer0"]["faults"]["anom_clogging"] = True
    else:
        setup["ds2"]["model"]["modules"]["mixer0"]["faults"]["anom_clogging"] = False
    if plant_states["anom_valve_in0"] == 1:
        setup["ds2"]["model"]["modules"]["mixer0"]["faults"]["anom_valve_in0"] = True
    else:
        setup["ds2"]["model"]["modules"]["mixer0"]["faults"]["anom_valve_in0"] = False

    for i in setup:
        run_sim(sim_setup=setup[i], modus="hybrid", states=True)

    with open("simulation/mixer_digital_twin.json", "w") as f:
        json.dump(setup, f, indent=4)

    df = pd.read_csv("../data/ds2/ds2_hybrid_s.csv")

    plant_states["B201_level"] = df["mixer0.tank_B201.level"].iloc[-1]
    plant_states["B202_level"] = df["mixer0.tank_B202.level"].iloc[-1]
    plant_states["B203_level"] = df["mixer0.tank_B203.level"].iloc[-1]
    plant_states["B204_level"] = df["mixer0.tank_B204.level"].iloc[-1]
    plant_states["init_state"] = init_state

    return plant_states

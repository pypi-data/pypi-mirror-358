import numpy as np
from pydrake.systems.framework import DiagramBuilder

from pydrake.multibody.plant import (AddMultibodyPlant, MultibodyPlantConfig)
from pydrake.geometry import SceneGraphConfig

from utilities.world_features import add_plate
from utilities.compare_models import ballDynamics_2D

from roboball_plant.create_ball_plant import add_planar_roboball

import time
from tabulate import tabulate

builder = DiagramBuilder()
sceneConfig = SceneGraphConfig()
sceneConfig.default_proximity_properties.compliance_type = "compliant"
plant, scene_graph = AddMultibodyPlant(
    MultibodyPlantConfig(
        time_step=0.001,
        penetration_allowance=0.001,
        contact_surface_representation="polygon",
        contact_model="hydroelastic"
        ), sceneConfig, 
    builder)


# insert a table (plant, angle [deg])
plant = add_plate(plant, 0.0)

plant, model_idx = add_planar_roboball(plant)
print(plant)

diagram = builder.Build()

diagram_context = diagram.CreateDefaultContext()
robot_context = diagram.GetMutableSubsystemContext(plant, diagram_context)

print(plant.GetStateNames())
# set initial positions

q0 = [00, 0.0, 1.57, 1.57]
plant.SetPositions(robot_context, q0)

mass_time = time.time()
m_mtx = plant.CalcMassMatrix(robot_context)
mass_time = time.time() - mass_time
mass_time*= 1000
print("M(q): \n", m_mtx)

Hq_time = time.time()
Hq = plant.CalcBiasTerm(robot_context) + plant.CalcGravityGeneralizedForces(robot_context)
Hq_time = time.time() - Hq_time
Hq_time*=1000
print("C(q) + V(q): \n", Hq)

ball = ballDynamics_2D()

q0 = np.hstack((q0, [0, 0, 0, 0]))

m_hand_time = time.time()
m_mtx_hand = ball.M(q0)
m_hand_time = time.time() - m_hand_time
m_hand_time*=1000
print("M(q)_HandCalcs: \n", m_mtx_hand)

h_hand_time = time.time()
h_mtx_hand = ball.H(q0)
h_hand_time = time.time() - h_hand_time
h_hand_time*=1000 
print("C(q) + V(q)_handCalcs: \n", ball.H(q0)) # gotta append for velocities

# Create a table with the results
table = [
    ["Method", " M(q) time (ms)", "H(q) time (ms)"],
    ["drake calcs", mass_time, Hq_time],
    ["hand calcs", m_hand_time, h_hand_time],
    ["Difference", str(mass_time - m_hand_time), str(Hq_time - h_hand_time)],
    ["frequency (1/time) (kHz)", 1/mass_time, 1/Hq_time]
]

print(tabulate(table, headers="firstrow", tablefmt="grid"))
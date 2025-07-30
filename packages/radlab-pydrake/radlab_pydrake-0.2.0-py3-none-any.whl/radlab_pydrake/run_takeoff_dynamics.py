import numpy as np
import matplotlib.pyplot as plt

from pydrake.systems.framework import DiagramBuilder
from pydrake.systems.analysis import Simulator

from pydrake.multibody.plant import (AddMultibodyPlant, MultibodyPlantConfig)
from pydrake.geometry import SceneGraphConfig, StartMeshcat

from utilities.world_features import add_plate
from roboball_plant.create_ball_plant import (
    add_RoboBall_plant
)
from roboball_controllers.swing_up_controllers import SpongEnergySwingUp

from pydrake.all import Multiplexer, Demultiplexer, AddDefaultVisualization, LogVectorOutput


meshcat = StartMeshcat()
meshcat.Set2dRenderMode()


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

plant, model_idx = add_RoboBall_plant(plant, place_in_stand="drive")
state_demuxer = builder.AddSystem(Demultiplexer(len(plant.GetStateNames())))
pos_muxer = builder.AddSystem(Multiplexer(4))
vel_muxer = builder.AddSystem(Multiplexer(4))

controller = builder.AddSystem(SpongEnergySwingUp(plant, model_idx, [10,10,1]))
print(plant.GetStateNames())
builder.Connect(plant.get_state_output_port(), state_demuxer.get_input_port())
for i in range(4): # connect positions
    builder.Connect(state_demuxer.get_output_port(i), pos_muxer.get_input_port(i))
for i in range(4):
    builder.Connect(state_demuxer.get_output_port(i+4), vel_muxer.get_input_port(i))

builder.Connect(pos_muxer.get_output_port(), controller.GetInputPort("q"))
builder.Connect(vel_muxer.get_output_port(), controller.GetInputPort("dq"))

builder.Connect(controller.GetOutputPort("tau_m"), plant.get_actuation_input_port())

AddDefaultVisualization(builder, meshcat)
controller_logger = LogVectorOutput(controller.get_output_port(), builder)
state_logger = LogVectorOutput(plant.get_state_output_port(), builder)

diagram = builder.Build()

diagram_context = diagram.CreateDefaultContext()
robot_context = diagram.GetMutableSubsystemContext(plant, diagram_context)

# set initial positions

q0 = [00, 0.3, 0.0, 0.0]
plant.SetPositions(robot_context, q0)
# print("M(q): \n", plant.CalcMassMatrix(robot_context))
# Hq = plant.CalcBiasTerm(robot_context) + plant.CalcGravityGeneralizedForces(robot_context)
# print("C(q) + V(q): \n", Hq)

# from utilities.compare_models import ballDynamics_2D
# ball = ballDynamics_2D()

# q0 = np.hstack((q0, [0, 0, 0, 0]))

# print("M(q)_HandCalcs: \n", ball.M(q0))
# print("C(q) + V(q)_handCalcs: \n", ball.H(q0)) # gotta append for velocities

simulator = Simulator(diagram, diagram_context)

meshcat.StartRecording()
simulator.set_target_realtime_rate(1)
simulator.AdvanceTo(10)
meshcat.PublishRecording()

# pull and plot logs
input_log = controller_logger.FindLog(simulator.get_context())
state_log = state_logger.FindLog(simulator.get_context())

input_times = input_log.sample_times()
state_times = state_log.sample_times()

input_data = input_log.data().transpose()
state_data = state_log.data().transpose()

y_idx = plant.GetStateNames().index("RoboBall_URDF_planar_joint_y")

plt.figure()
plt.plot(state_times, state_data[:, y_idx], label='ball height')
plt.legend()
plt.grid()

plt.figure()
plt.plot(input_times, input_data, label=["tau_m"])
plt.legend()
plt.grid()
plt.show()

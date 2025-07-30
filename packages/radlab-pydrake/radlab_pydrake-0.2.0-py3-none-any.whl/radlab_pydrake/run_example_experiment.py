from pydrake.systems.framework import DiagramBuilder
from pydrake.systems.analysis import Simulator

from pydrake.multibody.plant import (AddMultibodyPlant, MultibodyPlantConfig)
from pydrake.geometry import SceneGraphConfig, StartMeshcat

from utilities.world_features import add_plate
from roboball_plant.create_ball_plant import (
    add_RoboBall_plant,
)
from roboball_plant.pneumatics_system import DynamicPressureModel
from roboball_controllers.icra_2024_controllers import build_icra_2024_controllers

from utilities.sim_debugging import plot_diagram

from pydrake.all import ConstantVectorSource, Multiplexer, Demultiplexer, AddDefaultVisualization
from pydrake.math import RollPitchYaw
from numpy import deg2rad

meshcat = StartMeshcat()


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

plant = add_plate(plant, 0.0, visible=True)

plant, model_idx = add_RoboBall_plant(plant)

# add the pnumatics system to run in the background
pressure_sys = builder.AddSystem(DynamicPressureModel(manual=True))
# default to states off
zero_signal = builder.AddSystem(ConstantVectorSource([0]))
builder.Connect(zero_signal.get_output_port(), pressure_sys.get_solenoid_control)
builder.Connect(zero_signal.get_output_port(), pressure_sys.get_compressor_control)



control_muxer = builder.AddSystem(Multiplexer(2))
controller = builder.AddSystem(build_icra_2024_controllers())

# add feedback to controller
state_names = plant.GetStateNames()
print(state_names)
steer_q_idx = state_names.index("RoboBall_URDF_steer_q")
drive_q_idx = state_names.index("RoboBall_URDF_drive_q")
steer_w_idx = state_names.index("RoboBall_URDF_steer_w")
drive_w_idx = state_names.index("RoboBall_URDF_drive_w")
pipe_w_idx  = state_names.index("RoboBall_URDF_pitch_center_wx")
state_demux = builder.AddSystem(Demultiplexer(len(state_names)))
builder.Connect(plant.get_state_output_port(), state_demux.get_input_port())

# convert the quaternion its the first 4 states
quat_muxer = builder.AddSystem(Multiplexer(4))
rpy_demuxer = builder.AddSystem(Demultiplexer(3))
converter = builder.AddSystem(knematic_transformer())

for i in range(4):
    builder.Connect(state_demux.get_output_port(i), quat_muxer.get_input_port(i))
builder.Connect(quat_muxer.get_output_port(), converter.quat_input) 
builder.Connect(converter.rpy_output, rpy_demuxer.get_input_port())                   
 
# connect states for feedback
builder.Connect(rpy_demuxer.get_output_port(0), controller.GetInputPort("Pipe_Angle"))
builder.Connect(state_demux.get_output_port(pipe_w_idx), controller.GetInputPort("dPipe_Angle"))
builder.Connect(state_demux.get_output_port(steer_q_idx), controller.GetInputPort("Steer_Angle"))
builder.Connect(state_demux.get_output_port(steer_w_idx), controller.GetInputPort("dSteer_Angle"))


# connect controller output
builder.Connect(controller.GetOutputPort("tau_drive_steer"), plant.get_actuation_input_port())

AddDefaultVisualization(builder, meshcat)

diagram = builder.Build()

# define initial conditions
q = RollPitchYaw(deg2rad([0, 0,90])).ToQuaternion()
q0 = [q.w(), q.x(), q.y(), q.z(), 0, 0, 0.3, 0, 0.1] 
v0 = [0, 0, 0, 0, 0, 0, 0, 0]
IC_context = diagram.CreateDefaultContext()
robot_context = diagram.GetMutableSubsystemContext(plant, IC_context)

plant.SetPositions(robot_context, model_idx, q0)
plant.SetVelocities(robot_context, model_idx, v0)

# set the initial tank pressures as a separat subsystem
p0 = [120, 2] # initial tank and ball pressure
pressure_context = diagram.GetMutableSubsystemContext(pressure_sys, IC_context)
pressure_context.SetContinuousState(p0)


simulator = Simulator(diagram, IC_context)

meshcat.StartRecording()
simulator.set_target_realtime_rate(1)
simulator.AdvanceTo(10)
meshcat.PublishRecording()


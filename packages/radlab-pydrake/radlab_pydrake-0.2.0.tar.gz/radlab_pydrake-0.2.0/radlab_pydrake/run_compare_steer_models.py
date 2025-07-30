import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pandas as pd

from pydrake.systems.framework import DiagramBuilder

from pydrake.multibody.plant import (AddMultibodyPlant, MultibodyPlantConfig)
from pydrake.geometry import SceneGraphConfig
from pydrake.all import Simulator, LogVectorOutput, AddDefaultVisualization, Meshcat, Demultiplexer, Multiplexer, ConstantVectorSource

from utilities.world_features import add_plate
from utilities.compare_models import Pravecek_2025_Model, PravModelWithEmpiricalShellFingerprint

from roboball_plant.create_ball_plant import add_RoboBall_plant, update_bedliner_properties
from roboball_plant.joint_modifiers import StictionModel_Majd
from roboball_plant.data.plot_these_files import add_avg_data_to_plot

def plot_test_data(ax,log_directory, plot_peaks=False):
    peaks = None
    first_time = None
    data = pd.read_csv(log_directory, header=0)
    # timestep is in nanoseconds
    data[['timestamp']] = data[['timestamp']] *1e-9

    peaks, _ = find_peaks(data['ball_roll.velocity'], height=0.05, distance=50)
    idx = 2 # the manually selected peak to start the sim at
    first_time = data['timestamp'].iloc[peaks].values
    ax[0].plot(data[['timestamp']].values- first_time[idx],data[['ball_roll.position']].values, label="pipe angle data")
    ax[2].plot(data[['timestamp']].values- first_time[idx],data[['roll_joint.position']].values, label="Steer_Angle")
    ax[1].plot(data[['timestamp']].values- first_time[idx],data[['ball_roll.velocity']].values, label="pipe_vel")
    ax[3].plot(data[['timestamp']].values- first_time[idx],data[['roll_joint.velocity']].values, label="Steer_vel")
    init_pipe_angle = data['ball_roll.position'].iloc[peaks].values
    init_pipe_velocity = data["ball_roll.velocity"].iloc[peaks].values
    init_pend_angle = data["roll_joint.position"].iloc[peaks].values
    init_pend_veloctiy = data["roll_joint.velocity"].iloc[peaks].values

    if plot_peaks:
        ax[1].plot(first_time, init_pipe_velocity, 'x')
    return first_time[idx], init_pipe_angle[idx], init_pipe_velocity[idx], init_pend_angle[idx], init_pend_veloctiy[idx]

def plot_prav_model(ax, init_conditions, tf, time_offset, configs=(None,)):
    # set up the drake sim
    
    # Create a simple block diagram containing our system
    if "tau_flat" in configs:
        sys = PravModelWithEmpiricalShellFingerprint()
        sys.set_pressure = 3.6
    else:
        sys = Pravecek_2025_Model()

    builder = DiagramBuilder()
    mySys = builder.AddSystem(sys)  # add SimplerLinearSystem to diagram
   # wire loggers for data logging 
    logger_output = LogVectorOutput(mySys.get_output_port(), builder) # log the state output port
    
    if "stiction" in configs:
        steer_friction = builder.AddSystem(StictionModel_Majd([0.5, 0.8, 0.23]))
      
        state_demuxer = builder.AddSystem(Demultiplexer(4))
        # demux the states
        builder.Connect(mySys.get_state_output_port, # split the state vector
                        state_demuxer.get_input_port())
        
        builder.Connect(state_demuxer.get_output_port(3),  # connect the steer speed
                        steer_friction.velocity_input_port)

        # Apply the calculated friction torque back to the joint
        builder.Connect(steer_friction.torque_output_port, mySys.torque_input_port)
    else:
        zero_signal = builder.AddSystem(ConstantVectorSource([0]))
        builder.Connect(zero_signal.get_output_port(), mySys.torque_input_port)
    diagram = builder.Build()

    # set ic's for pravecek model
    q0_p = [init_conditions[0], 
            init_conditions[0] + init_conditions[2],
            init_conditions[1], 
            init_conditions[1] + init_conditions[3]] # [phi, theta_g, dphi, dtheta_g]
    context = diagram.CreateDefaultContext()
    context.SetContinuousState(q0_p)

    # create the simulator, the modified context with the ICs must be included
    simulator = Simulator(diagram, context)
    simulator.AdvanceTo(tf)

    # Grab output results from Logger:
    log = logger_output.FindLog(context) # find output log with that context
    time = log.sample_times()
    data = log.data().transpose()

    # Grab input results from Logger:

    ax[0].plot(time, data[:, 0], label=f'Pravecek et al. - {configs}')
    ax[1].plot(time, data[:, 2], label=f'Pravecek et al. - {configs}')
    ax[2].plot(time, data[:, 1], label=f'Pravecek et al. - {configs}')
    ax[3].plot(time, data[:, 3], label=f'Pravecek et al. - {configs}')

    return ax

def plot_drake_model(ax, initi_conditions, tf, time_offset, config, new_proximity=None, meshcat=None):
    builder = DiagramBuilder()
    
    sceneConfig = SceneGraphConfig()
    sceneConfig.default_proximity_properties.compliance_type = "compliant"

    # check config conflicts:
    if ("soft" in config) and ("point" in config):
        raise ValueError("Cannot model both point and soft models")
    
    # check configs to set up sim
    if "soft" in config:
        plant, scene_graph = AddMultibodyPlant(
            MultibodyPlantConfig(
                time_step=0.001,
                penetration_allowance=0.001,
                contact_surface_representation="polygon",
                contact_model="hydroelastic"
                ), 
                sceneConfig, 
            builder)
    elif "point" in config:
        plant, scene_graph = AddMultibodyPlant(
            MultibodyPlantConfig(
                time_step=0.001,
                contact_model="point"
                ), builder)

    # insert a table (plant, angle [deg])
    plant = add_plate(plant, 0.0, visible=False)

    plant, model_idx = add_RoboBall_plant(plant, place_in_stand="steer", lumpy_bedliner=("lumpy" in config))
    
    try:
        if new_proximity:
            update_bedliner_properties(scene_graph, new_proximity)
    except ValueError:
         if new_proximity.any():
            update_bedliner_properties(scene_graph, new_proximity)

    drake_logger = LogVectorOutput(plant.get_state_output_port(), builder)
     
    if "stiction" in config:
        steer_friction = builder.AddSystem(StictionModel_Majd([0.204, 0.45, 10, 0.1, 1]))
        steer_w_idx = plant.GetStateNames().index("RoboBall_URDF_steer_w")
        
        steer_q_idx = plant.GetStateNames().index("RoboBall_URDF_steer_q")
        steer_motor_idx = plant.GetActuatorNames().index("RoboBall_URDF_steer")
      
        state_demuxer = builder.AddSystem(Demultiplexer(plant.num_multibody_states()))
        # demux the states
        builder.Connect(plant.get_state_output_port(), # split the state vector
                        state_demuxer.get_input_port())
        
        builder.Connect(state_demuxer.get_output_port(steer_w_idx),  # connect the steer speed
                        steer_friction.velocity_input_port)

        # Apply the calculated friction torque back to the joint
        builder.Connect(steer_friction.torque_output_port, plant.get_actuation_input_port())
    if meshcat:
        AddDefaultVisualization(builder, meshcat)
    diagram = builder.Build()

    diagram_context = diagram.CreateDefaultContext()
    
    drake_model_context = diagram.GetMutableSubsystemContext(plant, diagram_context)
    # print(plant.GetStateNames())
    # set initial positions for drake model
    q0 = [00, 0.304, initi_conditions[0], initi_conditions[2]]
    v0 = [0,0, initi_conditions[1], initi_conditions[3]]
    plant.SetPositions(drake_model_context, q0)
    # plant.SetVelocities(drake_model_context, v0)

    simulator = Simulator(diagram, diagram_context)

    if meshcat:
        meshcat.StartRecording()
    simulator.AdvanceTo(tf)
    if meshcat:
        meshcat.PublishRecording()


    # plot the models
    drake_log = drake_logger.FindLog(simulator.get_context())
    drake_data = drake_log.data().transpose()

    config_str = f""
    if "point" in config:
        config_str = f"{config} "
    elif "soft" in config:
        try:
            if new_proximity == [1.2e5, 0.75]:
                config_str = f"{config} with Hand-Tuned Parameters"
            elif new_proximity == [1.55201e5, 0.405]:
                config_str = f"{config} with Optimized Parameters"
            else:
                config_str = f"{config} with Estimated Contact Parameters"
        except ValueError:
            config_str = "optimizing"

    # ax[4].plot(drake_log.sample_times()+ time_offset, drake_data[:, 1], label=f'drake - y - {config} - {new_proximity}')
    data = {"time": drake_log.sample_times(),
            "pipe": drake_data[:, 2],
            "pend": drake_data[:, 3]}
    
    try:
        # plot pipe angle
        ax[0].plot(drake_log.sample_times(), drake_data[:, 2], label=f'Drake - '+ config_str)
        # plot pipe speed
        ax[1].plot(drake_log.sample_times(), drake_data[:, 6], label=f'Drake - '+ config_str)
        # plot theta_g
        ax[2].plot(drake_log.sample_times(), drake_data[:, 3], label=f'Drake - '+ config_str)
        # plot dtheta_g
        ax[3].plot(drake_log.sample_times(), drake_data[:, 7], label=f'Drake - '+ config_str)
    
        return ax, data
    except TypeError:
        # if ax is None return it
        return None, data
   


if __name__=="__main__":
    meshcat = Meshcat()
    fig, ax_point = plt.subplots(4,1, sharex=True)
    fig, ax_soft = plt.subplots(4,1, sharex=True)
    fig, ax_prav = plt.subplots(4,1, sharex=True)
    # make sure ax are in the form:
    # ax = [phi, dphi, theta, dtheta]
    # pull the initial condition from the datafile
    directory = "./roboball_plant/data/steering_data/init_RAL_draft_data/trimmed_output"
    ax_prav,_,_ = add_avg_data_to_plot(ax_prav, directory) # same log same function dont need those vals
    ax_point,_,_ = add_avg_data_to_plot(ax_point, directory) # same log same function dont need those vals
    ax_soft, pipe0, pend0 = add_avg_data_to_plot(ax_soft, directory)
    # make sure IC's are in the form:
    # [phi, dphi, theta, dtheta]
    q0 = [pipe0["mean"][0], 0, pend0["mean"][0], 0 ]
    tf = pipe0["time"][-1] # final integrating time
    tuned_proximity = [1.2e5, 0.75]

    peak_times=0
   

    # ax_prav = plot_prav_model(ax_prav, q0, tf, peak_times, ("tau_flat",))
    # ax_prav, _ = plot_drake_model(ax_prav, q0, tf, peak_times, ("point",))
    # ax_prav, _ = plot_drake_model(ax_prav, q0, tf, peak_times, ("soft", "stiction"), [1.55201e5, 0.405])


    # ax_point = plot_prav_model(ax_point, q0, tf, peak_times, ("point", ))
    # ax_point, _ = plot_drake_model(ax_point, q0, tf, peak_times, ("point",))
    # ax_point, _ = plot_drake_model(ax_point, q0, tf, peak_times, ("point", "stiction"))
    # ax_point, _ = plot_drake_model(ax_point, q0, tf, peak_times, ("point", "stiction", "lumpy"))


    ax_soft, _ = plot_drake_model(ax_soft, q0, tf, peak_times, ("soft", "stiction"))
    ax_soft, _ = plot_drake_model(ax_soft, q0, tf, peak_times, ("soft", "stiction"), tuned_proximity)
    ax_soft, _ = plot_drake_model(ax_soft, q0, tf, peak_times, ("soft", "stiction"), [162487.50634276445, 0.2619369242963999]) # red line
    ax_soft,_ = plot_drake_model(ax_soft, q0, tf, peak_times, ("soft", "stiction"), [1.55201e5, 0.405]) # purple line

    # plot just the pipe and pend angle
    # Create a new figure and axis
    pipe_fig1, pipe_ax_point = plt.subplots(2, 1, sharex=True, figsize=(6,8))
    pipe_fig2, pipe_ax_soft = plt.subplots(2, 1, sharex=True, figsize=(6,8))
    pipe_fig3, pipe_ax_prav = plt.subplots(2, 1, sharex=True, figsize=(6,8))
    lines_point = ax_point[0].get_lines()
    lines_soft = ax_soft[0].get_lines()
    lines_prav = ax_prav[0].get_lines()

    lines_point_v = ax_point[2].get_lines()
    lines_soft_v =   ax_soft[2].get_lines()
    lines_prav_v =   ax_prav[2].get_lines()

    pipe_ax_soft[0].set_title("Responses of Models with Hydroelastic Contact")
    pipe_ax_point[0].set_title("Responses of Models with Point Contact")
    pipe_ax_prav[0].set_title("Pravecek's Models Compared with Modular Model")

    # Replot line data in the new axis
    for line in lines_point:
        pipe_ax_point[0].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
    for line in lines_soft:
        pipe_ax_soft[0].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
    for line in lines_prav:
        pipe_ax_prav[0].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())

    
    ''' plot the pend_angle '''
    # Replot the robot data in the new axis
    line = ax_soft[1].get_lines()[0] # add the averaged data added to the wrong axis
    pipe_ax_soft[1].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())

    line = ax_point[1].get_lines()[0] # add the averaged data added to the wrong axis
    pipe_ax_point[1].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())

    line = ax_prav[1].get_lines()[0] # add the averaged data added to the wrong axis
    pipe_ax_prav[1].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
   
    for line in lines_point_v:
        pipe_ax_point[1].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
    for line in lines_soft_v: 
        pipe_ax_soft[1].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
    for line in lines_prav_v:
        pipe_ax_prav[1].plot(line.get_xdata(), line.get_ydata(), label=line.get_label())

    new_axes = [pipe_ax_point, pipe_ax_soft, pipe_ax_prav]
    #pull the shaded std dev bounds
    for new_ax in new_axes:
        new_ax[0].fill_between(pipe0['time'], pipe0["lower"], pipe0["upper"], linestyle="--",color='gray', alpha=0.3, label='±1 Std Dev')
        new_ax[1].fill_between(pend0['time'], pend0["lower"], pend0["upper"], linestyle="--",color='gray', alpha=0.3, label='±1 Std Dev')
        # set all the fun stuff
        new_ax[1].set_xlabel("time (s)")
        new_ax[0].set_ylabel("pipe angle: $\phi$ (rad)")
        new_ax[0].set_xlim(left=0, right=tf)
        new_ax[0].grid()
        new_ax[1].set_ylabel("pend angle: $\\theta$ (rad)")
        new_ax[1].set_xlim(left=0, right=tf)
        new_ax[1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.15))
        new_ax[1].grid()

    plt.show()

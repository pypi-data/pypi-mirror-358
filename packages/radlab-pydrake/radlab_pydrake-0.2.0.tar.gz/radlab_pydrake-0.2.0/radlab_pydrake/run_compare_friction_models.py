from mpl_interactions import zoom_factory, panhandler

from pydrake.all import (
    Demultiplexer, 
    Multiplexer, 
    DiagramBuilder,
    SceneGraphConfig,
    AddMultibodyPlant,
    MultibodyPlantConfig,
    Simulator,
    AddDefaultVisualization
)
from pydrake.systems.primitives import LogVectorOutput
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import optuna


from roboball_plant.create_ball_plant import add_RoboBall_plant
from roboball_plant.joint_modifiers import StictionModel, StictionModel_Majd
from roboball_plant.data.plot_these_files import (
    plot_and_export_average_with_std, 
    get_csv_files
    )


def objective(trial):
    f_w = trial.suggest_float("f_w", 0.01, 3)
    f_c = trial.suggest_float("f_c", 0.01, 3)
    sigma = trial.suggest_float("sigma", 0.1, 9.5)
    w_c = trial.suggest_float("w_c", 0.01, 2)
    n = trial.suggest_float("n", 0.01, 5)

    params = [f_w, f_c, sigma, w_c, n]

    try:
        sim_times, sim_data = run_test(meshcat, starting_angle, StictionModel_Majd, params)
        sim_interp = np.interp(exp_time, sim_times, sim_data)
        mse = np.mean((sim_interp - exp_data)**2)
        return mse

    except Exception as e:
        print(f"Simulation failed at {params}: {e}")
        return np.inf



def plot_test_data(ax,log_directory, data_label, individual_traces=False):
    '''
        plot the testing logs for friction validation
        @param ax: plt axes object to layer the plots on
        @param log_directory: path to group of csv files
        @param data_label: for steer: 'roll_joint.position' for drive: 'pitch_joint.position'
        @param individual_traces: set to true to plot averaged data along with average
    '''
    csvs = get_csv_files(log_directory)
    for file in csvs:
        data = pd.read_csv(file)
        data['timestamp'] = (data['timestamp'].values - data['timestamp'].values[0])*1e-9
        if individual_traces:
            data.plot(x='timestamp', y=['roll_joint.position'], ax=ax)
    out_pend = plot_and_export_average_with_std(ax, csvs, time_column='timestamp', value_column=data_label, label="Average Robot Data")
    first_time = out_pend["time"][0]
    exp_time = out_pend["time"]
    exp_data = out_pend["mean"]
    return out_pend["ax"], first_time, exp_time, exp_data

    

def run_test(meshcat, starting_angle, friction_model_class, friction_params, stoptime=2):
   
    builder = DiagramBuilder()
    sceneConfig = SceneGraphConfig()
    sceneConfig.default_proximity_properties.compliance_type = "compliant"
    plant, scene_graph = AddMultibodyPlant(
        MultibodyPlantConfig(
            time_step=0.01,
            penetration_allowance=0.01,
            contact_surface_representation="polygon",
            contact_model="hydroelastic"
            ), sceneConfig, 
        builder)

    # plant = add_plate(plant, 0.0, visible=True)

    plant, model_idx = add_RoboBall_plant(plant, 
                                          place_in_stand="hanging")
    
    steer_q_idx = plant.GetStateNames().index("RoboBall_URDF_steer_q")
    steer_w_idx = plant.GetStateNames().index("RoboBall_URDF_steer_w")
    drive_q_idx = plant.GetStateNames().index("RoboBall_URDF_drive_q")
    drive_w_idx = plant.GetStateNames().index("RoboBall_URDF_drive_w")

    drive_motor_idx = plant.GetActuatorNames().index("RoboBall_URDF_drive")
    steer_motor_idx = plant.GetActuatorNames().index("RoboBall_URDF_steer")
    
    drive_friction = builder.AddSystem(friction_model_class(friction_params))
    steer_friction = builder.AddSystem(friction_model_class(friction_params))

    if meshcat != None:
        AddDefaultVisualization(builder, meshcat)

    state_demuxer = builder.AddSystem(Demultiplexer(plant.num_multibody_states()))
    control_muxer = builder.AddSystem(Multiplexer(2))
    
    # demux the states
    builder.Connect(plant.get_state_output_port(),
                    state_demuxer.get_input_port())
    
    builder.Connect(state_demuxer.get_output_port(steer_w_idx),
                    steer_friction.velocity_input_port)
    builder.Connect(state_demuxer.get_output_port(drive_w_idx),
                    drive_friction.velocity_input_port)
    # mux the forces
    builder.Connect(steer_friction.torque_output_port, control_muxer.get_input_port(steer_motor_idx))
    builder.Connect(drive_friction.torque_output_port, control_muxer.get_input_port(drive_motor_idx))
    
    builder.Connect(control_muxer.get_output_port(), plant.get_actuation_input_port())

    logger = LogVectorOutput(plant.get_state_output_port(), builder)
    diagram = builder.Build()
    
    diagram_context = diagram.CreateDefaultContext()
    plant_context = diagram.GetMutableSubsystemContext(plant, diagram_context)

    plant.SetPositions(plant_context, [0, starting_angle])
    
    simulator = simulator = Simulator(diagram, diagram_context)
    if meshcat !=None:
        meshcat.StartRecording()
    simulator.AdvanceTo(stoptime)
    if meshcat !=None:
        meshcat.PublishRecording()
    
    # plot_logger_data(logger, simulator, plant.GetStateNames())
    log = logger.FindLog(simulator.get_context())
    times = log.sample_times()
    data = log.data().transpose()
    return times, data[:,steer_q_idx]

if __name__=="__main__":

    steer_log_red = "roboball_plant/data/stiction_data/red_pitch/trimmed_output_steer"
    drive_log_red = "roboball_plant/data/stiction_data/red_pitch/trimmed_output_drive"
    
    # import to run visualizer
    meshcat = None
      
    # tune the steer model
    print(f"tuning steer friction from {steer_log_red}")
    fig, ax = plt.subplots()
    ax, time_offset, exp_time, exp_data = plot_test_data(ax, steer_log_red, "roll_joint.position")
    starting_angle = exp_data[0]
    end_time = exp_time[-1]

    print("\n When  prompted for optimizer, selecting no will load the last known best values\n")
    optimizer_bool_steer = input('Do you want to run the optimizer for steer stiction params (Answer with yes or no): ')

    if optimizer_bool_steer == 'Yes' or optimizer_bool_steer == 'yes':
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=150)

        # Extract best params
        best_params = study.best_params
        majd_stiction_params = [
            best_params['f_w'], 
            best_params['f_c'], 
            best_params['sigma'], 
            best_params['w_c'], 
            best_params['n']
        ]
        pass
    elif optimizer_bool_steer == 'No' or optimizer_bool_steer == 'no':
        print('Skipping optimization for steer.')
        # Results with the above optimizer (increasing n trials may reduce error initially but dynamics near the end become squished and unrealistic)
        best_params = {
            'f_w': 0.4157033347496656,
            'f_c': 0.10216601045708795,
            'sigma': 2.8153567767730086,
            'w_c': 0.38655082358510107,
            'n': 3.169269072267443
        }
    else:
        print('Invalid response, skipping optimization.')
        # Results with the above optimizer (increasing n trials may reduce error initially but dynamics near the end become squished and unrealistic)
        best_params = {
            'f_w': 0.4157033347496656,
            'f_c': 0.10216601045708795,
            'sigma': 2.8153567767730086,
            'w_c': 0.38655082358510107,
            'n': 3.169269072267443
        }

    majd_stiction_params = list(best_params.values())
    times_maj, data_maj = run_test(meshcat, starting_angle, StictionModel_Majd, majd_stiction_params, stoptime=end_time)
    ax.plot(times_maj + time_offset, data_maj, label="Majd et al.", color='red')

    ax.legend()
    ax.grid()
    ax.set_title("Robot Data vs Friction Models on Roll Joint")
    ax.set_xlabel("time(s)")
    ax.set_ylabel("Angle (rad)")

    # tune the drive model
    
    print(f"tuning drive friction from {drive_log_red}")
    fig, ax = plt.subplots()
    ax, time_offset, exp_time, exp_data = plot_test_data(ax, drive_log_red, "pitch_joint.position")
    starting_angle = exp_data[0]
    end_time = exp_time[-1]

    optimizer_bool_drive = input('Do you want to run the optimizer for drive stiction params (Answer with yes or no): ')

    if optimizer_bool_drive == 'yes' or optimizer_bool_drive == 'Yes':  
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=200)

        best_params = study.best_params
        majd_stiction_params = [
            best_params['f_w'], 
            best_params['f_c'], 
            best_params['sigma'], 
            best_params['w_c'], 
            best_params['n']
        ]
        pass
    elif optimizer_bool_drive == 'No' or optimizer_bool_drive == 'no':
        print('Skipping optimization for steer.')
        # Results with the above optimizer (increasing n trials may reduce error initially but dynamics near the end become squished and unrealistic)
        best_params = {
            'f_w': 1.776029713644168,
            'f_c': 1.2442621688382323,
            'sigma': 8.3285614144389655,
            'w_c': 1.35830578531488,
            'n': 1.599423615230998
        }
    else:
        print('Invalid response, skipping optimization.')
        # Results with the above optimizer (increasing n trials may reduce error initially but dynamics near the end become squished and unrealistic)
        best_params = {
            'f_w': 1.776029713644168,
            'f_c': 1.2442621688382323,
            'sigma': 8.3285614144389655,
            'w_c': 1.35830578531488,
            'n': 1.599423615230998
        }

    majd_stiction_params = list(best_params.values())

    times_maj, data_maj = run_test(meshcat, starting_angle, StictionModel_Majd, majd_stiction_params, stoptime=end_time)
    ax.plot(times_maj + time_offset, data_maj, label="Majd et al.", color='red')

    ax.legend()
    ax.grid()
    ax.set_title("Robot Data vs Friction Models on Pitch Joint")
    ax.set_xlabel("time(s)")
    ax.set_ylabel("Angle (rad)")
    # zoom_factory(ax)
    # panhandler(fig)

    plt.show()

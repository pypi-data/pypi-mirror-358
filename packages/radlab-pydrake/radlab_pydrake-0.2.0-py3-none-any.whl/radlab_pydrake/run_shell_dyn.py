from pydrake.systems.framework import DiagramBuilder
from pydrake.systems.analysis import Simulator

from pydrake.multibody.plant import (AddMultibodyPlant, MultibodyPlantConfig)
from pydrake.geometry import SceneGraphConfig, StartMeshcat

from rad_lab_roboball_pydrake.utilities.world_features import add_plate
from rad_lab_roboball_pydrake.roboball_plant.create_ball_plant import (
    add_RoboBall_shell,
    update_bedliner_properties
)


from pydrake.all import AddDefaultVisualization, LogVectorOutput, Quaternion
from pydrake.math import RollPitchYaw
from numpy import deg2rad, hstack
import numpy as np
import pandas as pd

meshcat = StartMeshcat()

def run_drake_shell_dyn(w0, tf, configs=(None,), new_props=None):
    """
        a digital twin experiment of the shell rolling outside the ric on the appron. with only the IMU attached 
        to a hubcap

        configs are ("soft", "angled_ground")
    """
    print(f"Running drake shell tests with configs {configs}")
    builder = DiagramBuilder()

    if "soft" in configs:
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
    else:
        plant, scene_graph = AddMultibodyPlant(
            MultibodyPlantConfig(
                time_step=0.001,
                contact_model="point"
                ), 
            builder)
    
    if "angled_ground" in configs:
        plant = add_plate(plant, 1, visible=True, plate_length=1000, plate_width=1000)

    else:
        plant = add_plate(plant, 0, visible=True, plate_length=1000, plate_width=1000)

    if "lumpy" in configs:
        plant, _ = add_RoboBall_shell(plant)
    else:
        plant, model_idx = add_RoboBall_shell(plant)

    logger = LogVectorOutput(plant.get_state_output_port(), builder)

    if meshcat:
        AddDefaultVisualization(builder, meshcat)

    diagram = builder.Build()

    # reset the bedliner properties
    if new_props:
        update_bedliner_properties(scene_graph, new_props)

    # define initial conditions
    q = RollPitchYaw(deg2rad([0, 0,0])).ToQuaternion()
    q0= [q.w(), q.x(), q.y(), q.z(), 0, 0, 0.305]
    R = 0.305
    v0 = [w0[0],w0[1], w0[2], w0[1]*R, -R*w0[0], 0]
    
    IC_context = diagram.CreateDefaultContext()
    robot_context = diagram.GetMutableSubsystemContext(plant, IC_context)
    plant.SetPositionsAndVelocities(robot_context, hstack((q0, v0)))    

    simulator = Simulator(diagram, IC_context)

    if meshcat:
        meshcat.StartRecording()
        simulator.set_target_realtime_rate(1)
    simulator.AdvanceTo(tf)
    if meshcat:
        meshcat.PublishRecording()

    log = logger.FindLog(simulator.get_context())

    names = plant.GetStateNames()
    wx_idx = names.index("RoboBall_URDF_pipe_assembly_wx")
    wy_idx = names.index("RoboBall_URDF_pipe_assembly_wy")
    wz_idx = names.index("RoboBall_URDF_pipe_assembly_wz")

    qw_idx = names.index("RoboBall_URDF_pipe_assembly_qw")
    qx_idx = names.index("RoboBall_URDF_pipe_assembly_qx")
    qy_idx = names.index("RoboBall_URDF_pipe_assembly_qy")
    qz_idx = names.index("RoboBall_URDF_pipe_assembly_qz")

    data = log.data().transpose()
    times = log.sample_times()

    wx_b = np.zeros_like(data[:, wx_idx])
    wy_b = np.zeros_like(data[:, wy_idx])
    wz_b = np.zeros_like(data[:, wz_idx])
    # convert global velocities to body velocities
    w_b = np.array([0, 0, 0])
    for i in range(len(data[:, wx_idx])):
        
        w_b[0] = data[i, wx_idx]
        w_b[1] = data[i, wy_idx]
        w_b[2] = data[i, wz_idx]
        # pull orientation q of pipe in world, q_PW
        q_b_norm = np.array([data[i, qw_idx],
                            data[i, qx_idx],
                            data[i, qy_idx],
                            data[i, qz_idx]])
        q_b_norm = q_b_norm / np.linalg.norm(q_b_norm)
        
        q_b = Quaternion(q_b_norm)
        q_b = q_b.rotation()
        
        # Rotate angular velocity into the body frame w_WP
        w_b = q_b.transpose()@w_b

        wx_b[i] = w_b[0]
        wy_b[i] = w_b[1]
        wz_b[i] = w_b[2]

    # assemble dataframe
    data_pd = pd.DataFrame({'timestamp':times,
                            'wx':wx_b,
                            'wy':wy_b,
                            'wz':wz_b,
                            'qw':data[:, qw_idx],
                            'qx':data[:, qx_idx],
                            'qy':data[:, qy_idx],
                            'qz':data[:, qz_idx]})

    return data_pd


if __name__=="__main__":
    import matplotlib.pyplot as plt
    # print(run_constrained_classical_exp([0, 5, 0], 20))
    # print(run_drake_shell_dyn())
    data = run_drake_shell_dyn([0.0, 0, 0], 30, ("soft", "angled_ground"), [1.2e5, 0.6])
    data1 = run_drake_shell_dyn([0.0, 0, 0], 30, ("point", "angled_ground"), [1.2e5, 0.6])
    data2 = run_drake_shell_dyn([1, 5, 0], 30, ("soft", ), [1.2e5, 0.6])
    data3 = run_drake_shell_dyn([1, 5, 0], 30, ("point",), [1.2e5, 0.6])

    fig, ax = plt.subplots()

    data.plot(x='timestamp', y=['wx', 'wy', 'wz'],  ax=ax)
    data1.plot(x='timestamp', y=['wx', 'wy', 'wz'], ax=ax)
    data2.plot(x='timestamp', y=['wx', 'wy', 'wz'], ax=ax)
    data3.plot(x='timestamp', y=['wx', 'wy', 'wz'], ax=ax)

    plt.show()
import numpy as np
from scipy.interpolate import interp1d
from run_compare_steer_models import plot_drake_model
from roboball_plant.data.plot_these_files import add_avg_data_to_plot
import matplotlib.pyplot as plt
import optuna

fig, ax = plt.subplots(2, 1)

if __name__=="__main__":

    directory = "/home/mjooevermann/repositories/rad_lab_roboball_pydrake/roboball_plant/data/steering_data/init_RAL_draft_data/trimmed_output"
    
    ax_return, pipe_data, pend_data = add_avg_data_to_plot(ax, directory)

    y_data = pipe_data["mean"]
    t_data = pipe_data["time"]
    q0 = [pipe_data["mean"][0], 0, pend_data["mean"][0], 0 ]

    tf = pipe_data["time"][-1] 
    t = np.linspace(0, tf, 100)

    def simulate_model(params):
        ax, data = plot_drake_model(None, q0, tf, 0, config=("soft", "stiction"), new_proximity=params)
        return data["time"], data["pipe"]

    # Exponential weight on early data points
    def weight_function(t, tau):
        return np.exp(-t / tau)

    def loss_function(params, tau):
        t_model, y_model = simulate_model(params)
        interp_model = interp1d(t_model, y_model, bounds_error=False, fill_value="extrapolate")
        y_model_interp = interp_model(t_data)
        weights = weight_function(t_data, tau)
        weights /= np.sum(weights)
        error = y_model_interp - y_data
        weighted_mse = np.sum(weights * error**2)
        return weighted_mse

    def objective(trial):
        p1 = trial.suggest_uniform('param1', 0.7e5, 2.5e5)
        p2 = trial.suggest_uniform('param2', 0.2, 0.7)
        tau = trial.suggest_uniform('tau', 0.5, 5.0)
        return loss_function([p1, p2], tau)

    study = optuna.create_study()
    study.optimize(objective, n_trials=70, n_jobs=12)  # <-- Parallelized

    print("Optimized parameters:", study.best_params)
    print("Final loss:", study.best_value)

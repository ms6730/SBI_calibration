# ------------------------------------------------------
# Import Librairies
# ------------------------------------------------------
import os
import pickle
import numpy as np
import pandas as pd
import torch
import json
import random
import matplotlib.pyplot as plt
import scipy.stats
from sbi.inference import SNPE
from pf_ens_functions import get_parflow_output_nc
import subsettools

# ----------------------------------------------------------------------------------------------------------------
# Training includes: Mean of Streamflow, Standard deviation of Streamflow, and streamflow for full the time series 
# ----------------------------------------------------------------------------------------------------------------
def extract_summary_stats_and_series(df):
    q = df.values.flatten()

    # Summary statistics
    mean_q = np.mean(q)
    std_q = np.std(q)

    # Combine mean, std, and raw streamflow values into a single feature vector
    feature_vector = np.concatenate(([mean_q, std_q], q))

    return torch.tensor(feature_vector, dtype=torch.float)

# ----------------------------------------------------------
# Load Settings
# ----------------------------------------------------------
json_path = '/home/ms6730/gage_1_shrinked_hundred/gage1_prior_shrinked/gage1_mcmc/mannning_prior_adjudted/hydrogen-sbi/scripts/settings.json'
with open(json_path, 'r') as file:
    settings = json.load(file)

base_dir = settings['base_dir']
grid = settings['grid']
huc = settings['huc']
temporal_resolution = settings['temporal_resolution']
runname = settings['runname']
variable_list = settings['variable_list']
num_sims = settings['num_sims']
ens_num = settings['ens_num']
num_samples = settings['num_samples']
quantile = settings['quantile']
obsv_path = settings['observation_path']
seed = settings['random_seed']
metadata_path = f'{base_dir}/output/{runname}/streamflow_daily_metadf.csv'

# --------------------------------------------------------------
# Set Seeds
# --------------------------------------------------------------
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

# ---------------------------------------------------------------
# Define Domain
# ---------------------------------------------------------------
_, mask = subsettools.define_huc_domain([huc], grid)

# ---------------------------------------------------------------
# Extract Simulation Outputs
# ---------------------------------------------------------------
for sim in range(num_sims):
    output_dir = f"{base_dir}/output/{runname}_{ens_num}_{sim}"
    nc_path = f"{output_dir}/{runname}_{sim-1}.nc"
    write_path = f"{output_dir}/{variable_list[0]}_{temporal_resolution}_pfsim.csv"
    for var in variable_list:
        get_parflow_output_nc(nc_path, metadata_path, var, write_path)

# ------------------------------------------------------------------
# Load Prior or Initialize Inference
# ------------------------------------------------------------------
try:
    with open(f"{base_dir}/{runname}_inference.pkl", "rb") as fp:
        inference = pickle.load(fp)
except FileNotFoundError:
    with open(f"{base_dir}/{runname}_prior.pkl", "rb") as fp:
        prior = pickle.load(fp)
    inference = SNPE(prior=prior)

# -------------------------------------------------------------------
# Load Parameter Samples (Manning’s)
# -------------------------------------------------------------------
theta_df = pd.read_csv(f"{base_dir}/{runname}_mannings_ens{ens_num}.csv")
theta_df = theta_df.rename(columns={'noise_param': 'noise_manning'})
theta_sim = torch.tensor(theta_df.values, dtype=torch.float)
noise_manning = torch.tensor(theta_df['noise_manning'].values, dtype=torch.float)

# ------------------------------------------------------------------
# Simulated and Observed Streamflow
# ------------------------------------------------------------------
gage_id = "01608500"
sim_data = []

for i in range(num_sims):
    sim_df = pd.read_csv(f'{base_dir}/output/{runname}_{ens_num}_{i}/streamflow_daily_pfsim.csv').drop('date', axis=1)[5:]

    if gage_id not in sim_df.columns:
        raise ValueError(f"Gage ID {gage_id} not found in simulated data.")

    # Load observation 
    if i == 0:
        obsv_df = pd.read_csv(obsv_path).drop('date', axis=1)[5:-1]
        if gage_id not in obsv_df.columns:
            raise ValueError(f"Gage ID {gage_id} not found in observed data.")
        summary_obs = extract_summary_stats_and_series(obsv_df[[gage_id]])
        x_obs = summary_obs.unsqueeze(0)

    # Simulated streamflow with added noise
    q_sim = sim_df[gage_id].values
    q_sim += np.random.randn(*q_sim.shape) * (q_sim * noise_manning[i].item())
    q_sim_df = pd.DataFrame(q_sim, columns=[gage_id])

    # Extract both streamflow and summary stats (raw streamflow)
    features_sim = extract_summary_stats_and_series(q_sim_df)
    sim_data.append(features_sim)

x_sim = torch.stack(sim_data)

# -----------------------------------------------------------------------------
# Train Posterior
# -----------------------------------------------------------------------------
_ = inference.append_simulations(theta_sim, x_sim).train(force_first_round_loss=True)
posterior = inference.build_posterior().set_default_x(x_obs)

# -----------------------------------------------------------------------------
# Plot Posterior Distributions
# -----------------------------------------------------------------------------
plots_dir = f'{base_dir}/plots'
os.makedirs(plots_dir, exist_ok=True)
samples = posterior.sample((1000,))
num_params = theta_df.shape[1]

for i in range(num_params):
    plt.figure(figsize=(8, 6))
    plt.hist(samples[:, i].numpy(), bins=30, density=True, alpha=0.6)
    plt.title(f'Density Plot for Parameter {i}')
    plt.xlabel(f'Parameter {i}')
    plt.ylabel('Density')
    plt.savefig(f'{plots_dir}/param{i}_posterior_density_ens{ens_num}.png', dpi=300)
    plt.close()

# -----------------------------------------------------------------------------
# Save Posterior and Inference Objects
# -----------------------------------------------------------------------------
with open(f"{base_dir}/{runname}_inference_{ens_num}.pkl", "wb") as fp:
    pickle.dump(inference, fp)
with open(f"{base_dir}/{runname}_posterior_{ens_num}.pkl", "wb") as fp:
    pickle.dump(posterior, fp)

# -----------------------------------------------------------------------------
# Update Ensemble Number
# -----------------------------------------------------------------------------
settings['ens_num'] = ens_num + 1
with open(json_path, 'w') as file:
    json.dump(settings, file, indent=4)

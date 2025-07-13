# -----------------------------------------------------------------------------
# Import The Libraries
# -----------------------------------------------------------------------------
import os
import pickle
import numpy as np
import pandas as pd
import subsettools
from sbi.inference import SNPE
from pf_ens_functions import get_parflow_output_nc
import torch
import json
import random
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# Load Settings from JSON File
# -----------------------------------------------------------------------------
json_path = '/home/ms6730/gage_1_shrinked_hundred/gage1_prior_shrinked/gage1_mcmc/mannning_prior_adjudted/hydrogen-sbi/scripts/settings.json'
with open(json_path, 'r') as file:
    settings = json.load(file)

# -----------------------------------------------------------------------------
# Extract variables from settings
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Set the seed
# -----------------------------------------------------------------------------
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

# -----------------------------------------------------------------------------
# Define the domain
# -----------------------------------------------------------------------------
_, mask = subsettools.define_huc_domain([huc], grid)

# -----------------------------------------------------------------------------
# Evaluate simulations
# -----------------------------------------------------------------------------
for sim in range(num_sims):
    output_dir = f"{base_dir}/output/{runname}_{ens_num}_{sim}"
    nc_path = f"{output_dir}/{runname}_{sim-1}.nc"
    write_path = f"{output_dir}/{variable_list[0]}_{temporal_resolution}_pfsim.csv"
    for var in variable_list:
        get_parflow_output_nc(nc_path, metadata_path, var, write_path)

# -----------------------------------------------------------------------------
# Load prior or inference
# -----------------------------------------------------------------------------
try:
    with open(f"{base_dir}/{runname}_inference.pkl", "rb") as fp:
        inference = pickle.load(fp)
except FileNotFoundError:
    with open(f"{base_dir}/{runname}_prior.pkl", "rb") as fp:
        prior = pickle.load(fp)
        print("Prior object:", prior)
    inference = SNPE(prior=prior)

# -----------------------------------------------------------------------------
# Load Manning's parameters (and noise)
# -----------------------------------------------------------------------------
theta_df_manning = pd.read_csv(f"{base_dir}/{runname}_mannings_ens{ens_num}.csv")
theta_df_manning = theta_df_manning.rename(columns={'noise_param': 'noise_manning'})
theta_df = theta_df_manning
print("[DEBUG] Final theta_df shape:", theta_df.shape)

noise_manning = torch.tensor(theta_df_manning['noise_manning'].values, dtype=torch.float)

if theta_df.shape[1] != prior.batch_shape[0]:
    print("\n[ERROR] Dimensional mismatch!")
    raise ValueError("Mismatch between prior and theta dimensions")

theta_sim = torch.tensor(theta_df.values, dtype=torch.float)

# -----------------------------------------------------------------------------
# Add noise to Simulated Streamflow for gage_id 01608500 only
# -----------------------------------------------------------------------------
gage_id = "01608500"
sim_data = []

for i in range(num_sims):
    sim_df = pd.read_csv(f'{base_dir}/output/{runname}_{ens_num}_{i}/streamflow_daily_pfsim.csv')
    sim_df = sim_df.drop(columns=['date'], errors='ignore')[5:]

    if gage_id not in sim_df.columns:
        raise ValueError(f"Gage ID {gage_id} not found in simulated data columns.")

    sim_series = sim_df[gage_id].astype(float).values
    sim_tensor = torch.tensor(sim_series, dtype=torch.float)
    sim_tensor += torch.randn(sim_tensor.shape) * (sim_tensor * noise_manning[i])
    sim_data.append(sim_tensor)

obsv_df = pd.read_csv(obsv_path).drop(columns=['date'], errors='ignore')[5:-1]
if gage_id not in obsv_df.columns:
    raise ValueError(f"Gage ID {gage_id} not found in observed data columns.")

obs_series = obsv_df[gage_id].astype(float).values
x_obs = torch.tensor(obs_series, dtype=torch.float).unsqueeze(0)
x_sim = torch.stack(sim_data)

# -----------------------------------------------------------------------------
# Debugging
# -----------------------------------------------------------------------------
print(f"[DEBUG] x_sim shape: {x_sim.shape}")
print(f"[DEBUG] theta_sim shape: {theta_sim.shape}")
print(f"[DEBUG] x_obs shape: {x_obs.shape}")

# -----------------------------------------------------------------------------
# Train posterior
# -----------------------------------------------------------------------------
_ = inference.append_simulations(theta_sim, x_sim).train(force_first_round_loss=True)
posterior = inference.build_posterior().set_default_x(x_obs)

#sample_with='mcmc'

# -----------------------------------------------------------------------------
# Plotting posterior densities
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
# Save posterior & inference
# -----------------------------------------------------------------------------
with open(f"{base_dir}/{runname}_inference_{ens_num}.pkl", "wb") as fp:
    pickle.dump(inference, fp)
with open(f"{base_dir}/{runname}_posterior_{ens_num}.pkl", "wb") as fp:
    pickle.dump(posterior, fp)

# -----------------------------------------------------------------------------
# Update ens_num in settings file
# -----------------------------------------------------------------------------
settings['ens_num'] = ens_num + 1
with open(json_path, 'w') as file:
    json.dump(settings, file, indent=4)


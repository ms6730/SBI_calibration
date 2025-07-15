## Description

**A second round of training** was conducted to assess whether model performance could be improved, given that **the first round successfully calibrated the Manning’s values,** resulting in a good match between the **simulated streamflow** and the **observed streamflow from USGS**. Moreover, a **second-round** is performed to evaluate whether the **most probable Manning's values** still fell outside the initially defined **prior range**, as indicated by heavy skewness in the posterior. The **SNPE model** was trained using the same **100 realizations** as in the first round. 


## Results:

### Hydrograph Plots:
The **hydrograph** shows that **both rounds** were able to match the **simulated streamflow** to the **observed streamflow** from **USGS**.

![Hydrograph Plot](hydrograph_plots/hydrograph_training_100_realizations_first_round_second_01608500.png)

However, the **first round** yielded a **closer match** to the **observed streamflow** from **USGS**. This suggests that the **initial training** already captured the pattern of the streamflow. 

### Posterior Distribution

![Density Plot for M0](posterior_distribution_training_100_realizations/Density_Plot_for_M0.png)
![Density Plot for M1](posterior_distribution_training_100_realizations/Density_Plot_for_M1.png)
![Density Plot for M2](posterior_distribution_training_100_realizations/Density_Plot_for_M2.png)
![Density Plot for M3](posterior_distribution_training_100_realizations/Density_Plot_for_M3.png)
![Density Plot for M4](posterior_distribution_training_100_realizations/Density_Plot_for_M4.png)
![Density Plot for M5](posterior_distribution_training_100_realizations/Density_Plot_for_M5.png)
![Density Plot for M6](posterior_distribution_training_100_realizations/Density_Plot_for_M6.png)
![Density Plot for M7](posterior_distribution_training_100_realizations/Density_Plot_for_M7.png)
![Density Plot for M8](posterior_distribution_training_100_realizations/Density_Plot_for_M8.png)


## Analysis of the Hydrograph

In the **first round**, we used a **wide prior** for Manning's values. This allowed the surrogate model **(SNPE)** to explore a broad parameter space, and learn how different **Manning's values** affect the entire streamflow. 

In the **second round**, the prior becomes very narrowed affecting the learning of the **SNPE**. By narrowing the prior too much, the **surrogate model** sees **less variation** in Manning's values. It can no longer learn how small changes affect the overall streamflow, especially peak flows. 


If the first round already learned the realtionship well, then it is not necessarily need a second round. The second round may be needed when we start with a **very wide prior** or **the model fails to learn**. Then, a **second round** is needed to **refine uncertainty gradually**. 


## Analysis of the Posterior Density Estimation 
The **results from the second round** reveal that the **posterior for M8** remains **heavily left-skewed**, suggesting that the prior for **M8** should be extended to better capture the parameter space. For **M4** and **M6**, the distributions are no longer heavily skewed, indicating that the selected priors were appropriate. 







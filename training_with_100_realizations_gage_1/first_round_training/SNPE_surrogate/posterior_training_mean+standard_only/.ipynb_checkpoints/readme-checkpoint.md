## Description 
The **surrogate model (SNPE)** was trained using **summary statitics** of the simulated streamflow only. The **hydrograph** shows a **good match** between the **simulated streamflow** ,obtained after training the **SNPE**, and the **observed streamflow** from USGS. Additionally, the **posterior distribution** obtained after the **first round of training** does not appear to be **heavily skewed** to the left or right, suggesting that the **selected prior range** of Manning's  is appropiate. 

## Hydrograph Plot 
![Hydrograph Plot](./hydrograph_training_mean+std_01608500.png)

## Posterior Distribution

![Density Plot for M0](./Density_Plot_for_M0.png)
![Density Plot for M1](./Density_Plot_for_M1.png)
![Density Plot for M2](./Density_Plot_for_M2.png)
![Density Plot for M3](./Density_Plot_for_M3.png)
![Density Plot for M4](./Density_Plot_for_M4.png)
![Density Plot for M5](./Density_Plot_for_M5.png)
![Density Plot for M6](./Density_Plot_for_M6.png)
![Density Plot for M7](./Density_Plot_for_M7.png)
![Density Plot for M8](./Density_Plot_for_M8.png)


## Results

**Training with Summary Statistics only** is enough to capture the overall shape. There are likely many different Manning's values (uniquness problem) that produces the same streamflow shape. However, **to match the peak flows at a precise time with a precise magnitude, the model becomes much more sensitive**. It tries to find a much narrower range of Manning's values that give that fit resulting in **heavily left or right skewness**. 


## Conclusion 
Overall, **both can produce good streamflow match** but with different precisions. 

- **Summary statistics** enable the model to capture the overall streamflow pattern using a broad range of Manning’s values obtained from the posterior distribution.
- **Training on the full time series** requires highly specific parameter values, often narrowing the posterior and pushing the optimal Manning’s values beyond the initially selected prior range.
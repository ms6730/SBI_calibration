## Streamflow Calibration Analysis

### Objective
The objective of this analysis is to identify the **most effective training approach** for matching the **simulated streamflow** to the **observed streamflow from USGS**.

### Results
The results demonstrate that training the surrogate model (SNPE) using **summary statistics**,specifically the mean and standard deviation,of the simulated streamflow across 100 realizations successfully captured the relationship between **Manning's values** and **streamflow**.

However, when the model was trained on the **full time series of streamflow data**, it was better able to capture the **peak flows and their magnitudes**. In particular, the **first peak** was more accurately represented compared to training with summary statistics alone.

**Streamflow patterns** are depended on **Manning's values**. The **mean** and the **standard deviation** of streamflow across 100 realizations are therefore **strongly correlated** with **Manning's values**.  

By computing the mean and the standard deviationover 100 realizations, we are **reducing noise** and extracting only **robust** and **informative summary features** that reflect the **response** of the sreamflow.  

This **denoising** and **decreasing the dimensionality** of data helps the **surrogate model** focus on the general relationship, which leads to good calibration, even if it is not precise at peak (first peak specefically)
.

However, **learning on full streamflow data** performs better, it has access to more **detailed signal structure**, especially useful for **matching sharp peaks**. 


### Limitations of Summary Statistics 

**Peak Flows** ,which are often narrow, high intensity events can occur over just a **few time steps**. However, this problem will appear with a long time series which is not our case. 

When the surrogate model is trained on the **entire streamflow** time series, it is directly informed and exposed to:

- Temporal Patterns
- Timing of Peaks
- Rate of Rise and Fall
- Event to Event variability

This allows the model to learn detailed dynamic relationships between **Manning's values** and how they affect flow behavior across all points in time excluding the **extreme events**.



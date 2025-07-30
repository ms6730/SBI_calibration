import subsettools as st
import hf_hydrodata as hf
import matplotlib.pyplot as plt

ij_huc_bounds, mask = st.define_huc_domain(hucs=["02070001"], grid="conus2")
print(f"bounding box: {ij_huc_bounds}")

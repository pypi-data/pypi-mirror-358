import logging

import numpy as np

from pyRadPlan import (
    PhotonPlan,
    load_tg119,
    generate_stf,
    calc_dose_influence,
    fluence_optimization,
    plot_slice,
)

from pyRadPlan.optimization.objectives import SquaredDeviation, SquaredOverdosing, MeanDose

logging.basicConfig(level=logging.INFO)

# Load TG119 (provided within pyRadPlan)
ct, cst = load_tg119()

# Create a plan object
pln = PhotonPlan(machine="Generic")
num_of_beams = 5
pln.prop_stf = {
    "gantry_angles": np.linspace(0, 360, num_of_beams, endpoint=False),
    "couch_angles": np.zeros((num_of_beams,)),
}
# Generate Steering Geometry ("stf")
stf = generate_stf(ct, cst, pln)

# Calculate Dose Influence Matrix ("dij")
dij = calc_dose_influence(ct, cst, stf, pln)

# Optimize
cst.vois[1].objectives = [SquaredDeviation(priority=1000.0, d_ref=3.0)]  # Target
cst.vois[0].objectives = [SquaredOverdosing(priority=100.0, d_max=1.0)]  # OAR
cst.vois[2].objectives = [
    MeanDose(priority=1.0, d_ref=0.0),
    SquaredOverdosing(priority=10.0, d_max=2.0),
]  # BODY

fluence = fluence_optimization(ct, cst, stf, dij, pln)

# Result
result = dij.compute_result_ct_grid(fluence)

# Choose a slice to visualize
view_slice = int(np.round(ct.size[2] / 2))

# Visualize
plot_slice(
    ct=ct,
    cst=cst,
    overlay=result["physical_dose"],
    view_slice=view_slice,
    plane="axial",
    overlay_unit="Gy",
)

#!/usr/bin/python
# encoding: utf-8
# %% [markdown]
# # Example of a TiO2/SiO2 Bragg mirror with 8.5 periods
#
# Berreman4x4 example
# Author: O. Castany, M.Müller

# %%
import berreman4x4 as bm
import berreman4x4.plotter as bmplot
import matplotlib.pyplot as pyplot
import numpy as np

# %%
bm.settings['ExpmBackend'] = 'scipy'
np.set_printoptions(suppress=True, precision=3)

# %% [markdown]
# Front and back materials

# %%
air = bm.IsotropicMaterial(bm.DispersionLess(1.0))
glass = bm.IsotropicMaterial(bm.DispersionLess(1.5))

# %% [markdown]
# Materials for a SiO2/TiO2 Bragg mirror

# %%
n_SiO2 = 1.47
n_TiO2 = 2.23 + 1j * 5.2e-4

SiO2 = bm.IsotropicMaterial(bm.DispersionLess(n_SiO2))
TiO2 = bm.IsotropicMaterial(bm.DispersionLess(n_TiO2))

# %% [markdown]
# Calculate layer thickness as quarterwaveplates

# %%
lbda0 = 1550

d_SiO2 = bm.get_QWP_thickness(SiO2, lbda0)
d_TiO2 = bm.get_QWP_thickness(TiO2, lbda0)

print("Thickness of the SiO2 QWP: {} nm".format(d_SiO2))
print("Thickness of the TiO2 QWP: {} nm".format(d_TiO2))

# %% [markdown]
# Create layers

# %%
L_SiO2 = bm.Layer(SiO2, d_SiO2)
L_TiO2 = bm.Layer(TiO2, d_TiO2)

# Repeated layers: 8.5 periods
Layerstack = bm.RepeatedLayers([L_TiO2, L_SiO2], 8, 0, 1)

# %% [markdown]
# Structure

# %%
s = bm.Structure(air, [Layerstack], glass)

# %% [markdown]
# Calculation

# %%
(lbda1, lbda2) = (1100, 2500)
lbda_list = np.linspace(lbda1, lbda2, 200)

data = s.evaluate(lbda_list, 0)

R = data.R[:, 1, 1]
T = data.T[:, 1, 1]

# %% [markdown]
# Plotting

# %%
fig = pyplot.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(lbda_list, R, label="$R$")
ax.plot(lbda_list, T, label="$T$")
ax.legend(loc='center right')
ax.set_xlabel(r"Wavelength $\lambda$ (nm)")
ax.set_ylabel(r"Power reflection $R$ or transmission $T$")
ax.set_title(r"Bragg mirror: Air/{TiO$_2$/SiO$_2$}x8/TiO$_2$/Glass")
fmt = ax.xaxis.get_major_formatter()
fmt.set_powerlimits((-3, 3))
pyplot.show()

# %% [markdown]
# Structure Graph

# %%
bmplot.drawStructure(s)

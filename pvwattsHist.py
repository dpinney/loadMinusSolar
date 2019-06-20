''' Carve solar out of some meter time series data. '''
import nrelsam2013solo as nrelsam2013
from matplotlib import pyplot as plt
import platform
import matplotlib
import pandas as pd
if platform.system() == "Darwin":
	plt.switch_backend('MacOSX')
# Set up SAM data structures.
ssc = nrelsam2013.SSCAPI()
dat = ssc.ssc_data_create()
# Solar system specs.
ssc.ssc_data_set_string(dat, "file_name", "climate.tmy3.csv")
ssc.ssc_data_set_number(dat, "system_size", 5.0) #kW
ssc.ssc_data_set_number(dat, "derate", 0.77)
ssc.ssc_data_set_number(dat, "track_mode", 0.0) #1=1axis, 2=2axis, 3=azimuthAxis
ssc.ssc_data_set_number(dat, "azimuth", 180)
ssc.ssc_data_set_number(dat, "tilt_eq_lat", 1.0)
# ssc.ssc_data_set_number(dat, "tilt", manualTilt)
ssc.ssc_data_set_number(dat, "rotlim", 45.0)
ssc.ssc_data_set_number(dat, "gamma", 0.45)
ssc.ssc_data_set_number(dat, "inv_eff", 0.92)
ssc.ssc_data_set_number(dat, "w_stow", 0.0)
# Advanced solar specs that we could enable later.
# ssc.ssc_data_set_array(dat, 'shading_hourly', None) 	# Hourly beam shading factors
# ssc.ssc_data_set_number(dat, 'tilt', 999)
# Run PV system simulation.
mod = ssc.ssc_module_create("pvwattsv1")
ssc.ssc_module_exec(mod, dat)
# Geodata output.
outData = {}
outData["city"] = ssc.ssc_data_get_string(dat, "city")
outData["state"] = ssc.ssc_data_get_string(dat, "state")
outData["lat"] = ssc.ssc_data_get_number(dat, "lat")
outData["lon"] = ssc.ssc_data_get_number(dat, "lon")
outData["elev"] = ssc.ssc_data_get_number(dat, "elev")
# Weather output.
outData["climate"] = {}
outData["climate"]["Plane of Array Irradiance (W/m^2)"] = ssc.ssc_data_get_array(dat,"poa")
outData["climate"]["Beam Normal Irradiance (W/m^2)"] = ssc.ssc_data_get_array(dat,"dn")
outData["climate"]["Diffuse Irradiance (W/m^2)"] = ssc.ssc_data_get_array(dat,"df")
outData["climate"]["Ambient Temperature (F)"] = ssc.ssc_data_get_array(dat,"tamb")
outData["climate"]["Cell Temperature (F)"] = ssc.ssc_data_get_array(dat,"tcell")
outData["climate"]["Wind Speed (m/s)"] = ssc.ssc_data_get_array(dat,"wspd")
# Power generation.
outData["Consumption"] = {}
outData["Consumption"]["Power"] = ssc.ssc_data_get_array(dat,"ac")
# from pprint import pprint as pp
# pp(outData)
# Meter data
meters = pd.read_csv('meters.csv')
meterNames = list(meters.columns.values)
# Plot solar and meters and difference
f, axarr = plt.subplots(1 + len(meterNames), sharex=True)
axarr[0].set_title('Solar Output')
axarr[0].plot(outData["Consumption"]["Power"])
axarr[0].set_ylabel('Watts')
axarr[0].yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
alpha = 0.8
for i, name in enumerate(meterNames):
	meterMinusSolar = meters[name] - outData["Consumption"]["Power"]
	peakRed = round(100 * (1 - max(meterMinusSolar) / max(meters[name])), 2)
	minLoad = round(min(meterMinusSolar),0)
	title = 'Meter {}. Minimum load: {}; Peak Reduction: {}%'.format(name, minLoad, peakRed)
	axarr[1 + i].set_title(title)
	axarr[1 + i].plot(meters[name], label='load', alpha=alpha)
	axarr[1 + i].plot(meterMinusSolar, label='load minus solar', alpha=alpha)
	axarr[1 + i].set_ylabel('Watts')
	axarr[1 + i].legend()
	axarr[1 + i].yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
axarr[-1].set_xlabel('Hour of Year')
axarr[-1].set_xlim(xmin=0, xmax=8760)
plt.show()
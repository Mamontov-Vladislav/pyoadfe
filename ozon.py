import argparse
import datetime
import json
from scipy.io import netcdf
import numpy as np
import matplotlib.pyplot as plt
import os
os.system('pip3 install geopy')
from geopy.geocoders import Nominatim



parser = argparse.ArgumentParser()
parser.add_argument('data', nargs='*')



if __name__ == "__main__":
    args = parser.parse_args()
    if len(args.data) == 1:
        geolocator = Nominatim(user_agent="h")
        location = geolocator.geocode(args.data)
        lat = np.round(location.latitude, 1)
        lon = np.round(location.longitude, 1)
    else:
        lon = float(args.data[0])
        lat = float(args.data[1])


print(lon, lat)


with netcdf.netcdf_file("MSR-2.nc", mmap=False) as file:
    variables = file.variables
    index_lon = np.searchsorted(variables['longitude'].data, lon)
    index_lat = np.searchsorted(variables['latitude'].data, lat)
    a = np.asarray(variables['Average_O3_column'].data[:, index_lat, index_lon])
    time = np.asarray(variables['time'].data)
    time = time/12 + 1970

    out = {
  "coordinates": [lon, lat],
  "jan": {
    "min": float(variables['Average_O3_column'].data[:, index_lat, index_lon][::12].min()),
    "max": float(variables['Average_O3_column'].data[:, index_lat, index_lon][::12].max()),
    "mean": np.around(float(variables['Average_O3_column'].data[:, index_lat, index_lon][::12].mean()), 1)
  },
  "jul": {
    "min": float(variables['Average_O3_column'].data[:, index_lat, index_lon][6::12].min()),
    "max": float(variables['Average_O3_column'].data[:, index_lat, index_lon][6::12].max()),
    "mean": np.around(float(variables['Average_O3_column'].data[:, index_lat, index_lon][6::12].mean()), 1)
  },
  "all": {
    "min": float(variables['Average_O3_column'].data[:, index_lat, index_lon].min()),
    "max": float(variables['Average_O3_column'].data[:, index_lat, index_lon].max()),
    "mean": np.around(float(variables['Average_O3_column'].data[:, index_lat, index_lon].mean()), 1)
  }
} 
with open('ozon.json', 'w') as f:
    json.dump(out, f)

plt.figure(figsize=(12, 7.5))
plt.xticks(np.linspace(1980, 2020, 9))
plt.grid()
plt.plot(time, a, 'o-', ms = 3, lw = 1, label='Для всего интервала')
plt.plot(time[::12],a[::12], 'o-', ms = 3, lw = 2, label='Для Январей каждого года')
plt.plot(time[6::12], a[6::12], 'o-', ms = 3, lw = 2, label='Для Июлей каждого года')
plt.title("Статистика содержания озона в атмосфере для {} широты, {} долготы.".format(lat, lon))
plt.xlabel("Дата")
plt.ylabel("Содержание озона, единиц Добсона")
plt.legend()
plt.savefig('ozon.png')

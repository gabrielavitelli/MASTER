# razao de mistura : mixing ration : rwmr : GRIB_typeOfLevel: hybrid : GRIB_stepType:                            instant
# theta : temperatura potencial
#lat=25.559S

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from glob import glob
import cartopy, cartopy.crs as ccrs
import metpy.calc as mpcalc
from metpy.units import units
#######################################################################################################################################
# le o arquivo 
arquivo='/home/gabriela/treinamento/python/scripts/fig_dados/2024040100/gfs.2024040100.1p00.f024'

# abre os arquivos
ds = xr.open_dataset(arquivo, engine='cfgrib', filter_by_keys={'typeOfLevel': 'isobaricInhPa', 'stepType': 'instant'})#,'typeOfLevel': 'surface'})
ds_rm = xr.open_dataset(arquivo, engine='cfgrib', filter_by_keys={'stepType': 'instant','typeOfLevel': 'surface'})#,'typeOfLevel': 'surface'})

# recortando longitude
ds_recortado =ds.sel(latitude=-25.0, longitude=slice(270, 335))
ds_rm_recortado = ds_rm.sel(latitude=-25.0, longitude=slice(270, 335))

# pegando valores para plotagem 
longitude = ds['longitude'][25:91].values
pressao = ds['isobaricInhPa'].values

#######################################################################################################################################
# theta --> temperatura potencial # pt

p0 = 1000  
R = 287.05  
cp = 1005  
theta=[]
pressoes_desejadas = np.array([1000, 900, 800, 700, 600, 500, 400, 300, 200])
ds_interp = ds.interp(isobaricInhPa=pressoes_desejadas, method='linear')
theta = ds_interp['t'] * (p0 / ds_interp['isobaricInhPa']) ** (R / cp)

#######################################################################################################################################
# velocidade vertical # 

vel_vento = ds['w']/100
vel_media_lat = vel_vento.mean(dim=['longitude']).values
u_1000 = ds['u'].sel(isobaricInhPa=1000).mean(dim=['longitude'])
v_1000 = ds['v'].sel(isobaricInhPa=1000).mean(dim=['longitude'])

#######################################################################################################################################
# razao de mistura # 
rm=[]
#rm = mixing_ratio(25 * units.hPa, 1000 * units.hPa).to('g/kg')
# Calculando a razão de mistura diretamente de pressão de vapor
T = ds['t'].values
pressao_vapor=  6.1078 * 10 ** ( (17.269*T) / (237.3+T) )
#print (pressao_vapor)

pressao_total= ds_rm['sp'].values

razao_mistura = mpcalc.mixing_ratio(pressao_vapor * units.pascal, pressao_total * units.pascal)

# Convertendo para g/kg
#mixing_ratio_g_kg = mixing_ratio.to('g/kg')

#print(f"Razão de mistura: {mixing_ratio_g_kg:.2f}")

#######################################################################################################################################
# plotagem #

# ajusta a figura para ficar igual a do site do MASTER
lon = np.where((longitude >= -90) & (longitude <= -25))[0]
plon = np.where((pressao >= 200) & (pressao <= 1000))[0]  # Indices para pressão entre 200 e 1000 hPa

# cria a grade
Longitude, Pressao = np.meshgrid(longitude[lon], pressao[plon])  

plt.figure(figsize=(10, 6))

# plotar razao de mistura #
plt.plot(razao_mistura, zorder=1)

# plota theta
#theta_recortado = theta.sel(latitude=-25.0, longitude=slice(270, 335))
#contour = plt.contourf(theta_recortado['longitude'], theta_recortado['isobaricInhPa'], theta_recortado, levels=100, cmap='viridis')
#plt.colorbar(contour, label='Temperatura Potencial (K)')

plt.xlabel('longitude')
plt.ylabel('Pressão (hPa)')

plt.gca().invert_yaxis()  # Inverte o eixo y para pressão
plt.title('Perfil Vertical da razão de mistura')

plt.show()

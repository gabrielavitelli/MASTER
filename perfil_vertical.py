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
import datetime as dt
from datetime import date
#######################################################################################################################################
# le o arquivo 2024042300
data_original= date.today()
data=data_original.strftime(f"%Y%m%d")
arquivo=f'/home/gabriela/treinamento/operacao/fig_dados/{data}00/gfs.{data}00.1p00.f006'
#/home/gabriela/treinamento/python/scripts/fig_dados/2024040100/gfs.2024040100.1p00.f024'

# abre os arquivos
ds = xr.open_dataset(arquivo, engine='cfgrib', filter_by_keys={'typeOfLevel': 'isobaricInhPa', 'stepType': 'instant'})#,'typeOfLevel': 'surface'})

# recorta lat,lon,niveis atmosfericos
ds_recortado =ds.sel(latitude=-25.0, longitude=slice(270, 335), isobaricInhPa=slice(1000, 200))

#######################################################################################################################################
# theta --> temperatura potencial # pt

p0 = 1000  
R = 287.05  
cp = 1005  
theta=[]
#pressoes_desejadas = np.array([1000, 900, 800, 700, 600, 500, 400, 300, 200])
#ds_interp = ds.interp(isobaricInhPa=pressoes_desejadas, method='linear')
#theta = ds_recortado['t'] * (p0 / ds_interp['isobaricInhPa']) ** (R / cp)

theta = ds_recortado['t'] * (p0 / ds_recortado['isobaricInhPa']) ** (R / cp)

#print (theta)


#######################################################################################################################################
# velocidade vertical # 

vel_vento = ds['w']/100
vel_media_lat = vel_vento.mean(dim=['longitude']).values
u_1000 = ds['u'].sel(isobaricInhPa=1000).mean(dim=['longitude'])
v_1000 = ds['v'].sel(isobaricInhPa=1000).mean(dim=['longitude'])

#######################################################################################################################################
# razao de mistura # 

T = ds_recortado['t']-273.15 

# pressao de vapor de saturacao
pressao_vapor=  6.1078 * 10 ** ( (17.269*T) / (237.3+T) ) *100


ur=ds_recortado['r']/100

#pressa_vapor_real
pressao_vr=pressao_vapor * ur
#print (pressao_vr)

pressao_vr_pascal = pressao_vr * units('Pa')
#print (pressao_vr_pascal)

p_isobaric_pascal = ds_recortado['isobaricInhPa']*units('Pa')


print ('\n\n\n')
print ('temperatura')
print (T.values)
print ('---------')
print ('pressao de vapor de saturacao')
print (pressao_vapor.values)
print ('---------')
print ('pressao de vapor real')
print (pressao_vr_pascal)
print ('---------')
print ('umidade relativa')
print (ur.values)



# razao de mistura

w = ((pressao_vr_pascal * 0.622) / (p_isobaric_pascal - pressao_vr_pascal))
print ('---------')
print ('razao de mistura')
print (w.values)


plt.figure(figsize=(10, 6))
plt.plot(w.isobaricInhPa, w[:,0], label='Razão de Mistura (w)')  # Assumindo que 'time' é o índice temporal
plt.title('Série Temporal da Razão de Mistura em 25S 270° ')
plt.show()
print ("\n\n\n")
print (w.values)




#print ('-------pressao vapor real ----------')
#print (pressao_vr_pascal)

#print ('-------razao mistura ----------')
#print (w)


#######################################################################################################################################
# plotagem #


plt.figure(figsize=(10, 6))

# cria a grade
Longitude, Pressao = np.meshgrid(ds_recortado.longitude.values, ds_recortado.isobaricInhPa.values)  

contour = plt.contour(Longitude, Pressao, w, levels=1, colors='black') 
plt.clabel(contour, inline=True, fontsize=10, fmt='%1.1f')  # Labels on contour lines


contour = plt.contourf(theta.longitude, theta.isobaricInhPa, theta, cmap='viridis')
plt.colorbar(contour, label='Temperatura Potencial (K)')


plt.xlabel('longitude')
plt.ylabel('Pressão (hPa)')

plt.gca().invert_yaxis()  # Inverte o eixo y para pressão
plt.title(f'Perfil Vertical da razão de mistura para {data} as 00h 12z para -25W')

plt.show()
plt.quit()
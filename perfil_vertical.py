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
# Função para converter coordenadas

def converte_coordenada(dado):
    dado = dado.assign_coords(longitude=(((dado.longitude + 180) % 360) - 180))
    dado = dado.sortby('longitude')
    return dado.sortby('longitude')

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
theta = ds_recortado['t'] * (p0 / ds_recortado['isobaricInhPa']) ** (R / cp)

#print (theta)


#######################################################################################################################################
# velocidade vertical # 

vel_vento = ds['w']/100
vel_media_lat = vel_vento.mean(dim=['longitude']).values
u_1000 = ds['u'].sel(isobaricInhPa=1000).mean(dim=['longitude'])
v_1000 = ds['v'].sel(isobaricInhPa=1000).mean(dim=['longitude'])



#######################################################################################################################################
# vento #

# vento em 1000hPa
print (ds_recortado['u'][0,:])

u_1000 = ds_recortado['u'][0,:]
v_1000 = ds_recortado['v'][0,:]
#u_1000 = converte_coordenada(u_1000)
#v_1000 = converte_coordenada(v_1000)
print ('---------')
print ('vento em 1000hPa')
print (u_1000)

# 800hPa = 
print (ds_recortado['u'][6,:])
u_800 = ds_recortado['u'][6,:]
v_800 = ds_recortado['v'][6,:]


# 500hPa = 
print (ds_recortado['u'][12,:])
u_500 = ds_recortado['u'][12,:]
v_500 = ds_recortado['v'][12,:]


# 200hPa = 
print (ds_recortado['u'][18,:])
u_200 = ds_recortado['u'][18,:]
v_200 = ds_recortado['v'][18,:]


#######################################################################################################################################
# razao de mistura # 

T = ds_recortado['t']-273.15 

# pressao de vapor de saturacao
pressao_vapor=  6.1078 * 10 ** ( (17.67*T) / (243.5+T) ) *100


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
print (w)

longitude=w.longitude.values

#plt.figure(figsize=(10, 6))
#for lon in range(len(longitude)):
#    plt.plot(w.isobaricInhPa, w[:, lon], label='Razão de Mistura (w)')  


    # Plot a razão de mistura para esta longitude
#    ax.plot(subset.isobaricInhPa, subset['w'], label=f'Lon: {lon}°')

#plt.title('Série Temporal da Razão de Mistura em 25S 270° ')
#plt.show()
#print ("\n\n\n")
#print (w.values)




#print ('-------pressao vapor real ----------')
#print (pressao_vr_pascal)

print ('-------razao mistura ----------')
print (w)


#######################################################################################################################################
# plotagem #
#plt.figure()
fig, ax = plt.subplots()

# cria a grade
Longitude, Pressao = np.meshgrid(ds_recortado.longitude.values, ds_recortado.isobaricInhPa.values)  


#for lon in range(len(longitude)):
#    plt.plot(w.isobaricInhPa, w[:, lon], label='Razão de Mistura (w)')  

w_matrix = w.values
print (w_matrix)

# Define os níveis de contorno que você deseja plotar
levels = np.linspace(np.min(w_matrix), np.max(w_matrix), 35)  
contour = plt.contour(Longitude, Pressao, w, levels=levels, colors='black') 
plt.clabel(contour, inline=True, fontsize=10, fmt='%1.1f')  # Labels on contour lines

contour = plt.contourf(theta.longitude, theta.isobaricInhPa, theta, cmap='viridis')
plt.colorbar(contour, label='Temperatura Potencial (K)')

    # plotar vento
vento_1000 = ax.quiver(u_1000.longitude, u_1000.isobaricInhPa, u_1000, v_1000, color='black', width=0.0025, headwidth=5, zorder=4) #600 0.0015,
ax.quiverkey(vento_1000, 0.86, 0.057, 20, r"$20 \frac{m}{s}$", labelpos="E", coordinates="figure") # 20 #0.86, 0.057, 20

vento_800 = ax.quiver(u_800.longitude, u_800.isobaricInhPa, u_800, v_800, color='black', width=0.0025, headwidth=5, zorder=4) #600 0.0015,
ax.quiverkey(vento_800, 0.86, 0.057, 20, r"$20 \frac{m}{s}$", labelpos="E", coordinates="figure") # 20 #0.86, 0.057, 20

vento_500 = ax.quiver(u_500.longitude, u_500.isobaricInhPa, u_500, v_500, color='black', width=0.0025, headwidth=5, zorder=4) #600 0.0015,
ax.quiverkey(vento_500, 0.86, 0.057, 20, r"$20 \frac{m}{s}$", labelpos="E", coordinates="figure") # 20 #0.86, 0.057, 20

vento_200 = ax.quiver(u_200.longitude, u_200.isobaricInhPa, u_200, v_200, color='black', width=0.0025, headwidth=5, zorder=4) #600 0.0015,
ax.quiverkey(vento_200, 0.86, 0.057, 20, r"$20 \frac{m}{s}$", labelpos="E", coordinates="figure") # 20 #0.86, 0.057, 20


plt.xlabel('longitude')
plt.ylabel('Pressão (hPa)')

plt.gca().invert_yaxis()  # Inverte o eixo y para pressão
plt.title(f'Perfil Vertical da razão de mistura para {data} as 00h 12z para -25W')

plt.show()
quit()
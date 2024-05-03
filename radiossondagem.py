from siphon.simplewebservice.wyoming import WyomingUpperAir
from datetime import datetime
import xarray as xr
from metpy.units import units
import numpy as np
from metpy.plots import SkewT
import metpy.calc as mpcalc
import matplotlib.pyplot as plt
import scipy.signal
entrada = '/home/gabriela/treinamento/python/scripts/MASTER/gfs.t12z.pgrb2.1p00.f000'
ds = xr.open_dataset(entrada, engine='cfgrib', filter_by_keys={'typeOfLevel': 'isobaricInhPa'})

ds_ur = xr.open_dataset(entrada, engine='cfgrib', filter_by_keys={'typeOfLevel': 'sigma'})
print (ds)

# registrando unidades

# joao pessoa (-7.148333333333333, 34.95055555555556)
lat = -7.148333333333333
lon = 34.95055555555556
#ds.sel(latitude=lat, longitude=lon, method='nearest')
ds=ds.sel(latitude=lat, longitude=lon, method='nearest')
ds_ur=ds_ur.sel(latitude=lat, longitude=lon, method='nearest')

#########################################################################################################################
pressao = ds['gh'].values*units('hPa')
# Ordenando os dados de pressão em ordem decrescente
indices = np.argsort(-pressao)  # Obtem os índices para ordenar de forma decrescente
pressao = pressao[indices]

temp = ds['t']#.values*units('celsius')
ur = ds_ur['r'].values*units('%')
vento_u = ds['u'].values*units('m/s')
vento_v = ds['v'].values*units('m/s')

def calculate_dew_point(T, RH):
    b = 17.62
    c = 243.12
    gamma = (b * T / (c + T)) + np.log(RH / 100.0)
    dew_point = (c * gamma) / (b - gamma)
    return dew_point.values*units('celsius')

ponto_de_orvalho = calculate_dew_point(temp, ur)
print(f"Ponto de Orvalho: {ponto_de_orvalho} °C")

#temp = temp[:, indices]  
#ponto_de_orvalho = ponto_de_orvalho[:, indices] 


levels = np.arange(100, 1050, 50) * units('hPa') # mbar para as unidades de milibar

#########################################################################################################################

# Criando a figura com o diagrama Skew-T Log-P

fig = plt.figure(figsize = (9,9))

skew = SkewT(fig, rotation = 45)

# Temperaturas e barbelas do vento
skew.plot(pressao, temp, color = 'red')
skew.plot(pressao, ponto_de_orvalho, color = 'green')
print (f'-------{pressao}-------')
print ('\n')
print (f'-------{vento_u}-------')
print('\n')
print (f'-------{vento_v}-------')
skew.plot_barbs(pressao, vento_u, vento_v, flip_barb=True)


# Adicionando as curvas das adiabáticas e razão de mistura no Skew-T Log-P
skew.plot_dry_adiabats()
skew.plot_moist_adiabats()
skew.plot_mixing_lines()

pressao_filtrada = scipy.signal.medfilt(pressao, kernel_size=5) #*units('hPa')

#pressao_filtrada = units.Quantity(pressao_filtrada, "hPa")
# Calcular o perfil vertical da parcela de ar
perfil = mpcalc.parcel_profile(pressao, temp[0], ponto_de_orvalho[0]).to('degC')
skew.plot(pressao, perfil, color = 'black', linewidth = 2)

#temp = ds['t']#.values*units('celsius')
 # Adicionar o CAPE e o CIN
skew.shade_cin(pressao, temp*units('celsius'), perfil, ponto_de_orvalho)
skew.shade_cape(pressao, temp*units('celsius'), perfil)

skew.ax.axvline(0, color = 'cyan', linestyle = '--')
skew.ax.set_xlim(-30,40)

# --------------------------------------------------------------------------------------------
# ADICIONAR OS PARÂMETROS TERMODINÂMICOS

# Agregar parâmetros termodinâmicos
#ax3 = fig.add_subplot(gs[1, -1])
#ax3.axis('off')
'''
# coluna 1
ax3.text(0.1, 1.4,' ', size = 12)
ax3.text(0.1, 1.3,'Total Total Index', size = 12)
#ax3.text(0.1, 1.3,'Cross Total Index', size = 12)
ax3.text(0.1, 1.2,'Vertical Total Index', size = 12)
ax3.text(0.1, 1.1,'K Index', size = 12)
ax3.text(0.1, 1,'Nível do LCL', size = 12)
ax3.text(0.1, 0.9,'Temp. do LCL', size = 12)
ax3.text(0.1, 0.8,'Nível do LFC', size = 12)
ax3.text(0.1, 0.7,'Temp. do LFC', size = 12)
ax3.text(0.1, 0.6,'Equi. Level', size = 12)
ax3.text(0.1, 0.5,'SBCAPE', size = 12)
ax3.text(0.1, 0.4,'SBCIN', size = 12)
ax3.text(0.1, 0.3,'Água Precip.', size = 12)
ax3.text(0.1, 0.2,'Showalter Index', size = 12)
ax3.text(0.1, 0.1,'Lifted Index', size = 12)

# coluna 2
ax3.text(0.7, 1.3, '{:.2f} '.format(np.array(tt)), size = 12)
#ax3.text(0.7, 1.3, '{:.2f} '.format(np.array(ct)), size = 12)
ax3.text(0.7, 1.2, '{:.2f} '.format(np.array(vt)), size = 12)
ax3.text(0.7, 1.1, '{:.2f} '.format(np.array(k_index)), size = 12)
ax3.text(0.7, 1, '{:.2f} hPa'.format(np.array(lcl_pressure)), size = 12)
ax3.text(0.7, 0.9, '{:.2f} C'.format(np.array(lcl_temperature)), size = 12)
ax3.text(0.7, 0.8, '{:.2f} hPa'.format(np.array(lfc_pressure)), size = 12)
ax3.text(0.7, 0.7, '{:.2f} C'.format(np.array(lfc_temperature)), size = 12)
ax3.text(0.7, 0.6, '{:.2f} hPa'.format(np.array(el_pressure)), size = 12)
ax3.text(0.7, 0.5, '{:.2f} J/kg'.format(np.array(sbcape)), size = 12)
ax3.text(0.7, 0.4, '{:.2f} J/kg'.format(np.array(sbcin)), size = 12)
ax3.text(0.7, 0.3, '{:.2f} mm'.format(np.array(precipitable_water)), size = 12)
ax3.text(0.7, 0.2, '{:.2f}'.format(np.array(showalter)[0]), size = 12)
ax3.text(0.7, 0.1, '{:.2f}'.format(np.array(lifted)[0]), size = 12)
ax3.text(0.1, 0.01, 'Elaborado por: ' + f'{Autor}', size = 12)
'''

# Formatando os eixos e título
plt.xlabel(r'Temperature ($\degree$C)', fontsize = 14)
plt.ylabel(r'Pressure (hPa)', fontsize = 14)
plt.title(f'Gabriela Vitelli', fontsize = 10, loc = 'left')
plt.title(f'Diagrama ', fontsize = 13, loc = 'center')

plt.tight_layout()
plt.show()
quit()
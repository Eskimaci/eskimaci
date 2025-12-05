import rasterio
from rasterio.mask import mask
import numpy as np
import matplotlib.pyplot as plt

# SAMUEL SUGRA: Stiahnute snimky na analyzu (.jp2)
input_b2 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B02_10m.jp2"
input_b3 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B03_10m.jp2"
input_b4 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B04_10m.jp2"
input_b8 = "static/SAFE/S2C_MSIL2A_20250625T095051_N0511_R079_T33UXP_20250625T152820.SAFE/GRANULE/L2A_T33UXP_A004196_20250625T095707/IMG_DATA/R10m/T33UXP_20250625T095051_B08_10m.jp2"

# SAMUEL SUGRA: Orezane snimky
output_b2 = "static/cropped/trnava_b2.tif"
output_b3 = "static/cropped/trnava_b3.tif"
output_b4 = "static/cropped/trnava_b4.tif"
output_8 = "static/cropped/trnava_b8.tif"


with rasterio.open(input_b4) as red_src:
    red = red_src.read(1).astype('float32')

with rasterio.open(input_b8) as nir_src:
    nir = nir_src.read(1).astype('float32')

# Ochrana proti deleniu nulou (vypne ochranu, numpy to zvladne)
np.seterr(divide='ignore', invalid='ignore')

# vzorec pre vypocet
ndvi = (nir - red) / (nir + red)

# vizualizacia
plt.figure(figsize=(10,10))

# Colormap
plt.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
plt.colorbar(label='NDVI Index (-1 = Voda/Beton, 1 = Husta zelen)')
plt.title('Zelene pluca Trnavy: NDVI Analyza')
plt.show()
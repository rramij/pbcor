# MeerKAT image Primary Beam Correction
# Written by Ramij Raja
# Date: 28 May 2023
# Image and PB image must have same dimension (i.e., pixel to pixel mapping possible)
#########################################
import numpy as np
from astropy.io import fits
from astropy.io.fits import getdata

##########################
# INPUTS
###########
# Both images have to have the same DIMENSION
fits_image = 'A85_1.28GHz_spix_100uv29kl_rob0-MFS-image_restore_bm9.fits'

pb_image = 'Test_1_p8192_r1_f1284_SI_I_re.fits'

pb_cutoff = 0.1 # keep it +ve and >0.

#################################
# Main Code
#################################
data, hdr = getdata(fits_image, header=True)

pbd, pbh = getdata(pb_image, header=True)

a = data[0,0,0:,0:]

b = pbd[0,0,0,0:,0:]

b[b < pb_cutoff] = 'NaN'

c = a / b

data[0,0,0:,0:] = c

fits.writeto(fits_image.replace(".fits", "_PBCOR.fits"), data, hdr, overwrite=True)

print(' ')
print('Output Image: '+fits_image.replace(".fits", "_PBCOR.fits"))
print(' ')
print('###########################  DONE  #########################')
print('Enjoy!, ... or Not???')
# THE END

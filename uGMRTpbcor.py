# uGMRT primary beam correction for WSclean image outputs
# Written by Ramij Raja
# Date: 13 March 2024
# RUN within CASA
# Astropy installed in that CASA version is required
#####################################

# inputs corresponding to the WSclean FITS image

fimage = 'Image_700MHz_GWB_rob0_b-MFS-image.fits'
vis = ['part1.ms','part2.ms','part3.ms','part4.ms','part5.ms','part6.ms']
pb_cutoff = 0.5 # USE -0.2 for no cutoff

###################################
# Main Code
###################################
import os
import numpy as np
from astropy.io import fits
from astropy.io.fits import getdata
from astropy.io.fits import getheader
from casacore.tables import table
###################################

if not os.path.exists('./concatvis.ms'):
  concat(vis=vis,concatvis='concatvis.ms',freqtol='',dirtol='100arcsec')

# Collect info for later tasks
spwtab = table('concatvis.ms/SPECTRAL_WINDOW',ack=False)
nspw = len(spwtab)
nchans = spwtab.getcol('NUM_CHAN')
spwtab.done()
nchans = (nchans / 2)
nchans = nchans.astype(np.int32)
chanlist = nchans.tolist()
spwlist = list(range(0, nspw))
weightlist = [1] * nspw

hdr = getheader(fimage)
imsize = [hdr['NAXIS1'], hdr['NAXIS2']]
cell = [str(hdr['CDELT1'] * 3600.0) + 'arcsec']
nterms=2 # Fixed. It doed not affect the o/p as we use pb.tt0 only.

# Start making primary beam FITS image
if not os.path.exists('./pbimage.pb.tt0.fits'):
  # Make CASA image output template for pbcor
  tclean(vis='concatvis.ms',datacolumn='data',imagename='test_pb',imsize=imsize,cell=cell,
  specmode='mfs',gridder='standard',pblimit=pb_cutoff,deconvolver='mtmfs',
  nterms=nterms,weighting='briggs',robust=0.0,niter=0,restart=True,stokes='RR')

  # Execute uGMRTpb
  sys.path.insert(0,'/home/rramij')
  from uGMRTprimarybeamCASA6.gotasks.ugmrtpb import ugmrtpb
  ugmrtpb(vis='concatvis.ms',imagename='test_pb',nterms=nterms,action='pbcor',pbmin=pb_cutoff,
  spwlist=spwlist,chanlist=chanlist,weightlist=weightlist)
  exportfits(imagename='test_pb.pbcor.workdirectory/test_pb.pb.tt0',
  fitsimage='test_pb.pbcor.workdirectory/test_pb.pb.tt0.fits',overwrite=True)
  os.system('mv test_pb.pbcor.workdirectory/test_pb.pb.tt0.fits ./pbimage.pb.tt0.fits')
  os.system('rm -rf test_pb.*')
  os.system('rm -rf pbname')


# Do PB correction
pbimage='pbimage.pb.tt0.fits'

data, hdr = getdata(fimage, header=True)
data2, hdr2 = getdata(pbimage, header=True)

a = data[0,0,:,:]
b = data2[0,0,:,:]
c = a / b
c[c == np.inf] = np.nan
c[c == -np.inf] = np.nan
data3 = np.array([[c]])

# Write PB corrected image
print('Writing PB corrected image...')
fits.writeto(fimage.replace(".fits", "_pbcor.fits"), data3, hdr, overwrite=True)

print(' ')
print('Output Image: '+fimage.replace(".fits", "_pbcor.fits"))
print(' ')
print('###########################  DONE  #########################')
print('Enjoy!, ... or Not???')
# THE END


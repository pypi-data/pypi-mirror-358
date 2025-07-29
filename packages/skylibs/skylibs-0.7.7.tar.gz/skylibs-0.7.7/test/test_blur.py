import numpy as np
from envmap import EnvironmentMap, rotation_matrix
from matplotlib import pyplot as plt
from tools3d.spharm import SphericalHarmonic


e = EnvironmentMap("pano.jpg", "latlong")
#e.rotate(rotation_matrix(azimuth=np.pi/2, elevation=0, roll=np.pi/2-0.3))#.rotate(rotation_matrix(azimuth=0, elevation=np.pi/2))
spharm_repr = SphericalHarmonic(e, max_l=4)
spham_reconstruction = spharm_repr.reconstruct(31, max_l=3, clamp_negative=True)
import pdb; pdb.set_trace()
spharm_repr.window()
spham_reconstruction_window = spharm_repr.reconstruct(31, max_l=3, clamp_negative=True)
#import pdb; pdb.set_trace()
e_ori = e.copy()
e.resize(64)
e_resized = e.copy()
e.blur(15.)
print(e.data.mean(axis=(0,1)))
sa = e.solidAngles()[:,:,None]
print((sa*e_resized.data).mean(axis=(0,1)))
print((sa*e.data).mean(axis=(0,1)))
print((sa*spham_reconstruction).mean(axis=(0,1)))
print((sa*spham_reconstruction_window).mean(axis=(0,1)))
plt.subplot(321); plt.imshow(e_ori.data); plt.title("Original")
plt.subplot(322); plt.imshow(e.data); plt.title("Spatial blurring")
plt.subplot(323); plt.imshow(e_resized.data); plt.title("Resized (64)")
plt.subplot(324); plt.imshow(spham_reconstruction); plt.title("Spherical harmonics (frequency) blurring")
plt.subplot(325); plt.imshow(spham_reconstruction_window); plt.title("Spherical harmonics (frequency) blurring w/ window")
plt.show()

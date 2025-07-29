from envmap import EnvironmentMap
from tools3d.spharm import SphericalHarmonic



e = EnvironmentMap("pano.jpg", 'latlong')
e = e.resize(256)
print(e.data.shape)
sph = SphericalHarmonic(e)
print(len(sph.coeffs))
import pdb; pdb.set_trace()
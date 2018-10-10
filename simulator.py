import numpy as np

class ContinuumSimulator:
    def __init__(self, area, rm):
        self._area = area
        self._rm = rm

    def read_spectrum(self, filename):
        from scipy.interpolate import interp1d

        xy = [
               (float(line.split()[0]), float(line.split()[1]))
               for line in open(filename)
               if len(line) > 0 and line[0] != '#' and len(line.split()) == 2
             ]
            
        self._x = np.log10([ x[0] for x in xy ])
        self._y = np.log10([ bgScale*x[1] for x in xy ])

        self._spline = interp1d(self._x, self._y, kind='cubic')

    def generate_events(self, emin, emax, time):
        emin = max(emin, 10**self._spline.x[0])
        emax = min(emax, 10**self._spline.x[-1])

        ebins = np.arange(emin, emax, step = self._rm.true_width)

        photons = np.empty([0], dtype=float)
        for i in range(1, len(ebins)):
            energy = 0.5*(ebins[i-1]+ebins[i])
            area = self._area.get(energy)
            nphotons = np.quad(lambda x: 10**self._spline(np.log10(x)), ebins[i-1], ebins) * area * time
            photons = np.append(photons, self._rm.get_energies(energy, nphotons))

        return photons


class LineSimulator:
    def __init__(self, energy, flux, area, rm):
        self._energy = energy
        self._flux = flux
        self._area = area
        self._rm = rm

    def generate_events(self, time):
        nphotons = self._flux * self._area.get(self._energy) * time
        return self._rm.get_energies(self._energy, nphotons)

import numpy as np

class Background:
    def __init__(self, filename):
        from scipy.interpolate import interp1d

        xy = [
               (float(line.split()[0]), float(line.split()[1]))
               for line in open(filename)
               if len(line) > 0 and line[0] != '#' and len(line.split()) == 2
             ]

        hpd = 1./6 #  HPD in arcmin
        hpdFactor = 2 #  extract signal from 2 HPD
        focalLength = 20 # m
        nustarLength = 10 # m
        lengthScale = focalLength/nustarLength
        backgroundArea = np.sqrt(36.) # NuSTAR background corresponds to 36arcmin^2
        detectorAreaScale = hpd*hpdFactor/backgroundArea
        bgScale = 2 * lengthScale * detectorAreaScale  # Factor 2 bc the NuSTAR numbers are per telescope
            
        self._x = np.log10([ x[0] for x in xy ])
        self._y = np.log10([ bgScale*x[1] for x in xy ])

        self._spline = interp1d(self._x, self._y, kind='cubic', fill_value='extrapolate')

    def draw(self):
        import matplotlib.pyplot as plt
        x = np.linspace(10**self._x[0], 10**self._x[-1], num=50, endpoint=True)
        plt.semilogy(x, 10**self._spline(np.log10(x)), '-')

    def get(self, energy):
        return 10**self._spline(np.log10(energy))

    def get_energies(self, emin, emax, time):
        import scipy.integrate as integrate

        # Integrate piecewise using spline supports as boundaries
        lmin = np.log10(emin)
        lmax = np.log10(emax)
        bounds = [lmin]
        imin = None
        imax = None
        for i in range(len(self._spline.x)):
            if imin is None and self._spline.x[i] > lmin:
                imin = i
            elif self._spline.x[i] >= lmax:
                imax = i
                break

        bounds += list(self._spline.x[imin:imax])
        bounds.append(lmax)
            
        total_events = 0.
        for i in range(1, len(bounds)):
            te = integrate.quad(lambda x: 10**self._spline(np.log10(x)), 10**bounds[i-1], 10**bounds[i])[0]
            total_events += te
        total_events = np.random.poisson(total_events * time)
        #print total_events, time*integrate.quad(lambda x: 10**self._spline(np.log10(x)), emin, emax)[0]

        xvalues = np.arange(emin, emax, 0.01)  # bin in 10eV steps
        cdf = np.cumsum(10**self._spline(np.log10(xvalues)))
        cdf = cdf/cdf[-1]
        
        values = np.random.rand(total_events)
        value_bins = np.searchsorted(cdf, values)
        return value_bins * 0.01 + emin


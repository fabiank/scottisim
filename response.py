import numpy as np

class EffectiveArea:
    def __init__(self, responsefile):
        from scipy.interpolate import interp1d

        xy = [
               (float(line.split()[0]), float(line.split()[1]))
               for line in open(responsefile)
               if len(line) > 0 and line[0] != '#' and len(line.split()) == 2
             ]
        self._x = np.log10([ x[0] for x in xy ])
        self._y = np.log10([ x[1] for x in xy ])

        self._spline = interp1d(self._x, self._y, kind='cubic')

    def draw(self):
        import matplotlib.pyplot as plt
        x = np.linspace(10**self._x[0], 10**self._x[-1], num=50, endpoint=True)
        plt.semilogy(x, 10**self._spline(np.log10(x)), '-')

    def get(self, energy):
        return 10**self._spline(np.log10(energy))

    def get_number(self, emin, emax, flux, time):
        a1 = 10**self._spline(np.log10(emin))
        a2 = 10**self._spline(np.log10(emax))
        area = 0.5*(a1 + a2)
        return np.random.poisson(flux*time*area*(emax-emin))


class RedistributionMatrix:
    def __init__(self, rmf, fix_cdfs=False, scale_cdfs=True):
        lines = [ line.split() for line in open(rmf) if len(line) > 0 and line[0] != '#' ]

        # The first line contains the RMF definition
        line1 = lines[0]
        self._nTrue = int(line1[0])
        self._trueMin = float(line1[1])
        self._trueMax = float(line1[2])
        self._nMeas = int(line1[3])
        self._measMin = float(line1[4])
        self._measMax = float(line1[5])

        # The other lines contain the data, 1 line per true energy, 1 column per reconstructed energy
        data = [ [ float(x) for x in line ] for line in lines[1:] ]
        
        # The total efficiency per true energy is the sum over the columns
        self._efficiency = [ sum(line) for line in data ]

        # The CDF is needed to generate random numbers
        cdfs = [ np.cumsum(line) for line in data ]

        if fix_cdfs:
            # Prevent flat regions in CDF
            for c, cdf in enumerate(cdfs):
                print 'Fixing CDF %d/%d' % (c, len(cdfs))
                bc_last = 0
                cdfmax = cdf[-1]
                if cdfmax == 0:
                    continue
    
                for b in range(len(cdf)):
                    bc = cdf[b]
                    if bc == cdfmax:
                        break
                    
                    if bc == bc_last and bc_last > 0:
                        #print '    fixing bin %d/%d' % (b, len(cdf))
                        for i in range(b+1, len(cdf)):
                            if cdf[i] > bc_last:
                                delta = cdf[i]-bc_last
                                step = delta/(i-b+1)
                                #print '        step: %g' % step
                                for j in range(b, i):
                                    cdf[j] = bc_last + (j-b+1)*step
                                break
                    bc_last = cdf[b]

        if scale_cdfs:
            self._cdfs = []
            for cdf in cdfs:
                scale = 1
                if cdf[-1] > 0:
                    scale = cdf[-1]
                self._cdfs.append(cdf/scale)
        else:
            self._cdfs = cdfs

        # Energies associated with CDF bins
        bw = (self._measMax - self._measMin)/self._nMeas
        self._cdf_energies = np.arange(self._measMin + 0.5*bw, self._measMax, step=bw)

        # True energy bin width
        self._true_width = (self._trueMax-self._trueMin)/self._nTrue

    def get_energies(self, etrue, number):
        e_bin = int(np.floor((etrue - self._trueMin)/self._true_width))
        if e_bin < 0 or e_bin >= self._nTrue:
            return None

        cdf = self._cdfs[e_bin]
        if cdf[-1] <= 0:
            return None

        efficiency = self._efficiency[e_bin]
        values = np.random.rand(int(number*efficiency))
        value_bins = np.searchsorted(cdf, values)
        return etrue - self._cdf_energies[value_bins]  # Response matrix is Etrue - Edet

    def plot(self, etrue, number):
        import matplotlib.pyplot as plt
        plt.hist(self.get_energies(etrue, number), bins=100)
        plt.yscale('log', nonposy='clip')

    def store(self, filename):
        outfile = open(filename, 'w')
        outfile.write('# One line per true energy\n')
        outfile.write('# N(E_true) | E_true^min | E_true^max | N(E_obs) | E_obs^min | E_obs^max\n')
        outfile.write('%d %g %g %d %g %g\n' % (self._nTrue, self._trueMin, self._trueMax, self._nMeas, self._measMin, self._measMax))
        
        for cdf in self._cdfs:
            last = 0
            for b, bc in enumerate(cdf):
                c = bc-last
                if c == 0:
                    outfile.write('0 ')
                else:
                    outfile.write('%g ' % c)
                last = bc
            outfile.write('\n')

        outfile.close()

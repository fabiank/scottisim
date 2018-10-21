#!/usr/bin/env python

import sys
import os.path

mydir = os.path.dirname(os.path.realpath(__file__))

import numpy as np
import matplotlib.pyplot as plt

import matplotlib.pylab as pylab

import background
import response
import simfile
import simulator

print 'Reading input file ...'    
sf = simfile.SimFile(sys.argv[1])

if sf.duration is None:
    print 'Missing keyword "duration"'
    exit(1)

if sf.bins is None:
    print 'Missing keyword "bins"'
    exit(1)

print 'Loading effective area ...'
area = response.EffectiveArea(mydir + '/scotti.area')

rmf_file = mydir + '/scotti-fixed.rmf'
if not os.path.isfile(rmf_file):
    print 'RMF file does not exist. Regenerating, which takes a moment.'
    import subprocess
    subprocess.call([mydir + '/cdffixer.py', mydir + '/scotti.rmf', rmf_file])
    print 'Done generating smoothed RMF'

print 'Loading response matrix ...'
rm = response.RedistributionMatrix(rmf_file)

print 'Loading background ...'
bg = background.Background(mydir + '/scotti.background')

cont_photons = []
if not sf.spectrum is None:
    print 'Loading spectrum ...'
    spectrum_sim = simulator.ContinuumSimulator(area, rm)
    spectrum_sim.read_spectrum(sf.spectrum)

    print 'Generating continuum photons ...'
    cont_photons = spectrum_sim.generate_events(sf.bins[1], sf.bins[2], sf.duration)
    print '    Total number of photons: %d' % len(cont_photons)

line_photons = []
if len(sf.lines) > 0:
    print 'Generating line photons ...'
    total_line_photons = 0
    for line in sf.lines:
        line_sim = simulator.LineSimulator(line[0], line[1], area, rm)
        photons = line_sim.generate_events(sf.duration)
        line_photons.append(photons)
    total_line_photons += len(photons)
    print '    Total nuber of photons: %d' % total_line_photons

print 'Generating background photons ...'
bg_photons = bg.get_energies(sf.bins[1], sf.bins[2], sf.duration)
print '    Total number of photons: %d' % len(bg_photons)

photons = np.concatenate(tuple([cont_photons, bg_photons] + line_photons))

log_e1 = np.log10(sf.bins[1])
log_e2 = np.log10(sf.bins[2])
bw = (log_e2 - log_e1)/sf.bins[0]
bins = 10**np.arange(log_e1, log_e2 + 0.5*bw, step = bw)
hist, bin_edges = np.histogram(photons, bins=bins)

#plt.hist(photons, bins=bins)

for i, bc in enumerate(hist):
    hist[i] = bc/(bin_edges[i+1]-bin_edges[i])

font = {'family': 'serif',
        'weight': 'normal',
        'size': 16,
        }
    
plot = plt.step(bin_edges, np.append(hist, [0]))
plt.xscale('log')
plt.xlabel('Energy [keV]', fontdict=font)
plt.xticks(fontsize=16, family='serif')
plt.yscale('log', nonposy='clip')
plt.ylabel('Counts / keV', fontdict=font)
plt.yticks(fontsize=16, family='serif')
plt.tight_layout()

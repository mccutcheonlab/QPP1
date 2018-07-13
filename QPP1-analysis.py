# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 15:09:12 2018

@author: James Rig
"""

import JM_general_functions as jmf
import JM_custom_figs as jmfig
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

## Colour scheme
col={}
col['np_cas'] = 'xkcd:silver'
col['np_malt'] = 'white'
col['lp_cas'] = 'xkcd:kelly green'
col['lp_malt'] = 'xkcd:light green'

class Session(object):
    
    def __init__(self, metafiledata):
        self.medfile = metafiledata[hrows['medfile']]
        self.rat = metafiledata[hrows['rat']]
        self.session = metafiledata[hrows['session']]
        self.diet = metafiledata[hrows['dietgroup']]
        self.quinconc = metafiledata[hrows['quinine']]
        self.bottleL = metafiledata[hrows['bottleL']]
        self.bottleR = metafiledata[hrows['bottleR']]
        self.intakeL = metafiledata[hrows['intakeL']]
        self.intakeR = metafiledata[hrows['intakeR']]
        
    def extractlicks(self):
        self.cas_meddata = jmf.medfilereader(medfolder + self.medfile,
                                         varsToExtract = sub2var(self, 'Cas'),
                                         remove_var_header = True)
        self.malt_meddata = jmf.medfilereader(medfolder + self.medfile,
                                 varsToExtract = sub2var(self, 'Malt'),
                                 remove_var_header = True)
    
    def calculatelickdata(self, interpolate='none'):
        self.cas_data = jmf.lickCalc(self.cas_meddata[0],
                                    offset=self.cas_meddata[1],
                                    burstThreshold=0.5, binsize=120,
                                    adjustforlonglicks=interpolate)
        self.malt_data = jmf.lickCalc(self.malt_meddata[0],
                                    offset=self.malt_meddata[1],
                                    burstThreshold=0.5, binsize=120,
                                    adjustforlonglicks=interpolate)
        self.pref = self.cas_data['total'] / (self.cas_data['total']+self.malt_data['total'])
        self.pref_intake = self.cas_intake / (self.cas_intake + self.malt_intake)
        
    def extractintake(self):
        self.cas_intake = sub2intake(self, 'Cas')
        self.malt_intake = sub2intake(self, 'Malt')

def sub2var(session, substance):
    
    if substance in session.bottleL:
        varsOut = ['b', 'c']        
    if substance in session.bottleR:
        varsOut = ['e', 'f']
        
    try:      
        return varsOut
    except UnboundLocalError:
        print('Searched for substance not found in either bottle - lick variables will be empty')
        return []

def sub2intake(session, substance):
    if substance in session.bottleL:
        intake = int(session.intakeL)
    if substance in session.bottleR:
        intake = int(session.intakeR)
      
    try:      
        return intake
    except UnboundLocalError:
        print('Searched for substance not found in either bottle - lick variables will be empty')
        return []
         
# Extracts data from metafile
metafile = 'C:\\Users\\James Rig\\Documents\\GitHub\\QPP1\\QPP1_metafile.txt'
medfolder = 'R:\\DA_and_Reward\\fn55\\QPP\QPP-1\\QPP1_allmedfiles\\'

rows, header = jmf.metafilereader(metafile)

hrows = {}
for idx, field in enumerate(header):
    hrows[field] = idx

# Sets up individual objects for each sessio and gets data from medfiles
sessions = {}
        
for row in rows:
    sessionID = row[hrows['rat']] + '-' + row[hrows['session']]
    sessions[sessionID] = Session(row)
    
subset = [sessions[x] for x in sessions if int(sessions[x].session) > 13]

for x in subset:
    x.extractlicks()
    x.extractintake()
    x.calculatelickdata(interpolate='none')
    
quinconcs = np.unique([float(x.quinconc) for x in subset])

# Puts data in a pandas dataframe for easy acces

df = pd.DataFrame()
    
df.insert(0, 'rat', [x.rat for x in subset])
df.insert(1, 'diet', [x.diet for x in subset])
df.insert(2, 'quin', [float(x.quinconc) for x in subset])
df.insert(3, 'pref', [x.pref_intake for x in subset])
df.insert(4, 'cas_pal', [x.cas_data['bMean'] for x in subset])
df.insert(5, 'malt_pal', [x.malt_data['bMean'] for x in subset])

#df.insert(3, 'cashist', [x.cas_data['hist'] for x in subset])
#df.insert(4, 'malthist', [x.malt_data['hist'] for x in subset])
#df.insert(5, 'caslicks', [x.cas_data['total'] for x in subset])
#df.insert(6, 'maltlicks', [x.malt_data['total'] for x in subset])
#df.insert(7, 'caslicks_all', [x.cas_data['licks'] for x in subset])
#df.insert(8, 'maltlicks_all', [x.malt_data['licks'] for x in subset])


NR = {}
PR = {}

keys = ['pref', 'caspal', 'maltpal']

for key in keys:
    NR[key] = []
    PR[key] = []

dietmsk = df.diet == 'NR'

for x in quinconcs:
    quinmsk = df.quin == x
    for groupdict, msk in zip([NR, PR], [dietmsk, ~dietmsk]):
        groupdict[keys[0]].append(list(df['pref'][msk & quinmsk]))
        groupdict[keys[1]].append(list(df['cas_pal'][msk & quinmsk]))
        groupdict[keys[2]].append(list(df['malt_pal'][msk & quinmsk]))

#jmfig.barscatter([nr_data, pr_data], transpose=False)
#_,_,_,_ = jmfig.barscatter(PR['pref'])
_,_,_,_ = jmfig.barscatter(PR['caspal'])
#_,_,_,_ = jmfig.barscatter(PR['maltpal'])
#_,_,_,_ = jmfig.barscatter([PR['caspal'], PR['maltpal']], transpose=True, paired=True)


figQPPpref, ax = plt.subplots()
jmfig.barscatter(PR['pref'],
                            barwidth=0.8,
                            barfacecolor = ['xkcd:kelly green'],
                            scatteredgecolor = ['xkcd:charcoal'],
                            barlabels = [str(x) for x in quinconcs],
                            barlabeloffset=2500,
                            ax=ax)
ax.set_ylabel('Casein preference')
ax.set_xlabel('Quinine concentration (mM)', labelpad=30)

try:
    figQPPpref.savefig('C:\\Users\\James Rig\\Dropbox\\AbstractsAndTalks\\180718_SSIB_Florida\\figs\\QPPpref.eps')
except FileNotFoundError:
    print('Could not find path to save QPPpref')
    
figQPPcaspal, ax = plt.subplots()
jmfig.barscatter(PR['caspal'],
                 barwidth=0.8,
                 barfacecolor = ['xkcd:kelly green'],
                 scatteredgecolor = ['xkcd:charcoal'],
                 barlabels = [str(x) for x in quinconcs],
                 barlabeloffset=2500,
                 ax=ax)
ax.set_ylabel('Casein palatability (licks/cluster')
ax.set_xlabel('Quinine concentration (mM)', labelpad=30)

try:
    figQPPcaspal.savefig('C:\\Users\\James Rig\\Dropbox\\AbstractsAndTalks\\180718_SSIB_Florida\\figs\\QPPcaspal.eps')
except FileNotFoundError:
    print('Could not find path to save QPPcaspal')
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Simulation
================

  CEO class for simulation of muon decays in nuSTORM production 
  straight.

  Not developed for the moment! KL 20Jan21.

  Class attributes:
  -----------------
  __instance : Set on creation of first (and only) instance.

  Packages loaded:
  ----------------
  "time"  : to get current date/time
  "random": uniform random number generator
      
  Instance attributes:
  --------------------
  None yet!
    
  Methods:
  --------
  Built-in methods __new__, __repr__ and __str__.
      __new__ : Creates singleton class and prints version, PDG
                reference, and values of constants used.
      __repr__: One liner with call.
      __str__ : Dump of contents

  Get/set methods:
      CdVrsn()     : Returns code version number.
      getRandomSeed: Returns random seed
  
  Simulation methods:
      getRandom    : Returns uniformly distributed randum number
      getParabolic : Generates a parabolic distributed random number from
                     -p1 to p1 (p1 input)

Created on Thu 10Jan21;11:04: Version history:
----------------------------------------------
 1.1: 25Feb21: Add Output to a root file
 1.0: 10Jan21: First implementation

@author: kennethlong
"""

#--------  Module dependencies
import random as __Rnd
import numpy as np
import nuSTORMPrdStrght as nuPrdStrt
import NeutrinoEventInstance as nuEvtInst
import ntupleMake as ntM 
import plane as plane

#--------  Module methods
def getRandom():
    return __Rnd.random()

def getParabolic(p1):
    ran = getRandom()
    a = np.array( [ 1., 0., (-3.*p1*p1), (2.*p1*p1*p1*(2.*ran - 1.)) ] )
    r = np.roots(a)
    isol = 0
    for ri in r:
        if not isinstance(ri, complex):
            if ri >= -p1:
                if ri <= p1:
                    isol += 1
                    p = ri
    if isol != 1:
        raiseException("nuSTORMPrdStrght.getParabolic; p multiply defined")
    return p

#--------  Simulation class  --------
class Simulation(object):
    import random as __Rnd
    import time as __T
    __RandomSeed = __T.time()

    __instance = None

#--------  "Built-in methods":
    def __new__(cls, NEvt=5, pmu=5., filename=None, rootfilename=None):
        if cls.__instance is None:
            print('Simulation.__new__: creating the Simulation object')
            print('-------------------')
            cls.__instance = super(Simulation, cls).__new__(cls)
            
            cls.__Rnd.seed(int(cls.__RandomSeed))

            cls._NEvt         = NEvt
            cls._pmu          = pmu
            cls._nufile       = filename
            cls._rootfilename = rootfilename
            cls._nuStrt       = nuPrdStrt.nuSTORMPrdStrght(filename)

            # Summarise initialisation
            cls.print(cls)

        return cls.__instance

    def __repr__(self):
        return "Simulation()"

    def __str__(self):
        self.__repr__()
        self.print()


    def RunSim(self):
        print()
        print('Simulation.RunSim: simulation begins')
        print('-----------------')
    # Define root output stream
        runNumber=9.0                   # set run number
        nt = ntM.ntupleMake(runNumber, "nuStorm.root")
        if (nt.Version != 2.6):
          raiseException("Incorrect version of ntupleMaker")
    # Define the distance of the downstream plane where the flux is calculated
        fluxPlane = plane.plane(50.0)

        iCnt = 0
        Scl  = 1
        prt  = 0
        for iEvt in range(self._NEvt):
            if (iEvt % Scl) == 0:
                iCnt += 1
                print("    Generating event ", iEvt)
                prt = 1
                if iCnt == 10:
                    Scl  = Scl * 10
                    iCnt = 0

#  generate Event
            nuEvt = nuEvtInst.NeutrinoEventInstance(self._pmu)
#  write to event branch
            nt.treeFill(nuEvt)
#  Check intersection with downstream plane
            hitE,hitMu=fluxPlane.findHitPosition(nuEvt)
            nt.fluxFill(hitE, hitMu)
            
            if prt == 1:
                prt = 0
                print(nuEvt)
                print("    End of this event simulation")

            del(nuEvt)

        nt.output()
                
            
#--------  "Get methods" only; version, reference, and constants
#.. Methods believed to be self documenting(!)

    def CdVrsn(self):
        return 1.0

    def getRandomSeed(self):
        return Simulation.__RandomSeed

#--------  Utilities:
    def print(self):
        print("    Simulation.print: version:", self.CdVrsn(self))
        print("      state of random generator:", self.__Rnd.getstate()[0])
        print("      number of events to generate:", self._NEvt)
        print("      muon beam momentum setting:", self._pmu)
        print("      nuSTORM specification file:", self._nufile)
        print("      root filename for output  :", self._rootfilename)
        print(self._nuStrt)

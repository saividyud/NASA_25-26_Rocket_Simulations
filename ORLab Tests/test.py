import os
import sys

import numpy as np
import warnings
from matplotlib import pyplot as plt

import orlab as ol
from random import gauss

print()
print('=' * 100)
with ol.OpenRocketInstance('./OpenRocket-23.09.jar') as instance:
    # Defining ORLab helper
    orl = ol.Helper(instance)
    print('=' * 100)
    print()

    # Loading the OpenRocket file
    doc = orl.load_doc('./ORLab Tests/10-14-24 NASA 24-25 Subscale.ork')

    # Getting the Nth simulation
    sim = doc.getSimulation(3)
    
    print(sim.getName())
    print('-' * 20)

    # Extracting the options from the simulation
    opts = sim.getOptions()
    opts.setLaunchRodAngle(0)  # Set a default launch rod angle

    # Extracting data about the rocket from the simulation
    rocket = sim.getRocket()

    # Printing all children of the rocket
    children = rocket.getAllChildren()
    for i, child in enumerate(children):
        print(f"{i}. {child}: {type(child)}")

    print('-' * 20)
    print()
    child_index = 1

    current_child = children[child_index]
    print(current_child)
    for attr in dir(current_child):
        if not attr.startswith('_'):
            print(f'\t{attr}')

    print('-' * 20)
    print()

print('=' * 100)
print('Shut down JVM')
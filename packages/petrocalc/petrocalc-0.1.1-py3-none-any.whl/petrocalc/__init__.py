"""
petrocalc: A comprehensive Python library for petroleum engineering calculations.

This library provides modules for various petroleum engineering calculations including:
- Drilling and wellbore calculations
- Reservoir engineering
- Production engineering  
- Fluid properties
- Rock properties
- Well completion and stimulation
- And more...

Author: Muhammad Farzad Ali
"""

__version__ = "0.1.1"
__author__ = "Muhammad Farzad Ali"
__email__ = "muhammad.farzad.ali@gmail.com"

# Import main modules for easy access
from . import drilling
from . import reservoir
from . import production
from . import fluids
from . import rock_properties
from . import completion
from . import pressure
from . import flow
from . import thermodynamics
from . import economics

__all__ = [
    "drilling",
    "reservoir", 
    "production",
    "fluids",
    "rock_properties",
    "completion",
    "pressure",
    "flow", 
    "thermodynamics",
    "economics"
]

"""
Drilling and wellbore engineering calculations.

This module contains functions for drilling-related calculations including:
- Mud properties and hydraulics
- Hole cleaning and cuttings transport
- Torque and drag calculations
- Pressure losses in drilling systems
- Wellbore stability
"""

import math
from typing import Union, Tuple, Optional


def mud_weight_to_pressure_gradient(mud_weight: float, unit: str = "ppg") -> float:
    """
    Converts mud weight to pressure gradient.
    
    Args:
        mud_weight (float): Mud weight value
        unit (str): Unit of mud weight ("ppg" for pounds per gallon, "sg" for specific gravity)
        
    Returns:
        float: Pressure gradient in psi/ft
        
    Raises:
        ValueError: If unit is not supported
    """
    if unit.lower() == "ppg":
        return mud_weight * 0.052
    elif unit.lower() == "sg":
        return mud_weight * 0.433
    else:
        raise ValueError("Unit must be 'ppg' or 'sg'")


def hydrostatic_pressure(mud_weight: float, depth: float, unit: str = "ppg") -> float:
    """
    Calculates hydrostatic pressure at a given depth.
    
    Args:
        mud_weight (float): Mud weight in ppg or specific gravity
        depth (float): Depth in feet
        unit (str): Unit of mud weight ("ppg" or "sg")
        
    Returns:
        float: Hydrostatic pressure in psi
    """
    pressure_gradient = mud_weight_to_pressure_gradient(mud_weight, unit)
    return pressure_gradient * depth


def annular_velocity(flow_rate: float, hole_diameter: float, pipe_diameter: float) -> float:
    """
    Calculates annular velocity in drilling operations.
    
    Args:
        flow_rate (float): Flow rate in gpm
        hole_diameter (float): Hole diameter in inches
        pipe_diameter (float): Pipe outer diameter in inches
        
    Returns:
        float: Annular velocity in ft/min
    """
    annular_area = (hole_diameter**2 - pipe_diameter**2) * math.pi / 4
    return (flow_rate * 0.3208) / (annular_area / 144)


def pipe_velocity(flow_rate: float, pipe_inner_diameter: float) -> float:
    """
    Calculates velocity inside pipe.
    
    Args:
        flow_rate (float): Flow rate in gpm
        pipe_inner_diameter (float): Pipe inner diameter in inches
        
    Returns:
        float: Pipe velocity in ft/min
    """
    pipe_area = (pipe_inner_diameter**2 * math.pi) / 4
    return (flow_rate * 0.3208) / (pipe_area / 144)


def reynolds_number(velocity: float, diameter: float, density: float, viscosity: float) -> float:
    """
    Calculates Reynolds number for flow in pipes.
    
    Args:
        velocity (float): Velocity in ft/sec
        diameter (float): Pipe diameter in ft
        density (float): Fluid density in lb/ft³
        viscosity (float): Dynamic viscosity in cp
        
    Returns:
        float: Reynolds number (dimensionless)
    """
    return (density * velocity * diameter) / (viscosity * 6.72e-4)


def fanning_friction_factor(reynolds_number: float, roughness: float = 0.0006) -> float:
    """
    Calculates Fanning friction factor using Colebrook-White equation.
    
    Args:
        reynolds_number (float): Reynolds number
        roughness (float): Relative roughness (dimensionless)
        
    Returns:
        float: Fanning friction factor
    """
    if reynolds_number < 2100:
        return 16 / reynolds_number
    else:
        # Simplified approximation for turbulent flow
        return 0.0791 / (reynolds_number**0.25)


def pressure_loss_in_pipe(
    flow_rate: float, 
    pipe_length: float, 
    pipe_diameter: float, 
    density: float, 
    viscosity: float
) -> float:
    """
    Calculates pressure loss in pipe due to friction.
    
    Args:
        flow_rate (float): Flow rate in gpm
        pipe_length (float): Pipe length in ft
        pipe_diameter (float): Pipe inner diameter in inches
        density (float): Fluid density in lb/ft³
        viscosity (float): Dynamic viscosity in cp
        
    Returns:
        float: Pressure loss in psi
    """
    velocity = pipe_velocity(flow_rate, pipe_diameter)
    velocity_fps = velocity / 60  # Convert to ft/sec
    diameter_ft = pipe_diameter / 12  # Convert to ft
    
    re = reynolds_number(velocity_fps, diameter_ft, density, viscosity)
    f = fanning_friction_factor(re)
    
    return (2 * f * density * velocity_fps**2 * pipe_length) / (32.174 * diameter_ft * 144)


def critical_flow_rate(
    hole_diameter: float, 
    pipe_diameter: float, 
    cutting_diameter: float,
    fluid_density: float,
    cutting_density: float
) -> float:
    """
    Calculates critical flow rate for hole cleaning.
    
    Args:
        hole_diameter (float): Hole diameter in inches
        pipe_diameter (float): Pipe outer diameter in inches
        cutting_diameter (float): Cutting particle diameter in inches
        fluid_density (float): Drilling fluid density in ppg
        cutting_density (float): Cutting density in ppg
        
    Returns:
        float: Critical flow rate in gpm
    """
    # Simplified Moore's equation
    annular_area = (hole_diameter**2 - pipe_diameter**2) * math.pi / 4
    
    # Terminal settling velocity
    terminal_velocity = 116.6 * math.sqrt(
        (cutting_density - fluid_density) * cutting_diameter / fluid_density
    )
    
    # Critical flow rate
    return (terminal_velocity * annular_area) / (0.3208 * 144)


def torque_calculation(
    weight_on_bit: float,
    bit_diameter: float,
    formation_strength: float,
    friction_coefficient: float = 0.35
) -> float:
    """
    Calculates drilling torque at the bit.
    
    Args:
        weight_on_bit (float): Weight on bit in lbs
        bit_diameter (float): Bit diameter in inches
        formation_strength (float): Formation compressive strength in psi
        friction_coefficient (float): Friction coefficient between bit and rock
        
    Returns:
        float: Torque in ft-lbs
    """
    bit_radius = bit_diameter / 24  # Convert to ft and get radius
    torque = friction_coefficient * weight_on_bit * bit_radius
    return torque


def hookload_calculation(
    pipe_weight: float,
    buoyancy_factor: float,
    overpull: float = 0
) -> float:
    """
    Calculates hookload during drilling operations.
    
    Args:
        pipe_weight (float): Total pipe weight in air in lbs
        buoyancy_factor (float): Buoyancy factor (dimensionless)
        overpull (float): Additional overpull in lbs
        
    Returns:
        float: Hookload in lbs
    """
    return pipe_weight * buoyancy_factor + overpull


def buoyancy_factor(mud_density: float, steel_density: float = 65.4) -> float:
    """
    Calculates buoyancy factor for steel in drilling mud.
    
    Args:
        mud_density (float): Mud density in lb/ft³
        steel_density (float): Steel density in lb/ft³ (default 65.4)
        
    Returns:
        float: Buoyancy factor (dimensionless)
    """
    return 1 - (mud_density / steel_density)

"""
Thermodynamics calculations for petroleum engineering.

This module contains functions for thermodynamic calculations including:
- Heat transfer calculations
- Phase behavior
- Thermal properties
- Temperature and heat balance calculations
"""

import math
from typing import Union, Tuple, Optional


def heat_capacity_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates heat capacity of crude oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Heat capacity in Btu/lb-°F
    """
    api = oil_gravity
    t = temperature
    
    # Watson and Nelson correlation
    specific_gravity = 141.5 / (api + 131.5)
    k = (1.8 * specific_gravity)**0.5
    
    cp = (0.388 + 0.00045 * t) / math.sqrt(specific_gravity)
    
    return cp


def heat_capacity_gas(
    gas_gravity: float,
    temperature: float,
    pressure: float = 14.7
) -> float:
    """
    Calculates heat capacity of natural gas at constant pressure.
    
    Args:
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia (default 14.7)
        
    Returns:
        float: Heat capacity in Btu/lb-°F
    """
    sg = gas_gravity
    t = temperature + 459.67  # Convert to °R
    p = pressure
    
    # Correlation for natural gas
    cp = 0.031 + 0.0000154 * t - 5.3e-9 * t**2
    
    # Pressure correction (simplified)
    cp = cp * (1 + 0.0001 * (p - 14.7))
    
    return cp


def heat_capacity_water(temperature: float, pressure: float = 14.7) -> float:
    """
    Calculates heat capacity of water.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia (default 14.7)
        
    Returns:
        float: Heat capacity in Btu/lb-°F
    """
    t = temperature
    
    # Correlation for liquid water
    cp = 1.0 - 0.0001 * (t - 32) + 0.0000002 * (t - 32)**2
    
    return cp


def thermal_conductivity_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates thermal conductivity of crude oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Thermal conductivity in Btu/hr-ft-°F
    """
    api = oil_gravity
    t = temperature
    
    # Cragoe correlation
    specific_gravity = 141.5 / (api + 131.5)
    k = 0.08 - 0.0003 * (t - 32) - 0.02 * specific_gravity
    
    return max(0.05, k)  # Minimum practical value


def thermal_conductivity_gas(
    gas_gravity: float,
    temperature: float,
    pressure: float = 14.7
) -> float:
    """
    Calculates thermal conductivity of natural gas.
    
    Args:
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia (default 14.7)
        
    Returns:
        float: Thermal conductivity in Btu/hr-ft-°F
    """
    sg = gas_gravity
    t = temperature + 459.67  # Convert to °R
    
    # Correlation for natural gas
    k = 0.00154 * (t / 530)**0.79 / sg**0.5
    
    return k


def thermal_expansion_coefficient_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates thermal expansion coefficient of oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Thermal expansion coefficient in 1/°F
    """
    api = oil_gravity
    t = temperature
    
    # Standing correlation
    beta = (0.00036 + 0.000055 * api) * (1 + 0.0004 * (t - 60))
    
    return beta


def heat_transfer_coefficient_forced_convection(
    velocity: float,
    pipe_diameter: float,
    fluid_density: float,
    fluid_viscosity: float,
    thermal_conductivity: float,
    heat_capacity: float
) -> float:
    """
    Calculates heat transfer coefficient for forced convection in pipes.
    
    Args:
        velocity (float): Fluid velocity in ft/sec
        pipe_diameter (float): Pipe diameter in ft
        fluid_density (float): Fluid density in lb/ft³
        fluid_viscosity (float): Fluid viscosity in cp
        thermal_conductivity (float): Thermal conductivity in Btu/hr-ft-°F
        heat_capacity (float): Heat capacity in Btu/lb-°F
        
    Returns:
        float: Heat transfer coefficient in Btu/hr-ft²-°F
    """
    v = velocity
    d = pipe_diameter
    rho = fluid_density
    mu = fluid_viscosity * 2.42  # Convert cp to lb/hr-ft
    k = thermal_conductivity
    cp = heat_capacity
    
    # Reynolds number
    re = rho * v * d * 3600 / mu  # 3600 to convert velocity units
    
    # Prandtl number
    pr = cp * mu / k
    
    # Nusselt number (Dittus-Boelter equation)
    if re > 10000:
        nu = 0.023 * re**0.8 * pr**0.4
    else:
        # Laminar flow
        nu = 3.66
    
    # Heat transfer coefficient
    h = nu * k / d
    
    return h


def heat_loss_insulated_pipe(
    inner_temperature: float,
    outer_temperature: float,
    pipe_inner_radius: float,
    pipe_outer_radius: float,
    insulation_outer_radius: float,
    pipe_thermal_conductivity: float,
    insulation_thermal_conductivity: float,
    length: float
) -> float:
    """
    Calculates heat loss from insulated pipe.
    
    Args:
        inner_temperature (float): Inner fluid temperature in °F
        outer_temperature (float): Ambient temperature in °F
        pipe_inner_radius (float): Pipe inner radius in ft
        pipe_outer_radius (float): Pipe outer radius in ft
        insulation_outer_radius (float): Insulation outer radius in ft
        pipe_thermal_conductivity (float): Pipe thermal conductivity in Btu/hr-ft-°F
        insulation_thermal_conductivity (float): Insulation thermal conductivity in Btu/hr-ft-°F
        length (float): Pipe length in ft
        
    Returns:
        float: Heat loss in Btu/hr
    """
    t_inner = inner_temperature
    t_outer = outer_temperature
    r1 = pipe_inner_radius
    r2 = pipe_outer_radius
    r3 = insulation_outer_radius
    k_pipe = pipe_thermal_conductivity
    k_insul = insulation_thermal_conductivity
    l = length
    
    # Thermal resistances
    r_pipe = math.log(r2 / r1) / (2 * math.pi * k_pipe * l)
    r_insul = math.log(r3 / r2) / (2 * math.pi * k_insul * l)
    
    # Total thermal resistance
    r_total = r_pipe + r_insul
    
    # Heat loss
    q = (t_inner - t_outer) / r_total
    
    return q


def temperature_drop_flowing_well(
    depth: float,
    flow_rate: float,
    geothermal_gradient: float = 0.015,
    surface_temperature: float = 70
) -> float:
    """
    Calculates temperature at depth in flowing well.
    
    Args:
        depth (float): Depth in ft
        flow_rate (float): Flow rate in bbl/day
        geothermal_gradient (float): Geothermal gradient in °F/ft (default 0.015)
        surface_temperature (float): Surface temperature in °F (default 70)
        
    Returns:
        float: Temperature at depth in °F
    """
    d = depth
    q = flow_rate
    grad = geothermal_gradient
    t_surf = surface_temperature
    
    # Static temperature
    t_static = t_surf + grad * d
    
    # Flowing temperature (simplified - assumes cooling due to expansion)
    cooling_factor = 1 - 0.0001 * math.sqrt(q)  # Simplified correlation
    t_flowing = t_static * cooling_factor
    
    return t_flowing


def joule_thomson_coefficient_gas(
    temperature: float,
    pressure: float,
    gas_gravity: float
) -> float:
    """
    Calculates Joule-Thomson coefficient for natural gas.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        gas_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        float: Joule-Thomson coefficient in °F/psi
    """
    t = temperature + 459.67  # Convert to °R
    p = pressure
    sg = gas_gravity
    
    # Calculate reduced properties
    tc = 168 + 325 * sg - 12.5 * sg**2  # Critical temperature in °R
    pc = 677 + 15.0 * sg - 37.5 * sg**2  # Critical pressure in psia
    
    tr = t / tc
    pr = p / pc
    
    # Simplified correlation
    jt = (5.4 - 17.5 * tr + 8.7 * tr**2) / (pc * (1 + 0.1 * pr))
    
    return jt


def heat_of_vaporization_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates heat of vaporization for crude oil.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Heat of vaporization in Btu/lb
    """
    api = oil_gravity
    t = temperature + 459.67  # Convert to °R
    
    # Watson correlation
    specific_gravity = 141.5 / (api + 131.5)
    
    # Critical temperature estimate
    tc = 1166 - 3 * api  # °R
    
    # Reduced temperature
    tr = t / tc
    
    if tr >= 1.0:
        return 0  # Above critical temperature
    
    # Heat of vaporization
    hv = 8.314 * tc * (1 - tr)**0.38 / (28.97 * specific_gravity)
    
    return hv


def bubble_point_temperature(
    pressure: float,
    oil_gravity: float,
    gas_gravity: float,
    gas_oil_ratio: float
) -> float:
    """
    Calculates bubble point temperature.
    
    Args:
        pressure (float): Pressure in psia
        oil_gravity (float): Oil API gravity in degrees
        gas_gravity (float): Gas specific gravity (air = 1.0)
        gas_oil_ratio (float): Gas-oil ratio in scf/STB
        
    Returns:
        float: Bubble point temperature in °F
    """
    p = pressure
    api = oil_gravity
    sg = gas_gravity
    gor = gas_oil_ratio
    
    # Standing's correlation (rearranged for temperature)
    # Simplified iteration approach
    t_guess = 150  # Initial guess
    
    for _ in range(10):  # Simple iteration
        rs_calc = sg * ((p / 18.2) + 1.4) * (10**(0.0125 * api - 0.00091 * t_guess))
        
        if abs(rs_calc - gor) < 1:
            break
        
        # Adjust temperature
        if rs_calc > gor:
            t_guess -= 5
        else:
            t_guess += 5
    
    return t_guess

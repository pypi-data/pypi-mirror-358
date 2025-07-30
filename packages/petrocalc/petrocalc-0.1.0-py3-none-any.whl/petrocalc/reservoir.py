"""
Reservoir engineering calculations.

This module contains functions for reservoir engineering calculations including:
- Reservoir fluid properties
- Material balance equations
- Recovery calculations
- Decline curve analysis
- Well performance
"""

import math
from typing import Union, Tuple, Optional


def oil_formation_volume_factor_standing(
    gas_oil_ratio: float,
    gas_gravity: float, 
    oil_gravity: float,
    temperature: float,
    pressure: float
) -> float:
    """
    Calculates oil formation volume factor using Standing's correlation.
    
    Args:
        gas_oil_ratio (float): Solution gas-oil ratio in scf/STB
        gas_gravity (float): Gas specific gravity (air = 1.0)
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        
    Returns:
        float: Oil formation volume factor in res bbl/STB
    """
    rs = gas_oil_ratio
    gamma_g = gas_gravity
    gamma_o = 141.5 / (oil_gravity + 131.5)  # Convert API to specific gravity
    t = temperature
    p = pressure
    
    # Standing's correlation
    bob = 0.9759 + 0.000120 * (rs * (gamma_g / gamma_o)**0.5 + 1.25 * t)**1.2
    return bob


def gas_formation_volume_factor(temperature: float, pressure: float, z_factor: float = 1.0) -> float:
    """
    Calculates gas formation volume factor.
    
    Args:
        temperature (float): Temperature in °R (°F + 459.67)
        pressure (float): Pressure in psia
        z_factor (float): Gas compressibility factor (dimensionless)
        
    Returns:
        float: Gas formation volume factor in res ft³/scf
    """
    return 0.02827 * z_factor * temperature / pressure


def solution_gas_oil_ratio_standing(
    pressure: float,
    temperature: float,
    gas_gravity: float,
    oil_gravity: float
) -> float:
    """
    Calculates solution gas-oil ratio using Standing's correlation.
    
    Args:
        pressure (float): Pressure in psia
        temperature (float): Temperature in °F
        gas_gravity (float): Gas specific gravity (air = 1.0)
        oil_gravity (float): Oil API gravity in degrees
        
    Returns:
        float: Solution gas-oil ratio in scf/STB
    """
    gamma_g = gas_gravity
    api = oil_gravity
    t = temperature
    p = pressure
    
    # Standing's correlation
    rs = gamma_g * ((p / 18.2) + 1.4) * (10**(0.0125 * api - 0.00091 * t))
    return rs


def bubble_point_pressure_standing(
    gas_oil_ratio: float,
    gas_gravity: float,
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates bubble point pressure using Standing's correlation.
    
    Args:
        gas_oil_ratio (float): Solution gas-oil ratio in scf/STB
        gas_gravity (float): Gas specific gravity (air = 1.0)
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        
    Returns:
        float: Bubble point pressure in psia
    """
    rs = gas_oil_ratio
    gamma_g = gas_gravity
    api = oil_gravity
    t = temperature
    
    # Standing's correlation
    pb = 18.2 * ((rs / gamma_g)**0.83 * 10**(0.00091 * t - 0.0125 * api) - 1.4)
    return pb


def oil_viscosity_beggs_robinson(
    oil_gravity: float,
    temperature: float,
    pressure: float,
    gas_oil_ratio: float = 0
) -> float:
    """
    Calculates oil viscosity using Beggs-Robinson correlation.
    
    Args:
        oil_gravity (float): Oil API gravity in degrees
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        gas_oil_ratio (float): Solution gas-oil ratio in scf/STB
        
    Returns:
        float: Oil viscosity in cp
    """
    api = oil_gravity
    t = temperature
    rs = gas_oil_ratio
    
    # Dead oil viscosity
    x = t**(-1.163)
    y = 10**(3.0324 - 0.02023 * api) * x
    mu_od = 10**y - 1
    
    # Live oil viscosity
    if rs > 0:
        a = 10.715 * (rs + 100)**(-0.515)
        b = 5.44 * (rs + 150)**(-0.338)
        mu_o = a * mu_od**b
    else:
        mu_o = mu_od
    
    return mu_o


def gas_viscosity_lee(
    molecular_weight: float,
    temperature: float,
    pressure: float,
    specific_gravity: float
) -> float:
    """
    Calculates gas viscosity using Lee correlation.
    
    Args:
        molecular_weight (float): Gas molecular weight in lb/lb-mol
        temperature (float): Temperature in °R
        pressure (float): Pressure in psia
        specific_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        float: Gas viscosity in cp
    """
    mw = molecular_weight
    t = temperature
    p = pressure
    sg = specific_gravity
    
    # Gas density
    rho_g = (p * mw) / (10.732 * t)  # lb/ft³
    
    # Lee correlation
    k = ((9.379 + 0.01607 * mw) * t**1.5) / (209.2 + 19.26 * mw + t)
    x = 3.448 + (986.4 / t) + 0.01009 * mw
    y = 2.447 - 0.2224 * x
    
    mu_g = k * math.exp(x * (rho_g / 62.428)**y) / 10000
    return mu_g


def material_balance_oil_reservoir(
    initial_oil_in_place: float,
    cumulative_oil_production: float,
    cumulative_gas_production: float,
    cumulative_water_production: float,
    initial_formation_volume_factor: float,
    current_formation_volume_factor: float,
    initial_solution_gor: float,
    current_solution_gor: float,
    gas_formation_volume_factor: float
) -> float:
    """
    Calculates current reservoir pressure using material balance equation.
    
    Args:
        initial_oil_in_place (float): Initial oil in place in STB
        cumulative_oil_production (float): Cumulative oil production in STB
        cumulative_gas_production (float): Cumulative gas production in scf
        cumulative_water_production (float): Cumulative water production in STB
        initial_formation_volume_factor (float): Initial oil FVF in res bbl/STB
        current_formation_volume_factor (float): Current oil FVF in res bbl/STB
        initial_solution_gor (float): Initial solution GOR in scf/STB
        current_solution_gor (float): Current solution GOR in scf/STB
        gas_formation_volume_factor (float): Gas FVF in res ft³/scf
        
    Returns:
        float: Remaining oil in reservoir in STB
    """
    n = initial_oil_in_place
    np = cumulative_oil_production
    gp = cumulative_gas_production
    wp = cumulative_water_production
    boi = initial_formation_volume_factor
    bo = current_formation_volume_factor
    rsi = initial_solution_gor
    rs = current_solution_gor
    bg = gas_formation_volume_factor
    
    # Simplified material balance (no water influx, no gas cap)
    remaining_oil = n - np - (gp - np * rs) * (bg / 5.615) / (bo - rsi * bg / 5.615)
    return remaining_oil


def arps_decline_curve(
    initial_rate: float,
    time: float,
    decline_rate: float,
    decline_exponent: float = 1.0
) -> float:
    """
    Calculates production rate using Arps decline curve equation.
    
    Args:
        initial_rate (float): Initial production rate
        time (float): Time period
        decline_rate (float): Initial decline rate (1/time)
        decline_exponent (float): Decline exponent (b-factor)
        
    Returns:
        float: Production rate at given time
    """
    qi = initial_rate
    t = time
    di = decline_rate
    b = decline_exponent
    
    if b == 0:  # Exponential decline
        q = qi * math.exp(-di * t)
    else:  # Hyperbolic decline
        q = qi / (1 + b * di * t)**(1/b)
    
    return q


def cumulative_production_arps(
    initial_rate: float,
    time: float,
    decline_rate: float,
    decline_exponent: float = 1.0
) -> float:
    """
    Calculates cumulative production using Arps decline curve.
    
    Args:
        initial_rate (float): Initial production rate
        time (float): Time period
        decline_rate (float): Initial decline rate (1/time)
        decline_exponent (float): Decline exponent (b-factor)
        
    Returns:
        float: Cumulative production at given time
    """
    qi = initial_rate
    t = time
    di = decline_rate
    b = decline_exponent
    
    if abs(b) < 1e-6:  # Exponential decline (b ≈ 0)
        if di == 0:
            qcum = qi * t  # Constant rate
        else:
            qcum = (qi / di) * (1 - math.exp(-di * t))
    elif abs(b - 1.0) < 1e-6:  # Harmonic decline (b = 1)
        qcum = (qi / di) * math.log(1 + di * t)
    else:  # Hyperbolic decline
        if di == 0:
            qcum = qi * t  # Constant rate
        else:
            qcum = (qi / ((1 - b) * di)) * (1 - (1 + b * di * t)**(1 - 1/b))
    
    return qcum


def recovery_factor_waterflooding(
    initial_water_saturation: float,
    residual_oil_saturation: float,
    porosity: float,
    sweep_efficiency: float
) -> float:
    """
    Calculates oil recovery factor for waterflooding.
    
    Args:
        initial_water_saturation (float): Initial water saturation (fraction)
        residual_oil_saturation (float): Residual oil saturation (fraction)
        porosity (float): Porosity (fraction)
        sweep_efficiency (float): Sweep efficiency (fraction)
        
    Returns:
        float: Recovery factor (fraction)
    """
    swi = initial_water_saturation
    sor = residual_oil_saturation
    phi = porosity
    es = sweep_efficiency
    
    # Volumetric sweep efficiency
    ed = 1 - swi - sor  # Displacement efficiency
    recovery_factor = ed * es
    
    return recovery_factor

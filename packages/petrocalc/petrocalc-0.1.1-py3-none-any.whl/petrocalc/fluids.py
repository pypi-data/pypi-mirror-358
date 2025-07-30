"""
Fluid properties calculations.

This module contains functions for calculating fluid properties including:
- PVT properties of oil, gas, and water
- Fluid correlations and equations of state
- Phase behavior calculations
- Thermodynamic properties
"""

import math
from typing import Union, Tuple, Optional


def water_formation_volume_factor(
    temperature: float,
    pressure: float,
    salinity: float = 0
) -> float:
    """
    Calculates water formation volume factor.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0 for fresh water)
        
    Returns:
        float: Water formation volume factor in res bbl/STB
    """
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert ppm to fraction
    
    # McCain correlation
    dvwt = -1.0001e-2 + 1.33391e-4 * t + 5.50654e-7 * t**2
    dvwp = -1.95301e-9 * p * t - 1.72834e-13 * p**2 * t - 3.58922e-7 * p - 2.25341e-10 * p**2
    dvws = s * (0.0816 - 0.0122 * s + 0.000128 * s**2)
    
    bw = 1 + dvwt + dvwp + dvws
    return bw


def water_compressibility(
    temperature: float,
    pressure: float,
    salinity: float = 0
) -> float:
    """
    Calculates water compressibility.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0)
        
    Returns:
        float: Water compressibility in 1/psi
    """
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert to fraction
    
    # Osif correlation
    cw = (1 / (7.033 * p + 541.5 * s - 537.0 * t + 403300)) * 1e-6
    return cw


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


def water_viscosity(temperature: float, pressure: float, salinity: float = 0) -> float:
    """
    Calculates water viscosity.
    
    Args:
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0)
        
    Returns:
        float: Water viscosity in cp
    """
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert to fraction
    
    # McCain correlation for fresh water viscosity
    # Adjusted correlation to ensure positive values
    if t < 32:
        t = 32  # Prevent calculations below freezing
    
    # Simplified correlation for water viscosity
    mu_w = 1.0 - 0.0035 * (t - 32) + 0.000005 * (t - 32)**2
    
    # Ensure minimum viscosity
    mu_w = max(0.1, mu_w)
    
    # Salinity correction
    if s > 0:
        salinity_factor = 1 + s * 10  # Simplified salinity effect
        mu_w = mu_w * salinity_factor
    
    # Pressure correction (simplified)
    mu_w = mu_w * (1 + 0.000001 * (p - 14.7))
    
    return mu_w


def gas_compressibility_factor_standing(
    pressure: float,
    temperature: float,
    gas_gravity: float
) -> float:
    """
    Calculates gas compressibility factor using Standing-Katz correlation.
    
    Args:
        pressure (float): Pressure in psia
        temperature (float): Temperature in °R
        gas_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        float: Gas compressibility factor (dimensionless)
    """
    sg = gas_gravity
    t = temperature
    p = pressure
    
    # Calculate pseudocritical properties
    tpc = 168 + 325 * sg - 12.5 * sg**2  # °R
    ppc = 677 + 15.0 * sg - 37.5 * sg**2  # psia
    
    # Calculate pseudoreduced properties
    tpr = t / tpc
    ppr = p / ppc
    
    # Standing-Katz correlation (simplified approximation)
    a = 1.39 * (tpr - 0.92)**0.5 - 0.36 * tpr - 0.101
    b = (0.62 - 0.23 * tpr) * ppr + ((0.066 / (tpr - 0.86)) - 0.037) * ppr**2 + (0.32 * ppr**6) / (10**(9 * (tpr - 1)))
    c = 0.132 - 0.32 * math.log10(tpr)
    d = 10**(0.3106 - 0.49 * tpr + 0.1824 * tpr**2)
    
    z = a + (1 - a) / math.exp(b) + c * ppr**d
    
    return max(0.2, min(2.0, z))  # Practical bounds


def gas_density(
    pressure: float,
    temperature: float,
    molecular_weight: float,
    z_factor: float = 1.0
) -> float:
    """
    Calculates gas density using equation of state.
    
    Args:
        pressure (float): Pressure in psia
        temperature (float): Temperature in °R
        molecular_weight (float): Gas molecular weight in lb/lb-mol
        z_factor (float): Gas compressibility factor (dimensionless)
        
    Returns:
        float: Gas density in lb/ft³
    """
    p = pressure
    t = temperature
    mw = molecular_weight
    z = z_factor
    
    # Ideal gas law with compressibility factor
    rho_g = (p * mw) / (10.732 * z * t)
    return rho_g


def oil_density(
    oil_gravity: float,
    gas_gravity: float,
    solution_gor: float,
    temperature: float,
    pressure: float
) -> float:
    """
    Calculates oil density at reservoir conditions.
    
    Args:
        oil_gravity (float): Stock tank oil gravity in °API
        gas_gravity (float): Gas specific gravity (air = 1.0)
        solution_gor (float): Solution gas-oil ratio in scf/STB
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        
    Returns:
        float: Oil density in lb/ft³
    """
    api = oil_gravity
    sg_g = gas_gravity
    rs = solution_gor
    t = temperature
    p = pressure
    
    # Stock tank oil density
    sg_o = 141.5 / (api + 131.5)
    rho_o_std = sg_o * 62.428  # lb/ft³ at standard conditions
    
    # Standing correlation for live oil density
    rho_o = rho_o_std + 0.00277 * rs * sg_g - 1.71e-7 * rs**2 * sg_g**2
    
    # Temperature correction (simplified)
    rho_o = rho_o * (1 - 3.5e-4 * (t - 60))
    
    return rho_o


def surface_tension_oil_gas(
    oil_gravity: float,
    gas_gravity: float,
    temperature: float,
    pressure: float
) -> float:
    """
    Calculates surface tension between oil and gas phases.
    
    Args:
        oil_gravity (float): Oil gravity in °API
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        
    Returns:
        float: Surface tension in dynes/cm
    """
    api = oil_gravity
    sg_g = gas_gravity
    t = temperature
    p = pressure
    
    # Baker and Swerdloff correlation
    sigma_68 = 39.0 - 0.2571 * api  # Surface tension at 68°F
    sigma_t = sigma_68 * ((t + 459.67) / 527.67)**(-1.25)  # Temperature correction
    
    # Pressure correction (simplified)
    sigma = sigma_t * (1 - 0.024 * math.sqrt(p / 1000))
    
    return max(0, sigma)


def interfacial_tension_oil_water(
    oil_gravity: float,
    temperature: float,
    pressure: float,
    salinity: float = 0
) -> float:
    """
    Calculates interfacial tension between oil and water phases.
    
    Args:
        oil_gravity (float): Oil gravity in °API
        temperature (float): Temperature in °F
        pressure (float): Pressure in psia
        salinity (float): Water salinity in ppm (default 0)
        
    Returns:
        float: Interfacial tension in dynes/cm
    """
    api = oil_gravity
    t = temperature
    p = pressure
    s = salinity / 1000000  # Convert to fraction
    
    # Correlation based on oil gravity and temperature
    sigma_ow = 35.0 - 0.2 * api + 0.001 * (t - 60)**2
    
    # Salinity effect
    if s > 0:
        sigma_ow = sigma_ow * (1 + 0.1 * s)
    
    # Pressure effect (minimal for oil-water)
    sigma_ow = sigma_ow * (1 - 0.001 * (p - 14.7) / 1000)
    
    return max(0, sigma_ow)


def critical_properties_gas(gas_gravity: float) -> Tuple[float, float]:
    """
    Estimates critical temperature and pressure for natural gas.
    
    Args:
        gas_gravity (float): Gas specific gravity (air = 1.0)
        
    Returns:
        tuple: (critical_temperature_R, critical_pressure_psia)
    """
    sg = gas_gravity
    
    # Standing correlations for natural gas
    tc = 168 + 325 * sg - 12.5 * sg**2  # °R
    pc = 677 + 15.0 * sg - 37.5 * sg**2  # psia
    
    return tc, pc


def vapor_pressure_oil(
    oil_gravity: float,
    temperature: float
) -> float:
    """
    Calculates vapor pressure of oil using Riedel equation.
    
    Args:
        oil_gravity (float): Oil gravity in °API
        temperature (float): Temperature in °F
        
    Returns:
        float: Vapor pressure in psia
    """
    api = oil_gravity
    t = temperature + 459.67  # Convert to °R
    
    # Estimate critical temperature for oil
    tc = 1166.0 - 3.0 * api  # °R (approximate)
    
    # Simplified Riedel equation
    tr = t / tc
    if tr >= 1.0:
        return 14.7  # Assume atmospheric pressure at critical point
    
    # Antoine equation (simplified)
    a = 8.0 - 0.01 * api
    b = 1500 + 10 * api
    
    pv = math.exp(a - b / t) * 14.7  # psia
    
    return max(0, pv)

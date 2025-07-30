"""
Pressure calculations and analysis.

This module contains functions for pressure-related calculations including:
- Hydrostatic and formation pressures
- Pressure gradient calculations
- Well control calculations
- Kick analysis and well control
"""

import math
from typing import Union, Tuple, Optional


def formation_pressure_gradient(
    formation_water_density: float,
    salinity: float = 100000,
    temperature: float = 150
) -> float:
    """
    Calculates formation pressure gradient.
    
    Args:
        formation_water_density (float): Formation water density in lb/ft³
        salinity (float): Water salinity in ppm (default 100,000)
        temperature (float): Formation temperature in °F (default 150)
        
    Returns:
        float: Formation pressure gradient in psi/ft
    """
    rho_w = formation_water_density
    
    # Convert density to pressure gradient
    pressure_gradient = rho_w / 144  # psi/ft
    
    return pressure_gradient


def overburden_pressure_gradient(depth: float, surface_density: float = 18.0) -> float:
    """
    Calculates overburden pressure gradient.
    
    Args:
        depth (float): Depth in ft
        surface_density (float): Average surface density in lb/ft³ (default 18.0)
        
    Returns:
        float: Overburden pressure gradient in psi/ft
    """
    # Typical overburden gradient increases with depth
    if depth < 1000:
        gradient = 0.8 + 0.15 * (depth / 1000)
    else:
        gradient = 0.95 + 0.05 * ((depth - 1000) / 9000)
    
    return min(1.1, gradient)  # Cap at 1.1 psi/ft


def fracture_pressure_gradient(
    overburden_gradient: float,
    pore_pressure_gradient: float,
    poisson_ratio: float = 0.25
) -> float:
    """
    Calculates fracture pressure gradient using Eaton's method.
    
    Args:
        overburden_gradient (float): Overburden pressure gradient in psi/ft
        pore_pressure_gradient (float): Pore pressure gradient in psi/ft
        poisson_ratio (float): Poisson's ratio (default 0.25)
        
    Returns:
        float: Fracture pressure gradient in psi/ft
    """
    s_ob = overburden_gradient
    s_pp = pore_pressure_gradient
    nu = poisson_ratio
    
    # Eaton's correlation
    k = nu / (1 - nu)
    fracture_gradient = k * (s_ob - s_pp) + s_pp
    
    return fracture_gradient


def equivalent_mud_weight(pressure: float, depth: float) -> float:
    """
    Calculates equivalent mud weight from pressure and depth.
    
    Args:
        pressure (float): Pressure in psi
        depth (float): Depth in ft
        
    Returns:
        float: Equivalent mud weight in ppg
    """
    if depth <= 0:
        raise ValueError("Depth must be positive")
    
    emw = pressure / (0.052 * depth)
    return emw


def kick_tolerance(
    casing_shoe_depth: float,
    formation_pressure: float,
    fracture_pressure: float,
    current_mud_weight: float
) -> float:
    """
    Calculates kick tolerance for well control.
    
    Args:
        casing_shoe_depth (float): Casing shoe depth in ft
        formation_pressure (float): Formation pressure in psi
        fracture_pressure (float): Fracture pressure at shoe in psi
        current_mud_weight (float): Current mud weight in ppg
        
    Returns:
        float: Kick tolerance in ppg equivalent
    """
    d_shoe = casing_shoe_depth
    p_form = formation_pressure
    p_frac = fracture_pressure
    mw_current = current_mud_weight
    
    # Maximum allowable surface pressure
    p_max_surface = p_frac - (mw_current * 0.052 * d_shoe)
    
    # Kick tolerance
    kt = p_max_surface / (0.052 * d_shoe)
    
    return kt


def kill_mud_weight(
    original_mud_weight: float,
    shut_in_drillpipe_pressure: float,
    true_vertical_depth: float
) -> float:
    """
    Calculates kill mud weight for well control.
    
    Args:
        original_mud_weight (float): Original mud weight in ppg
        shut_in_drillpipe_pressure (float): SIDPP in psi
        true_vertical_depth (float): True vertical depth in ft
        
    Returns:
        float: Kill mud weight in ppg
    """
    mw_orig = original_mud_weight
    sidpp = shut_in_drillpipe_pressure
    tvd = true_vertical_depth
    
    if tvd <= 0:
        raise ValueError("True vertical depth must be positive")
    
    # Kill mud weight calculation
    kmw = mw_orig + (sidpp / (0.052 * tvd))
    
    return kmw


def initial_circulating_pressure(
    shut_in_drillpipe_pressure: float,
    slow_pump_rate_pressure: float
) -> float:
    """
    Calculates initial circulating pressure for well control.
    
    Args:
        shut_in_drillpipe_pressure (float): SIDPP in psi
        slow_pump_rate_pressure (float): Slow pump rate pressure in psi
        
    Returns:
        float: Initial circulating pressure in psi
    """
    sidpp = shut_in_drillpipe_pressure
    spr = slow_pump_rate_pressure
    
    icp = sidpp + spr
    return icp


def final_circulating_pressure(
    slow_pump_rate_pressure: float,
    original_mud_weight: float,
    kill_mud_weight: float
) -> float:
    """
    Calculates final circulating pressure for well control.
    
    Args:
        slow_pump_rate_pressure (float): Slow pump rate pressure in psi
        original_mud_weight (float): Original mud weight in ppg
        kill_mud_weight (float): Kill mud weight in ppg
        
    Returns:
        float: Final circulating pressure in psi
    """
    spr = slow_pump_rate_pressure
    mw_orig = original_mud_weight
    mw_kill = kill_mud_weight
    
    if mw_orig <= 0:
        raise ValueError("Original mud weight must be positive")
    
    fcp = spr * (mw_kill / mw_orig)**2
    return fcp


def maximum_allowable_annular_surface_pressure(
    fracture_pressure: float,
    mud_weight: float,
    shoe_depth: float
) -> float:
    """
    Calculates maximum allowable annular surface pressure.
    
    Args:
        fracture_pressure (float): Fracture pressure at shoe in psi
        mud_weight (float): Current mud weight in ppg
        shoe_depth (float): Shoe depth in ft
        
    Returns:
        float: MAASP in psi
    """
    p_frac = fracture_pressure
    mw = mud_weight
    d_shoe = shoe_depth
    
    # Hydrostatic pressure at shoe
    p_hydro = mw * 0.052 * d_shoe
    
    # MAASP
    maasp = p_frac - p_hydro
    
    return max(0, maasp)


def pit_gain_calculation(
    kick_volume: float,
    formation_gas_gradient: float = 0.1,
    mud_gradient: float = 0.45
) -> float:
    """
    Calculates pit gain during gas kick migration.
    
    Args:
        kick_volume (float): Original kick volume in bbls
        formation_gas_gradient (float): Gas gradient in psi/ft (default 0.1)
        mud_gradient (float): Mud gradient in psi/ft (default 0.45)
        
    Returns:
        float: Expected pit gain in bbls
    """
    v_kick = kick_volume
    grad_gas = formation_gas_gradient
    grad_mud = mud_gradient
    
    # Gas expansion factor (simplified)
    expansion_factor = grad_mud / grad_gas
    
    # Pit gain
    pit_gain = v_kick * (expansion_factor - 1)
    
    return pit_gain


def pump_pressure_schedule(
    initial_circulating_pressure: float,
    final_circulating_pressure: float,
    total_pump_strokes: float,
    current_stroke: float
) -> float:
    """
    Calculates pump pressure for kill operation.
    
    Args:
        initial_circulating_pressure (float): ICP in psi
        final_circulating_pressure (float): FCP in psi
        total_pump_strokes (float): Total pump strokes to circulate
        current_stroke (float): Current pump stroke number
        
    Returns:
        float: Required pump pressure in psi
    """
    icp = initial_circulating_pressure
    fcp = final_circulating_pressure
    total_strokes = total_pump_strokes
    current = current_stroke
    
    if total_strokes <= 0:
        raise ValueError("Total pump strokes must be positive")
    
    # Linear pressure reduction
    pressure = icp - (icp - fcp) * (current / total_strokes)
    
    return pressure


def lost_circulation_pressure(
    formation_pressure: float,
    hydrostatic_pressure: float,
    safety_margin: float = 50
) -> float:
    """
    Calculates pressure at which lost circulation may occur.
    
    Args:
        formation_pressure (float): Formation pressure in psi
        hydrostatic_pressure (float): Hydrostatic pressure in psi
        safety_margin (float): Safety margin in psi (default 50)
        
    Returns:
        float: Lost circulation pressure in psi
    """
    p_form = formation_pressure
    p_hydro = hydrostatic_pressure
    margin = safety_margin
    
    # Lost circulation occurs when pressure exceeds formation strength
    lc_pressure = p_form + margin
    
    return lc_pressure

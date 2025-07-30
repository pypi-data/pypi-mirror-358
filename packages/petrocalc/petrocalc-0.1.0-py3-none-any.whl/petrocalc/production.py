"""
Production engineering calculations.

This module contains functions for production engineering calculations including:
- Well performance and inflow performance
- Artificial lift calculations
- Nodal analysis
- Well testing analysis
- Flow through chokes and restrictions
"""

import math
from typing import Union, Tuple, Optional


def vogel_ipr(
    reservoir_pressure: float,
    bottomhole_pressure: float,
    maximum_oil_rate: float
) -> float:
    """
    Calculates oil production rate using Vogel's IPR correlation.
    
    Args:
        reservoir_pressure (float): Reservoir pressure in psia
        bottomhole_pressure (float): Bottomhole flowing pressure in psia
        maximum_oil_rate (float): Maximum oil rate at zero bottomhole pressure in STB/day
        
    Returns:
        float: Oil production rate in STB/day
    """
    pr = reservoir_pressure
    pwf = bottomhole_pressure
    qmax = maximum_oil_rate
    
    # Vogel's IPR equation
    q = qmax * (1 - 0.2 * (pwf / pr) - 0.8 * (pwf / pr)**2)
    return max(0, q)  # Ensure non-negative flow rate


def productivity_index(
    flow_rate: float,
    reservoir_pressure: float,
    bottomhole_pressure: float
) -> float:
    """
    Calculates productivity index for a well.
    
    Args:
        flow_rate (float): Production rate in STB/day
        reservoir_pressure (float): Reservoir pressure in psia
        bottomhole_pressure (float): Bottomhole flowing pressure in psia
        
    Returns:
        float: Productivity index in STB/day/psi
    """
    q = flow_rate
    pr = reservoir_pressure
    pwf = bottomhole_pressure
    
    if pr <= pwf:
        raise ValueError("Reservoir pressure must be greater than bottomhole pressure")
    
    pi = q / (pr - pwf)
    return pi


def darcy_radial_flow(
    permeability: float,
    thickness: float,
    pressure_drop: float,
    viscosity: float,
    formation_volume_factor: float,
    wellbore_radius: float,
    drainage_radius: float
) -> float:
    """
    Calculates flow rate using Darcy's equation for radial flow.
    
    Args:
        permeability (float): Formation permeability in md
        thickness (float): Net pay thickness in ft
        pressure_drop (float): Pressure drop in psi
        viscosity (float): Fluid viscosity in cp
        formation_volume_factor (float): Formation volume factor in res bbl/STB
        wellbore_radius (float): Wellbore radius in ft
        drainage_radius (float): Drainage radius in ft
        
    Returns:
        float: Flow rate in STB/day
    """
    k = permeability
    h = thickness
    dp = pressure_drop
    mu = viscosity
    bo = formation_volume_factor
    rw = wellbore_radius
    re = drainage_radius
    
    if re <= rw:
        raise ValueError("Drainage radius must be greater than wellbore radius")
    
    q = (0.00708 * k * h * dp) / (mu * bo * math.log(re / rw))
    return q


def skin_factor(
    actual_productivity_index: float,
    ideal_productivity_index: float
) -> float:
    """
    Calculates skin factor from productivity indices.
    
    Args:
        actual_productivity_index (float): Actual PI in STB/day/psi
        ideal_productivity_index (float): Ideal PI in STB/day/psi
        
    Returns:
        float: Skin factor (dimensionless)
    """
    pi_actual = actual_productivity_index
    pi_ideal = ideal_productivity_index
    
    if pi_actual <= 0 or pi_ideal <= 0:
        raise ValueError("Productivity indices must be positive")
    
    skin = (pi_ideal / pi_actual) - 1
    return skin


def gas_well_deliverability_rawlins_schellhardt(
    absolute_open_flow_potential: float,
    flowing_bottomhole_pressure: float,
    reservoir_pressure: float,
    flow_exponent: float = 0.5
) -> float:
    """
    Calculates gas well deliverability using Rawlins-Schellhardt equation.
    
    Args:
        absolute_open_flow_potential (float): AOF in Mscf/day
        flowing_bottomhole_pressure (float): Flowing BHP in psia
        reservoir_pressure (float): Reservoir pressure in psia
        flow_exponent (float): Flow exponent (n), typically 0.5-1.0
        
    Returns:
        float: Gas flow rate in Mscf/day
    """
    aof = absolute_open_flow_potential
    pwf = flowing_bottomhole_pressure
    pr = reservoir_pressure
    n = flow_exponent
    
    if pr <= pwf:
        raise ValueError("Reservoir pressure must be greater than flowing pressure")
    
    qg = aof * (1 - (pwf / pr)**2)**n
    return qg


def choke_flow_rate_gas(
    upstream_pressure: float,
    downstream_pressure: float,
    choke_diameter: float,
    gas_gravity: float,
    temperature: float,
    discharge_coefficient: float = 0.85
) -> float:
    """
    Calculates gas flow rate through a choke.
    
    Args:
        upstream_pressure (float): Upstream pressure in psia
        downstream_pressure (float): Downstream pressure in psia
        choke_diameter (float): Choke diameter in inches
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Temperature in °R
        discharge_coefficient (float): Discharge coefficient
        
    Returns:
        float: Gas flow rate in Mscf/day
    """
    p1 = upstream_pressure
    p2 = downstream_pressure
    d = choke_diameter
    sg = gas_gravity
    t = temperature
    cd = discharge_coefficient
    
    # Critical pressure ratio
    critical_ratio = 0.55  # Approximate for natural gas
    
    if p2 / p1 < critical_ratio:
        # Critical flow
        qg = 0.0125 * cd * (d**2) * p1 / math.sqrt(sg * t)
    else:
        # Subcritical flow
        qg = 0.0125 * cd * (d**2) * p1 * math.sqrt((p1**2 - p2**2) / (sg * t * p1**2))
    
    return qg * 1000  # Convert to Mscf/day


def multiphase_flow_beggs_brill(
    liquid_rate: float,
    gas_rate: float,
    pipe_diameter: float,
    pipe_inclination: float,
    liquid_density: float,
    gas_density: float,
    liquid_viscosity: float,
    gas_viscosity: float
) -> Tuple[float, float]:
    """
    Calculates pressure gradient using Beggs-Brill correlation.
    
    Args:
        liquid_rate (float): Liquid flow rate in bbl/day
        gas_rate (float): Gas flow rate in Mscf/day
        pipe_diameter (float): Pipe diameter in inches
        pipe_inclination (float): Pipe inclination angle in degrees
        liquid_density (float): Liquid density in lb/ft³
        gas_density (float): Gas density in lb/ft³
        liquid_viscosity (float): Liquid viscosity in cp
        gas_viscosity (float): Gas viscosity in cp
        
    Returns:
        tuple: (pressure_gradient_psi_per_ft, liquid_holdup)
    """
    ql = liquid_rate / 86400  # Convert to ft³/sec
    qg = gas_rate * 1000 / 86400  # Convert to ft³/sec
    d = pipe_diameter / 12  # Convert to ft
    theta = math.radians(pipe_inclination)
    rho_l = liquid_density
    rho_g = gas_density
    mu_l = liquid_viscosity
    mu_g = gas_viscosity
    
    # Calculate superficial velocities
    area = math.pi * d**2 / 4
    vsl = ql / area  # Superficial liquid velocity
    vsg = qg / area  # Superficial gas velocity
    vm = vsl + vsg  # Mixture velocity
    
    # Calculate liquid holdup (simplified)
    lambda_l = vsl / vm if vm > 0 else 0
    
    # Simplified liquid holdup calculation
    if lambda_l < 0.01:
        hl = lambda_l
    else:
        hl = 0.845 * lambda_l**0.351  # Approximate correlation
    
    # Calculate mixture density
    rho_m = hl * rho_l + (1 - hl) * rho_g
    
    # Calculate pressure gradient components
    # Hydrostatic component
    dp_dz_h = rho_m * math.sin(theta) / 144  # psi/ft
    
    # Friction component (simplified)
    rho_ns = lambda_l * rho_l + (1 - lambda_l) * rho_g
    mu_ns = lambda_l * mu_l + (1 - lambda_l) * mu_g
    
    # Reynolds number
    re = rho_ns * vm * d / (mu_ns * 6.72e-4)
    
    # Friction factor (simplified)
    if re < 2100:
        f = 16 / re
    else:
        f = 0.0791 / re**0.25
    
    # Friction pressure gradient
    dp_dz_f = (2 * f * rho_ns * vm**2) / (32.174 * d * 144)
    
    # Total pressure gradient
    dp_dz_total = dp_dz_h + dp_dz_f
    
    return dp_dz_total, hl


def well_test_analysis_horner(
    pressure_data: list,
    time_data: list,
    production_time: float,
    flow_rate: float,
    porosity: float,
    viscosity: float,
    total_compressibility: float,
    formation_volume_factor: float,
    thickness: float
) -> Tuple[float, float]:
    """
    Analyzes well test data using Horner plot method.
    
    Args:
        pressure_data (list): List of pressure measurements in psia
        time_data (list): List of time measurements (shutin time) in hours
        production_time (float): Production time before shutin in hours
        flow_rate (float): Production rate before shutin in STB/day
        porosity (float): Porosity fraction
        viscosity (float): Oil viscosity in cp
        total_compressibility (float): Total compressibility in 1/psi
        formation_volume_factor (float): Formation volume factor in res bbl/STB
        thickness (float): Net pay thickness in ft
        
    Returns:
        tuple: (permeability_md, skin_factor)
    """
    # This is a simplified implementation
    # In practice, you would perform linear regression on Horner plot
    
    if len(pressure_data) != len(time_data):
        raise ValueError("Pressure and time data must have same length")
    
    # Calculate Horner time function
    tp = production_time
    horner_time = [(tp + dt) / dt for dt in time_data]
    
    # Find slope of pressure vs log(horner_time) - simplified
    if len(pressure_data) >= 2:
        p1, p2 = pressure_data[0], pressure_data[-1]
        t1, t2 = horner_time[0], horner_time[-1]
        
        if t2 > t1:
            slope = (p2 - p1) / math.log(t2 / t1)
        else:
            slope = 0
    else:
        slope = 0
    
    # Calculate permeability
    if slope != 0:
        k = (162.6 * flow_rate * viscosity * formation_volume_factor) / (abs(slope) * thickness)
    else:
        k = 0
    
    # Calculate skin (simplified)
    if len(pressure_data) > 0 and slope != 0:
        pi = pressure_data[-1]  # Initial pressure estimate
        p1hr = pressure_data[0] if len(pressure_data) > 0 else pi
        
        skin = 1.151 * ((p1hr - pressure_data[0]) / abs(slope) - math.log(k / (porosity * viscosity * total_compressibility * 0.0002637)) + 3.23)
    else:
        skin = 0
    
    return k, skin

"""
Flow calculations for petroleum engineering.

This module contains functions for flow calculations including:
- Single-phase and multiphase flow
- Flow through pipes and restrictions
- Choke flow calculations
- Flow in porous media
"""

import math
from typing import Union, Tuple, Optional


def moody_friction_factor(reynolds_number: float, relative_roughness: float) -> float:
    """
    Calculates friction factor using Moody chart correlation.
    
    Args:
        reynolds_number (float): Reynolds number (dimensionless)
        relative_roughness (float): Relative roughness (ε/D)
        
    Returns:
        float: Darcy friction factor (dimensionless)
    """
    re = reynolds_number
    roughness = relative_roughness
    
    if re < 2100:
        # Laminar flow
        f = 64 / re
    elif re < 4000:
        # Transition region (interpolation)
        f_lam = 64 / 2100
        f_turb = 0.0791 / (4000**0.25)
        f = f_lam + (f_turb - f_lam) * (re - 2100) / (4000 - 2100)
    else:
        # Turbulent flow - Colebrook-White equation (implicit)
        # Using approximation for computational efficiency
        if roughness == 0:
            # Smooth pipe - Blasius equation
            f = 0.0791 / (re**0.25)
        else:
            # Rough pipe - approximation
            f = 0.25 / (math.log10(roughness/3.7 + 5.74/(re**0.9)))**2
    
    return f


def pressure_drop_horizontal_pipe(
    flow_rate: float,
    pipe_diameter: float,
    pipe_length: float,
    fluid_density: float,
    fluid_viscosity: float,
    pipe_roughness: float = 0.0006
) -> float:
    """
    Calculates pressure drop in horizontal pipe due to friction.
    
    Args:
        flow_rate (float): Flow rate in bbl/day
        pipe_diameter (float): Pipe inner diameter in inches
        pipe_length (float): Pipe length in ft
        fluid_density (float): Fluid density in lb/ft³
        fluid_viscosity (float): Fluid viscosity in cp
        pipe_roughness (float): Pipe roughness in ft (default 0.0006)
        
    Returns:
        float: Pressure drop in psi
    """
    q = flow_rate / 86400  # Convert to ft³/sec
    d = pipe_diameter / 12  # Convert to ft
    l = pipe_length
    rho = fluid_density
    mu = fluid_viscosity
    roughness = pipe_roughness
    
    # Calculate velocity
    area = math.pi * d**2 / 4
    velocity = q / area  # ft/sec
    
    # Reynolds number
    re = rho * velocity * d / (mu * 6.72e-4)  # Convert viscosity units
    
    # Relative roughness
    rel_roughness = roughness / d
    
    # Friction factor
    f = moody_friction_factor(re, rel_roughness)
    
    # Pressure drop (Darcy-Weisbach equation)
    dp = f * (l / d) * (rho * velocity**2) / (2 * 32.174 * 144)  # psi
    
    return dp


def gas_flow_rate_weymouth(
    upstream_pressure: float,
    downstream_pressure: float,
    pipe_diameter: float,
    pipe_length: float,
    gas_gravity: float,
    temperature: float,
    efficiency: float = 1.0
) -> float:
    """
    Calculates gas flow rate using Weymouth equation.
    
    Args:
        upstream_pressure (float): Upstream pressure in psia
        downstream_pressure (float): Downstream pressure in psia
        pipe_diameter (float): Pipe inner diameter in inches
        pipe_length (float): Pipe length in miles
        gas_gravity (float): Gas specific gravity (air = 1.0)
        temperature (float): Average gas temperature in °R
        efficiency (float): Pipeline efficiency factor (default 1.0)
        
    Returns:
        float: Gas flow rate in Mscf/day
    """
    p1 = upstream_pressure
    p2 = downstream_pressure
    d = pipe_diameter
    l = pipe_length
    sg = gas_gravity
    t = temperature
    e = efficiency
    
    # Weymouth equation
    q = 433.5 * e * d**(8/3) * math.sqrt((p1**2 - p2**2) / (sg * t * l))
    
    return q


def oil_flow_rate_hazen_williams(
    pressure_drop: float,
    pipe_diameter: float,
    pipe_length: float,
    hazen_williams_coefficient: float = 120
) -> float:
    """
    Calculates oil flow rate using Hazen-Williams equation.
    
    Args:
        pressure_drop (float): Pressure drop in psi
        pipe_diameter (float): Pipe diameter in inches
        pipe_length (float): Pipe length in ft
        hazen_williams_coefficient (float): Hazen-Williams coefficient (default 120)
        
    Returns:
        float: Flow rate in bbl/day
    """
    dp = pressure_drop
    d = pipe_diameter
    l = pipe_length
    c = hazen_williams_coefficient
    
    # Hazen-Williams equation for oil
    q = 4.52 * c * d**2.63 * (dp / l)**0.54
    
    return q


def critical_flow_velocity(
    liquid_density: float,
    gas_density: float,
    surface_tension: float
) -> float:
    """
    Calculates critical velocity for liquid carryover in gas flow.
    
    Args:
        liquid_density (float): Liquid density in lb/ft³
        gas_density (float): Gas density in lb/ft³
        surface_tension (float): Surface tension in dynes/cm
        
    Returns:
        float: Critical velocity in ft/sec
    """
    rho_l = liquid_density
    rho_g = gas_density
    sigma = surface_tension / 1000  # Convert to lb/ft
    
    # Souders-Brown equation
    k = 0.35  # Typical K-factor for horizontal separators
    vc = k * math.sqrt((rho_l - rho_g) / rho_g)
    
    return vc


def terminal_settling_velocity(
    particle_diameter: float,
    particle_density: float,
    fluid_density: float,
    fluid_viscosity: float
) -> float:
    """
    Calculates terminal settling velocity of particles in fluid.
    
    Args:
        particle_diameter (float): Particle diameter in ft
        particle_density (float): Particle density in lb/ft³
        fluid_density (float): Fluid density in lb/ft³
        fluid_viscosity (float): Fluid viscosity in cp
        
    Returns:
        float: Terminal settling velocity in ft/sec
    """
    dp = particle_diameter
    rho_p = particle_density
    rho_f = fluid_density
    mu = fluid_viscosity * 6.72e-4  # Convert to lb/ft-sec
    
    # Gravity constant
    g = 32.174  # ft/sec²
    
    # Stokes law (for small particles)
    vt = (g * dp**2 * (rho_p - rho_f)) / (18 * mu)
    
    # Check Reynolds number for validity
    re = rho_f * vt * dp / mu
    
    if re > 0.5:
        # Use Newton's law for larger particles
        cd = 0.44  # Drag coefficient for spheres at high Re
        vt = math.sqrt((4 * g * dp * (rho_p - rho_f)) / (3 * cd * rho_f))
    
    return vt


def flow_through_orifice(
    upstream_pressure: float,
    downstream_pressure: float,
    orifice_diameter: float,
    fluid_density: float,
    discharge_coefficient: float = 0.6
) -> float:
    """
    Calculates flow rate through an orifice.
    
    Args:
        upstream_pressure (float): Upstream pressure in psi
        downstream_pressure (float): Downstream pressure in psi
        orifice_diameter (float): Orifice diameter in inches
        fluid_density (float): Fluid density in lb/ft³
        discharge_coefficient (float): Discharge coefficient (default 0.6)
        
    Returns:
        float: Flow rate in bbl/day
    """
    p1 = upstream_pressure * 144  # Convert to psf
    p2 = downstream_pressure * 144
    d = orifice_diameter / 12  # Convert to ft
    rho = fluid_density
    cd = discharge_coefficient
    
    # Orifice equation
    area = math.pi * d**2 / 4
    dp = p1 - p2
    
    if dp <= 0:
        return 0
    
    velocity = cd * math.sqrt(2 * 32.174 * dp / rho)
    q = area * velocity  # ft³/sec
    
    # Convert to bbl/day
    q_bbl_day = q * 86400 / 5.615
    
    return q_bbl_day


def multiphase_flow_pressure_drop(
    liquid_superficial_velocity: float,
    gas_superficial_velocity: float,
    pipe_diameter: float,
    pipe_inclination: float,
    liquid_density: float,
    gas_density: float,
    liquid_viscosity: float,
    gas_viscosity: float,
    surface_tension: float
) -> Tuple[float, float]:
    """
    Calculates pressure drop in multiphase flow using simplified correlation.
    
    Args:
        liquid_superficial_velocity (float): Liquid superficial velocity in ft/sec
        gas_superficial_velocity (float): Gas superficial velocity in ft/sec
        pipe_diameter (float): Pipe diameter in ft
        pipe_inclination (float): Pipe inclination in degrees from horizontal
        liquid_density (float): Liquid density in lb/ft³
        gas_density (float): Gas density in lb/ft³
        liquid_viscosity (float): Liquid viscosity in cp
        gas_viscosity (float): Gas viscosity in cp
        surface_tension (float): Surface tension in dynes/cm
        
    Returns:
        tuple: (pressure_gradient_psi_per_ft, liquid_holdup)
    """
    vsl = liquid_superficial_velocity
    vsg = gas_superficial_velocity
    d = pipe_diameter
    theta = math.radians(pipe_inclination)
    rho_l = liquid_density
    rho_g = gas_density
    mu_l = liquid_viscosity
    mu_g = gas_viscosity
    sigma = surface_tension
    
    # Mixture velocity
    vm = vsl + vsg
    
    # Liquid input holdup
    lambda_l = vsl / vm if vm > 0 else 0
    
    # Simplified liquid holdup correlation
    if lambda_l < 0.01:
        hl = lambda_l
    else:
        # Simplified correlation
        hl = 0.845 * lambda_l**0.5
    
    # Mixture density
    rho_m = hl * rho_l + (1 - hl) * rho_g
    
    # Friction factor calculation
    mu_m = hl * mu_l + (1 - hl) * mu_g
    re = rho_m * vm * d / (mu_m * 6.72e-4)
    
    if re < 2100:
        f = 64 / re
    else:
        f = 0.0791 / re**0.25
    
    # Pressure gradient components
    # Hydrostatic
    dp_dz_h = rho_m * math.sin(theta) / 144
    
    # Friction
    dp_dz_f = 2 * f * rho_m * vm**2 / (32.174 * d * 144)
    
    # Total pressure gradient
    dp_dz_total = dp_dz_h + dp_dz_f
    
    return dp_dz_total, hl


def pump_head_calculation(
    flow_rate: float,
    total_dynamic_head: float,
    pump_efficiency: float = 0.75
) -> float:
    """
    Calculates required pump power.
    
    Args:
        flow_rate (float): Flow rate in bbl/day
        total_dynamic_head (float): Total dynamic head in ft
        pump_efficiency (float): Pump efficiency fraction (default 0.75)
        
    Returns:
        float: Required pump power in hp
    """
    q = flow_rate / 86400  # Convert to ft³/sec
    h = total_dynamic_head
    eff = pump_efficiency
    
    # Specific weight of fluid (assume water)
    gamma = 62.4  # lb/ft³
    
    # Hydraulic power
    power_hydraulic = (gamma * q * h) / 550  # hp
    
    # Brake power
    power_brake = power_hydraulic / eff
    
    return power_brake

"""
Economic calculations for petroleum engineering.

This module contains functions for economic analysis including:
- Net Present Value (NPV) calculations
- Discounted Cash Flow (DCF) analysis
- Economic indicators
- Cost estimation
- Project economics
"""

import math
from typing import Union, Tuple, Optional, List


def net_present_value(
    cash_flows: List[float],
    discount_rate: float,
    initial_investment: float = 0
) -> float:
    """
    Calculates Net Present Value (NPV) of a project.
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        discount_rate (float): Discount rate as decimal (e.g., 0.1 for 10%)
        initial_investment (float): Initial investment (default 0)
        
    Returns:
        float: Net Present Value
    """
    npv = -initial_investment
    
    for i, cash_flow in enumerate(cash_flows):
        npv += cash_flow / (1 + discount_rate)**(i + 1)
    
    return npv


def internal_rate_of_return(
    cash_flows: List[float],
    initial_investment: float,
    tolerance: float = 0.001
) -> float:
    """
    Calculates Internal Rate of Return (IRR) using iterative method.
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        initial_investment (float): Initial investment
        tolerance (float): Tolerance for convergence (default 0.001)
        
    Returns:
        float: Internal Rate of Return as decimal
    """
    # Initial guess
    irr_low = 0.0
    irr_high = 1.0
    
    # Find an upper bound where NPV is negative
    while net_present_value(cash_flows, irr_high, initial_investment) > 0:
        irr_high *= 2
        if irr_high > 10:  # Prevent infinite loop
            return float('nan')
    
    # Bisection method
    for _ in range(100):  # Maximum iterations
        irr_mid = (irr_low + irr_high) / 2
        npv_mid = net_present_value(cash_flows, irr_mid, initial_investment)
        
        if abs(npv_mid) < tolerance:
            return irr_mid
        
        if npv_mid > 0:
            irr_low = irr_mid
        else:
            irr_high = irr_mid
    
    return irr_mid


def discounted_payback_period(
    cash_flows: List[float],
    discount_rate: float,
    initial_investment: float
) -> float:
    """
    Calculates discounted payback period.
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        discount_rate (float): Discount rate as decimal
        initial_investment (float): Initial investment
        
    Returns:
        float: Discounted payback period in years
    """
    cumulative_pv = -initial_investment
    
    for i, cash_flow in enumerate(cash_flows):
        pv_cash_flow = cash_flow / (1 + discount_rate)**(i + 1)
        cumulative_pv += pv_cash_flow
        
        if cumulative_pv >= 0:
            # Interpolate to find exact payback period
            previous_cumulative = cumulative_pv - pv_cash_flow
            fraction = -previous_cumulative / pv_cash_flow
            return i + 1 + fraction
    
    return float('inf')  # Never pays back


def profitability_index(
    cash_flows: List[float],
    discount_rate: float,
    initial_investment: float
) -> float:
    """
    Calculates Profitability Index (PI).
    
    Args:
        cash_flows (List[float]): List of annual cash flows
        discount_rate (float): Discount rate as decimal
        initial_investment (float): Initial investment
        
    Returns:
        float: Profitability Index
    """
    if initial_investment == 0:
        return float('inf')
    
    pv_cash_flows = sum(cf / (1 + discount_rate)**(i + 1) for i, cf in enumerate(cash_flows))
    
    return pv_cash_flows / initial_investment


def oil_revenue_calculation(
    production_rate: float,
    oil_price: float,
    royalty_rate: float = 0.125,
    operating_cost_per_barrel: float = 15
) -> float:
    """
    Calculates annual oil revenue.
    
    Args:
        production_rate (float): Oil production rate in bbl/day
        oil_price (float): Oil price in $/bbl
        royalty_rate (float): Royalty rate as decimal (default 12.5%)
        operating_cost_per_barrel (float): Operating cost in $/bbl (default 15)
        
    Returns:
        float: Annual net revenue in $
    """
    annual_production = production_rate * 365
    gross_revenue = annual_production * oil_price
    royalty = gross_revenue * royalty_rate
    operating_costs = annual_production * operating_cost_per_barrel
    
    net_revenue = gross_revenue - royalty - operating_costs
    
    return net_revenue


def gas_revenue_calculation(
    production_rate: float,
    gas_price: float,
    royalty_rate: float = 0.125,
    operating_cost_per_mcf: float = 1.5
) -> float:
    """
    Calculates annual gas revenue.
    
    Args:
        production_rate (float): Gas production rate in Mscf/day
        gas_price (float): Gas price in $/Mscf
        royalty_rate (float): Royalty rate as decimal (default 12.5%)
        operating_cost_per_mcf (float): Operating cost in $/Mscf (default 1.5)
        
    Returns:
        float: Annual net revenue in $
    """
    annual_production = production_rate * 365
    gross_revenue = annual_production * gas_price
    royalty = gross_revenue * royalty_rate
    operating_costs = annual_production * operating_cost_per_mcf
    
    net_revenue = gross_revenue - royalty - operating_costs
    
    return net_revenue


def drilling_cost_estimation(
    well_depth: float,
    hole_diameter: float,
    day_rate: float = 25000,
    drilling_days_per_1000ft: float = 2.5
) -> float:
    """
    Estimates drilling cost for a well.
    
    Args:
        well_depth (float): Well depth in ft
        hole_diameter (float): Average hole diameter in inches
        day_rate (float): Rig day rate in $/day (default 25,000)
        drilling_days_per_1000ft (float): Drilling days per 1000 ft (default 2.5)
        
    Returns:
        float: Estimated drilling cost in $
    """
    drilling_days = (well_depth / 1000) * drilling_days_per_1000ft
    
    # Complexity factor based on diameter
    if hole_diameter > 12:
        complexity_factor = 1.3
    elif hole_diameter > 8:
        complexity_factor = 1.1
    else:
        complexity_factor = 1.0
    
    drilling_cost = drilling_days * day_rate * complexity_factor
    
    return drilling_cost


def completion_cost_estimation(
    well_depth: float,
    completion_type: str = "conventional",
    number_of_stages: int = 1
) -> float:
    """
    Estimates completion cost for a well.
    
    Args:
        well_depth (float): Well depth in ft
        completion_type (str): Type of completion ("conventional", "hydraulic_fracturing")
        number_of_stages (int): Number of fracturing stages (default 1)
        
    Returns:
        float: Estimated completion cost in $
    """
    base_cost = well_depth * 50  # $50 per foot base cost
    
    if completion_type.lower() == "hydraulic_fracturing":
        frac_cost = number_of_stages * 150000  # $150k per stage
        total_cost = base_cost + frac_cost
    else:
        total_cost = base_cost
    
    return total_cost


def abandonment_cost_estimation(well_depth: float, offshore: bool = False) -> float:
    """
    Estimates well abandonment cost.
    
    Args:
        well_depth (float): Well depth in ft
        offshore (bool): Whether well is offshore (default False)
        
    Returns:
        float: Estimated abandonment cost in $
    """
    base_cost = well_depth * 25  # $25 per foot
    
    if offshore:
        base_cost *= 3  # Offshore factor
    
    # Minimum abandonment cost
    return max(100000, base_cost)


def break_even_oil_price(
    initial_investment: float,
    annual_production: float,
    operating_cost_per_barrel: float,
    royalty_rate: float = 0.125,
    discount_rate: float = 0.1,
    project_life: int = 20
) -> float:
    """
    Calculates break-even oil price for a project.
    
    Args:
        initial_investment (float): Initial investment in $
        annual_production (float): Annual oil production in bbl
        operating_cost_per_barrel (float): Operating cost in $/bbl
        royalty_rate (float): Royalty rate as decimal (default 12.5%)
        discount_rate (float): Discount rate as decimal (default 10%)
        project_life (int): Project life in years (default 20)
        
    Returns:
        float: Break-even oil price in $/bbl
    """
    # Present value of operating costs
    pv_operating_costs = sum(
        annual_production * operating_cost_per_barrel / (1 + discount_rate)**i
        for i in range(1, project_life + 1)
    )
    
    # Present value of production (without price)
    pv_production = sum(
        annual_production * (1 - royalty_rate) / (1 + discount_rate)**i
        for i in range(1, project_life + 1)
    )
    
    # Break-even price
    break_even_price = (initial_investment + pv_operating_costs) / pv_production
    
    return break_even_price


def decline_curve_economics(
    initial_rate: float,
    decline_rate: float,
    oil_price: float,
    operating_cost_per_barrel: float,
    discount_rate: float = 0.1,
    project_life: int = 20
) -> Tuple[float, float]:
    """
    Calculates economics for a well with exponential decline.
    
    Args:
        initial_rate (float): Initial production rate in bbl/day
        decline_rate (float): Annual decline rate as decimal
        oil_price (float): Oil price in $/bbl
        operating_cost_per_barrel (float): Operating cost in $/bbl
        discount_rate (float): Discount rate as decimal (default 10%)
        project_life (int): Project life in years (default 20)
        
    Returns:
        tuple: (total_production, present_value_revenue)
    """
    total_production = 0
    pv_revenue = 0
    
    for year in range(1, project_life + 1):
        # Production rate at end of year (exponential decline)
        rate = initial_rate * math.exp(-decline_rate * year)
        
        # Average rate during the year
        avg_rate = initial_rate * (1 - math.exp(-decline_rate)) / decline_rate * math.exp(-decline_rate * (year - 1))
        
        # Annual production
        annual_production = avg_rate * 365
        total_production += annual_production
        
        # Annual revenue
        annual_revenue = annual_production * (oil_price - operating_cost_per_barrel)
        
        # Present value of annual revenue
        pv_annual_revenue = annual_revenue / (1 + discount_rate)**year
        pv_revenue += pv_annual_revenue
    
    return total_production, pv_revenue


def tax_calculation(
    gross_income: float,
    depletion_allowance: float = 0.15,
    corporate_tax_rate: float = 0.21
) -> float:
    """
    Calculates taxes for oil and gas operations.
    
    Args:
        gross_income (float): Gross income in $
        depletion_allowance (float): Depletion allowance rate (default 15%)
        corporate_tax_rate (float): Corporate tax rate (default 21%)
        
    Returns:
        float: Tax amount in $
    """
    depletion = gross_income * depletion_allowance
    taxable_income = gross_income - depletion
    
    tax = taxable_income * corporate_tax_rate
    
    return max(0, tax)

# PetroCalc

A comprehensive Python library for petroleum engineering calculations, providing modules for various aspects of petroleum engineering including drilling, reservoir engineering, production, fluid properties, and economic analysis.

## Features

PetroCalc includes the following modules:

### 🔧 **Drilling** (`petrocalc.drilling`)
- Mud weight and pressure calculations
- Hydraulic calculations
- Hole cleaning and cuttings transport
- Torque and drag calculations
- Wellbore stability analysis

### 🏭 **Reservoir Engineering** (`petrocalc.reservoir`)
- PVT properties correlations
- Material balance equations
- Decline curve analysis
- Recovery factor calculations
- Fluid property correlations (Standing, Beggs-Robinson, etc.)

### ⚡ **Production Engineering** (`petrocalc.production`)
- Inflow Performance Relationships (IPR)
- Well performance analysis
- Artificial lift calculations
- Multiphase flow calculations
- Well testing analysis

### 💧 **Fluid Properties** (`petrocalc.fluids`)
- Oil, gas, and water properties
- PVT correlations
- Phase behavior calculations
- Surface and interfacial tension
- Viscosity correlations

### 🗿 **Rock Properties** (`petrocalc.rock_properties`)
- Porosity and permeability relationships
- Log analysis calculations
- Relative permeability correlations
- Capillary pressure calculations
- Formation evaluation

### 🔩 **Completion** (`petrocalc.completion`)
- Perforation design and analysis
- Hydraulic fracturing calculations
- Acidizing calculations
- Sand control design
- Stimulation optimization

### 📊 **Pressure Analysis** (`petrocalc.pressure`)
- Formation and overburden pressures
- Well control calculations
- Kick analysis
- Mud weight optimization

### 🌊 **Flow Calculations** (`petrocalc.flow`)
- Single and multiphase flow
- Pressure drop calculations
- Flow through restrictions
- Pipeline hydraulics

### 🌡️ **Thermodynamics** (`petrocalc.thermodynamics`)
- Heat transfer calculations
- Thermal properties
- Phase behavior
- Temperature profiles

### 💰 **Economics** (`petrocalc.economics`)
- Net Present Value (NPV) analysis
- Internal Rate of Return (IRR)
- Cash flow analysis
- Cost estimation
- Break-even analysis

## Installation

```bash
pip install petrocalc
```

Or for development:

```bash
git clone https://github.com/your-username/petrocalc.git
cd petrocalc
pip install -e .
```

## Quick Start

```python
import petrocalc

# Drilling calculations
mud_gradient = petrocalc.drilling.mud_weight_to_pressure_gradient(12.0, "ppg")
hydrostatic_pressure = petrocalc.drilling.hydrostatic_pressure(12.0, 10000, "ppg")

# Reservoir engineering
oil_fvf = petrocalc.reservoir.oil_formation_volume_factor_standing(
    gas_oil_ratio=500, gas_gravity=0.7, oil_gravity=35, 
    temperature=180, pressure=2500
)

# Production analysis
oil_rate = petrocalc.production.vogel_ipr(
    reservoir_pressure=3000, bottomhole_pressure=2000, maximum_oil_rate=1000
)

# Fluid properties
water_fvf = petrocalc.fluids.water_formation_volume_factor(
    temperature=180, pressure=2500, salinity=50000
)

# Rock properties
porosity = petrocalc.rock_properties.porosity_from_density_log(
    bulk_density=2.3, matrix_density=2.65, fluid_density=1.0
)

# Economic analysis
npv = petrocalc.economics.net_present_value(
    cash_flows=[100000, 150000, 120000, 90000], 
    discount_rate=0.1, 
    initial_investment=500000
)
```

## Detailed Usage Examples

### Drilling Engineering Example

```python
from petrocalc import drilling

# Calculate mud weight required for a given formation pressure
formation_pressure = 5000  # psi
depth = 10000  # ft
required_mud_weight = formation_pressure / (0.052 * depth)

print(f"Required mud weight: {required_mud_weight:.1f} ppg")

# Calculate annular velocity for hole cleaning
flow_rate = 400  # gpm
hole_diameter = 8.5  # inches
pipe_diameter = 5.0  # inches
ann_velocity = drilling.annular_velocity(flow_rate, hole_diameter, pipe_diameter)

print(f"Annular velocity: {ann_velocity:.1f} ft/min")
```

### Reservoir Engineering Example

```python
from petrocalc import reservoir

# Calculate bubble point pressure
bubble_point = reservoir.bubble_point_pressure_standing(
    gas_oil_ratio=600,
    gas_gravity=0.75,
    oil_gravity=32,
    temperature=180
)

print(f"Bubble point pressure: {bubble_point:.0f} psia")

# Decline curve analysis
initial_rate = 1000  # bbl/day
time = 2  # years
decline_rate = 0.15  # annual
current_rate = reservoir.arps_decline_curve(initial_rate, time, decline_rate)

print(f"Production rate after {time} years: {current_rate:.0f} bbl/day")
```

### Economic Analysis Example

```python
from petrocalc import economics

# Project economics analysis
cash_flows = [200000, 180000, 160000, 140000, 120000]  # Annual cash flows
initial_investment = 800000
discount_rate = 0.12

npv = economics.net_present_value(cash_flows, discount_rate, initial_investment)
irr = economics.internal_rate_of_return(cash_flows, initial_investment)
payback = economics.discounted_payback_period(cash_flows, discount_rate, initial_investment)

print(f"NPV: ${npv:,.0f}")
print(f"IRR: {irr:.1%}")
print(f"Payback period: {payback:.1f} years")
```

## Requirements

- Python >= 3.10
- No external dependencies (uses only Python standard library)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This library implements correlations and methods from various petroleum engineering textbooks and industry standards, including:

- "Formulas and Calculations for Petroleum Engineering" by Cenk Temizel
- Various SPE papers and industry correlations
- Standard petroleum engineering practices

## Author

**Muhammad Farzad Ali**  
Email: muhammad.farzad.ali@gmail.com

## Version

Current version: 0.1.1

"""
engineering.py
===============
Object-oriented engineering calculation classes for the Fluid Flow &
Heat Transfer Engineering Suite capstone project.

This module contains no Streamlit code — it is pure Python so it can be
unit-tested and reused independently of the UI. Each class validates its
own inputs and raises ValueError on physically invalid data (e.g. a
negative diameter), which the Streamlit pages catch and turn into
on-screen warnings instead of crashes.

Classes:
    Fluid               - a fluid and its density/viscosity properties
    Pipe                - the geometry of a circular pipe
    PipeFlowAnalyzer    - pipe flow calculations (Module A)
    FlatWallConduction  - steady-state 1D conduction, Fourier's Law (Module B.1)
    NewtonianCooling    - Newton's Law of Cooling (Module B.2)
"""

import math


class Fluid:
    """Represents a fluid and its density and dynamic viscosity."""

    #: Built-in fluid presets: name -> {density (kg/m^3), viscosity (Pa.s)}
    PRESET_FLUIDS = {
        "Water (20°C)": {"density": 998.0, "viscosity": 1.002e-3},
        "Air (20°C, 1 atm)": {"density": 1.225, "viscosity": 1.81e-5},
        "Crude Oil (medium, 20°C)": {"density": 870.0, "viscosity": 8.0e-3},
    }

    def __init__(self, name: str, density: float, viscosity: float):
        """
        Initialize a Fluid.

        Args:
            name: Descriptive label for the fluid.
            density: Fluid density in kg/m^3. Must be greater than 0.
            viscosity: Dynamic viscosity in Pa.s (kg/m.s). Must be greater than 0.

        Raises:
            ValueError: If density or viscosity is not strictly positive.
        """
        if density <= 0:
            raise ValueError("Fluid density must be greater than 0 kg/m^3.")
        if viscosity <= 0:
            raise ValueError("Fluid viscosity must be greater than 0 Pa.s.")
        self.name = name
        self.density = density
        self.viscosity = viscosity

    @classmethod
    def from_preset(cls, preset_name: str) -> "Fluid":
        """
        Build a Fluid from one of the built-in presets.

        Args:
            preset_name: A key in Fluid.PRESET_FLUIDS.

        Returns:
            A new Fluid instance using that preset's properties.

        Raises:
            KeyError: If preset_name is not a recognised preset.
        """
        props = cls.PRESET_FLUIDS[preset_name]
        return cls(preset_name, props["density"], props["viscosity"])

    def __repr__(self) -> str:
        return f"Fluid(name={self.name!r}, density={self.density}, viscosity={self.viscosity})"


class Pipe:
    """Represents the geometry of a circular pipe."""

    def __init__(self, diameter_m: float, length_m: float, roughness_m: float):
        """
        Initialize a Pipe.

        Args:
            diameter_m: Internal diameter in metres. Must be greater than 0.
            length_m: Pipe length in metres. Must be greater than 0.
            roughness_m: Absolute internal roughness in metres. Must be >= 0.

        Raises:
            ValueError: If diameter or length is not positive, or roughness
                is negative.
        """
        if diameter_m <= 0:
            raise ValueError("Pipe diameter must be greater than 0 m.")
        if length_m <= 0:
            raise ValueError("Pipe length must be greater than 0 m.")
        if roughness_m < 0:
            raise ValueError("Pipe roughness cannot be negative.")
        self.diameter_m = diameter_m
        self.length_m = length_m
        self.roughness_m = roughness_m

    @property
    def area_m2(self) -> float:
        """Cross-sectional flow area of the pipe, in m^2."""
        return (math.pi / 4.0) * self.diameter_m ** 2

    def __repr__(self) -> str:
        return f"Pipe(D={self.diameter_m}m, L={self.length_m}m, roughness={self.roughness_m}m)"


class PipeFlowAnalyzer:
    """
    Performs pipe flow calculations (velocity, Reynolds number, friction
    factor, and pressure drop) for a given Fluid flowing through a Pipe.
    """

    #: Reynolds number below which flow is considered laminar.
    RE_LAMINAR_LIMIT = 2300
    #: Reynolds number above which flow is considered fully turbulent.
    RE_TURBULENT_LIMIT = 4000

    def __init__(self, fluid: Fluid, pipe: Pipe):
        """
        Initialize the analyzer.

        Args:
            fluid: A Fluid instance describing the flowing fluid.
            pipe: A Pipe instance describing the pipe geometry.
        """
        self.fluid = fluid
        self.pipe = pipe

    def velocity(self, flow_rate_m3s: float) -> float:
        """
        Compute the mean flow velocity for a given volumetric flow rate.

        Args:
            flow_rate_m3s: Volumetric flow rate in m^3/s. Must be >= 0.

        Returns:
            Mean flow velocity in m/s.

        Raises:
            ValueError: If flow_rate_m3s is negative.
        """
        if flow_rate_m3s < 0:
            raise ValueError("Flow rate cannot be negative.")
        return flow_rate_m3s / self.pipe.area_m2

    def reynolds_number(self, velocity_ms: float) -> float:
        """
        Compute the Reynolds number, Re = (rho * v * D) / mu.

        Args:
            velocity_ms: Mean flow velocity in m/s.

        Returns:
            Dimensionless Reynolds number.
        """
        return (self.fluid.density * velocity_ms * self.pipe.diameter_m) / self.fluid.viscosity

    def friction_factor(self, re: float) -> float:
        """
        Compute the dimensionless Darcy friction factor.

        Uses f = 64/Re for laminar flow (Re < 2300), and the Swamee-Jain
        explicit approximation to the Colebrook-White equation for
        turbulent flow (Re >= 2300):

            f = 0.25 / [log10(eps/(3.7*D) + 5.74/Re^0.9)]^2

        Args:
            re: Reynolds number.

        Returns:
            Dimensionless Darcy friction factor (0 if re <= 0).
        """
        if re <= 0:
            return 0.0
        if re < self.RE_LAMINAR_LIMIT:
            return 64.0 / re
        relative_roughness = self.pipe.roughness_m / self.pipe.diameter_m
        denominator = math.log10((relative_roughness / 3.7) + (5.74 / (re ** 0.9)))
        return 0.25 / (denominator ** 2)

    def flow_regime(self, re: float) -> str:
        """
        Classify the flow regime from the Reynolds number.

        Args:
            re: Reynolds number.

        Returns:
            'Laminar', 'Transitional', or 'Turbulent'.
        """
        if re < self.RE_LAMINAR_LIMIT:
            return "Laminar"
        elif re < self.RE_TURBULENT_LIMIT:
            return "Transitional"
        return "Turbulent"

    def analyze(self, flow_rate_m3s: float) -> dict:
        """
        Run the full pipe flow analysis for a given flow rate.

        Args:
            flow_rate_m3s: Volumetric flow rate in m^3/s. Must be >= 0.

        Returns:
            Dict with keys: flow_rate_m3s, velocity_ms, reynolds_number,
            friction_factor, regime, pressure_drop_pa, pressure_drop_kpa.

        Raises:
            ValueError: If flow_rate_m3s is negative.
        """
        v = self.velocity(flow_rate_m3s)
        re = self.reynolds_number(v)
        f = self.friction_factor(re)
        dp_pa = f * (self.pipe.length_m / self.pipe.diameter_m) * (self.fluid.density * v ** 2) / 2.0
        return {
            "flow_rate_m3s": flow_rate_m3s,
            "velocity_ms": v,
            "reynolds_number": re,
            "friction_factor": f,
            "regime": self.flow_regime(re),
            "pressure_drop_pa": dp_pa,
            "pressure_drop_kpa": dp_pa / 1000.0,
        }


class FlatWallConduction:
    """Steady-state 1D conduction through a single-layer flat wall (Fourier's Law)."""

    def __init__(self, thermal_conductivity: float, area_m2: float, thickness_m: float):
        """
        Initialize the wall.

        Args:
            thermal_conductivity: Material thermal conductivity, k, in
                W/m.K. Must be greater than 0.
            area_m2: Cross-sectional area normal to heat flow, in m^2.
                Must be greater than 0.
            thickness_m: Wall thickness in the direction of heat flow, in
                metres. Must be greater than 0.

        Raises:
            ValueError: If any argument is not strictly positive.
        """
        if thermal_conductivity <= 0:
            raise ValueError("Thermal conductivity must be greater than 0 W/m.K.")
        if area_m2 <= 0:
            raise ValueError("Area must be greater than 0 m^2.")
        if thickness_m <= 0:
            raise ValueError("Thickness must be greater than 0 m.")
        self.k = thermal_conductivity
        self.area_m2 = area_m2
        self.thickness_m = thickness_m

    def heat_transfer_rate(self, t_hot: float, t_cold: float) -> float:
        """
        Compute the steady-state conduction heat transfer rate.

        Fourier's Law: Q = k * A * (T_hot - T_cold) / L

        Args:
            t_hot: Hot-face temperature (°C or K).
            t_cold: Cold-face temperature (same scale as t_hot).

        Returns:
            Heat transfer rate, Q, in Watts. Negative if t_cold > t_hot
            (heat flowing in the opposite direction).
        """
        return self.k * self.area_m2 * (t_hot - t_cold) / self.thickness_m


class NewtonianCooling:
    """
    Newton's Law of Cooling: lumped-capacitance transient cooling (or
    heating) of an object exposed to a constant-temperature ambient fluid.
    """

    def __init__(self, mass_kg: float, specific_heat: float, h: float,
                 area_m2: float, t_ambient: float):
        """
        Initialize the cooling model.

        Args:
            mass_kg: Mass of the object, in kg. Must be greater than 0.
            specific_heat: Specific heat capacity of the object's
                material, c, in J/kg.K. Must be greater than 0.
            h: Convective heat transfer coefficient between the object and
                the ambient fluid, in W/m^2.K. Must be greater than 0.
            area_m2: Surface area of the object exposed to the ambient
                fluid, in m^2. Must be greater than 0.
            t_ambient: Ambient (surrounding fluid) temperature, T_inf.

        Raises:
            ValueError: If mass, specific_heat, h, or area is not
                strictly positive.
        """
        if mass_kg <= 0:
            raise ValueError("Mass must be greater than 0 kg.")
        if specific_heat <= 0:
            raise ValueError("Specific heat must be greater than 0 J/kg.K.")
        if h <= 0:
            raise ValueError("Convection coefficient must be greater than 0 W/m^2.K.")
        if area_m2 <= 0:
            raise ValueError("Area must be greater than 0 m^2.")
        self.mass_kg = mass_kg
        self.specific_heat = specific_heat
        self.h = h
        self.area_m2 = area_m2
        self.t_ambient = t_ambient

    @property
    def time_constant_s(self) -> float:
        """Thermal time constant, tau = (m * c) / (h * A), in seconds."""
        return (self.mass_kg * self.specific_heat) / (self.h * self.area_m2)

    def temperature_at(self, t_initial: float, time_s: float) -> float:
        """
        Compute the object's temperature at a given elapsed time.

        T(t) = T_inf + (T0 - T_inf) * exp(-t / tau)

        Args:
            t_initial: Initial object temperature, T0.
            time_s: Elapsed time in seconds. Must be >= 0.

        Returns:
            Object temperature at time_s (same scale as t_initial).

        Raises:
            ValueError: If time_s is negative.
        """
        if time_s < 0:
            raise ValueError("Time cannot be negative.")
        return self.t_ambient + (t_initial - self.t_ambient) * math.exp(-time_s / self.time_constant_s)

    def time_to_reach(self, t_initial: float, t_target: float) -> float:
        """
        Compute the time required to cool (or heat) from t_initial to
        t_target.

        Solves T(t) = T_inf + (T0 - T_inf) * exp(-t / tau) for t:

            t = -tau * ln[(T_target - T_inf) / (T0 - T_inf)]

        Args:
            t_initial: Initial object temperature, T0.
            t_target: Target temperature. For a finite, physically
                meaningful time to exist, t_target must lie strictly
                between t_ambient and t_initial.

        Returns:
            Time in seconds required to reach t_target.

        Raises:
            ValueError: If t_initial equals t_ambient (no driving
                temperature difference), or if t_target is not strictly
                between t_ambient and t_initial.
        """
        if t_initial == self.t_ambient:
            raise ValueError("Initial temperature cannot equal the ambient temperature.")
        ratio = (t_target - self.t_ambient) / (t_initial - self.t_ambient)
        if ratio <= 0 or ratio >= 1:
            raise ValueError(
                "Target temperature must be strictly between the ambient "
                "temperature and the initial temperature."
            )
        return -self.time_constant_s * math.log(ratio)

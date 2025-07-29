"""Methods for correlating time-independent data, like yield and tensile strength"""

import abc

import numpy as np
from numpy.polynomial import Polynomial
import scipy.interpolate as inter

from pycreep import dataset, methods, units


class TimeIndependentCorrelation(abc.ABC):
    """
    Class used to correlate time independent/temperature dependent
    data as a function of temperature.
    """

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def predict(self, T):
        """
        Predict some new values as a function of temperature

        Args:
            T:      temperature data
        """
        return

    @abc.abstractmethod
    def predict_heat(self, heat, T):
        """
        Predict heat-specific values as a function of temperature

        Args:
            heat:   heat ID
            T:      temperature
        """
        return

    def analyze(self):
        """Analyze the data to get ready for predict calls"""
        return self

    def __call__(self, T):
        """
        Alias for self.predict(T)

        Args:
            T:      temperature data
        """
        return self.predict(T)


class DataDrivenTimeIndependentCorrelation(dataset.DataSet, TimeIndependentCorrelation):
    """
    Class used to correlate time independent/temperature dependent
    data as a function of temperature.

    Args:
        data:                       dataset as a pandas dataframe

    Keyword Args:
        temp_field (str):           field in array giving temperature, default
                                    is "Temp (C)"
        stress_field (str):         field in array giving stress, default is
                                    "Stress (MPa)"
        heat_field (str):           field in array giving heat ID, default is
                                    "Heat/Lot ID"
        input_temp_units (str):     temperature units, default is "C"
        input_stress_units (str):   stress units, default is "MPa"
        analysis_temp_units (str):  temperature units for analysis,
                                    default is "K"
        analysis_stress_units (str):    analysis stress units, default is
                                        "MPa"

    """

    def __init__(
        self,
        data,
        temp_field="Temp (C)",
        stress_field="Stress (MPa)",
        heat_field="Heat/Lot ID",
        input_temp_units="degC",
        input_stress_units="MPa",
        analysis_temp_units="K",
        analysis_stress_units="MPa",
    ):
        super().__init__(data)

        self.add_field_units(
            "temperature", temp_field, input_temp_units, analysis_temp_units
        )
        self.add_field_units(
            "stress", stress_field, input_stress_units, analysis_stress_units
        )

        self.add_heat_field(heat_field)


class PolynomialTimeIndependentCorrelation(DataDrivenTimeIndependentCorrelation):
    """
    Class used to correlate time independent/temperature dependent
    data as a function of temperature using polynomial regression.

    Args:
        deg:                        polynomial degree
        data:                       dataset as a pandas dataframe

    Keyword Args:
        temp_field (str):           field in array giving temperature, default
                                    is "Temp (C)"
        stress_field (str):         field in array giving stress, default is
                                    "Stress (MPa)"
        heat_field (str):           field in array giving heat ID, default is
                                    "Heat/Lot ID"
        input_temp_units (str):     temperature units, default is "C"
        input_stress_units (str):   stress units, default is "MPa"
        analysis_temp_units (str):  temperature units for analysis,
                                    default is "K"
        analysis_stress_units (str):    analysis stress units, default is
                                        "MPa"

    """

    def __init__(self, deg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deg = deg
        self.heat_correlations = {}
        self.heat_correlation_data = {}

    def analyze(self):
        """
        Run the stress analysis and store results
        """
        # Overall correlation
        self.polyavg, self.preds, self.SSE, self.R2, self.SEE = methods.polynomial_fit(
            self.temperature, self.stress, self.deg
        )

        # Heat-specific correlations
        for heat in self.unique_heats:
            polyavg, preds, SSE, R2, SEE = methods.polynomial_fit(
                self.temperature[self.heat_indices[heat]],
                self.stress[self.heat_indices[heat]],
                self.deg,
            )
            self.heat_correlations[heat] = polyavg
            self.heat_correlation_data[heat] = (preds, SSE, R2, SEE)

        return self

    def predict(self, T):
        """
        Predict some new values as a function of temperature

        Args:
            T:      temperature data
        """
        return np.polyval(self.polyavg, T)

    def predict_heat(self, heat, T):
        """
        Predict heat-specific values as a function of temperature

        Args:
            heat:   heat ID
            T:      temperature
        """
        return np.polyval(self.heat_correlations[heat], T)


class UserProvidedTimeIndependentCorrelation(TimeIndependentCorrelation):
    """
    Superclass where the user provides the correlation directly
    for all heats.

    Keyword Args:
        input_temp_units (str):     temperature units, default is "C"
        input_stress_units (str):   stress units, default is "MPa"
        analysis_temp_units (str):  temperature units for analysis,
                                    default is "K"
        analysis_stress_units (str):    analysis stress units, default is
                                        "MPa"
    """

    def __init__(
        self,
        *args,
        input_temp_units="degC",
        input_stress_units="MPa",
        analysis_temp_units="K",
        analysis_stress_units="MPa",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fn = lambda T: None

        self.corr_temp = input_temp_units
        self.in_temp = analysis_temp_units
        self.corr_stress = input_stress_units
        self.in_stress = analysis_stress_units

        self.unique_heats = []

    def predict(self, T):
        """
        Predict some new values as a function of temperature

        Args:
            T:      temperature data
        """
        return units.convert(
            self.fn(units.convert(T, self.in_temp, self.corr_temp)),
            self.corr_stress,
            self.in_stress,
        )

    def predict_heat(self, heat, T):
        """
        Predict heat-specific values as a function of temperature

        Args:
            heat:   heat ID
            T:      temperature
        """
        return self.predict(T)


class TabulatedTimeIndependentCorrelation(UserProvidedTimeIndependentCorrelation):
    """
    Class used to correlate time independent/temperature dependent
    data as a function of temperature using a user-provided table
    of values

    Args:
        temp_table:                 temperature table values
        stress_table:               stress table values
    """

    def __init__(self, temp_table, stress_table, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.temp_table = temp_table
        self.stress_table = stress_table

    def analyze(self):
        """
        Run the stress analysis and store results
        """
        self.fn = inter.interp1d(self.temp_table, self.stress_table)

        return self


class UserPolynomialTimeIndependentCorrelation(UserProvidedTimeIndependentCorrelation):
    """
    User provides a temperature -> value correlation directly

    Args:
        poly:       polynomial in numpy order
    """

    def __init__(self, poly, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.coefs = poly

    def analyze(self):
        """
        Run the stress analysis and store results
        """
        self.fn = Polynomial(self.coefs[::-1])


class SimpleASMEPolynomialTimeIndependentCorrelation(
    UserProvidedTimeIndependentCorrelation
):
    """
    ASME type correlation of

    F * S * (p[0] * (T/T0)**0 + p[1] * (T/T0)**1 + ...)

    Args:
        poly:       polynomial in standard
    """

    def __init__(self, F, S0, T0, poly, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.F = F
        self.S0 = S0
        self.T0 = T0
        self.coefs = poly

    def analyze(self):
        """
        Run the stress analysis and store results
        """
        self.fn = lambda T: self.F * self.S0 * np.polyval(self.coefs[::-1], T / self.T0)


class StandardASMEPolynomialTimeIndependentCorrelation(
    UserProvidedTimeIndependentCorrelation
):
    """
    ASME type correlation of

    min(F * S * (1 + p[1] * (T-T0)**1 + p[2] * (T-T0)**2 + ...), S)

    Args:
        poly:       polynomial in standard
    """

    def __init__(self, F, S0, T0, poly, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.F = F
        self.S0 = S0
        self.T0 = T0
        self.coefs = poly

    def analyze(self):
        """
        Run the stress analysis and store results
        """
        self.fn = lambda T: np.minimum(
            self.F * self.S0 * np.polyval(self.coefs[::-1], T - self.T0), self.S0
        )


class TensileDataAnalysis(dataset.DataSet):
    """
    Superclass for time-temperature parameter (TTP) analysis of a
    dataset

    Args:
        data:                       dataset as a pandas dataframe

    Keyword Args:
        temp_field (str):           field in array giving temperature, default
                                    is "Temp (C)"
        yield_strength_field (str): field in array giving yield stress, default is
                                    "Yield Strength (MPa)"
        tensile_strength_field (str): field in array giving tensile strength, default is
                                    "Tensile Strength (MPa)"
        heat_field (str):           field in array giving heat ID, default is
                                    "Heat/Lot ID"
        input_temp_units (str):     temperature units, default is "C"
        input_stress_units (str):   stress units, default is "MPa"
        analysis_temp_units (str):  temperature units for analysis,
                                    default is "C"
        analysis_stress_units (str):    analysis stress units, default is
                                        "MPa"

    The analyzed model must provide Sy(T) and Su(T) methods.
    """

    def __init__(
        self,
        data,
        temp_field="Temp (C)",
        yield_strength_field="Yield Strength (MPa)",
        tensile_strength_field="Tensile Strength (MPa)",
        heat_field="Heat/Lot ID",
        input_temp_units="degC",
        input_stress_units="MPa",
        analysis_temp_units="degC",
        analysis_stress_units="MPa",
    ):
        super().__init__(data)

        self.add_field_units(
            "temperature", temp_field, input_temp_units, analysis_temp_units
        )
        self.add_field_units(
            "yield_strength",
            yield_strength_field,
            input_stress_units,
            analysis_stress_units,
        )
        self.add_field_units(
            "tensile_strength",
            tensile_strength_field,
            input_stress_units,
            analysis_stress_units,
        )

        self.analysis_temp_units = analysis_temp_units
        self.analysis_stress_units = analysis_stress_units

        self.add_heat_field(heat_field)


class ASMETensileDataAnalysis(TensileDataAnalysis):
    """
    ASME type tensile data analysis

    Args:
        order_yield:                      polynomial order for yield correlation
        order_tensile:                    polynomial order for tensile correlation
        min_yield:                 minimum yield strength value
        min_tensile:               minimum tensile strength value
        data:                       dataset as a pandas dataframe

    Keyword Args:
        temp_field (str):           field in array giving temperature, default
                                    is "Temp (C)"
        yield_strength_field (str): field in array giving yield stress, default is
                                    "Yield Strength (MPa)"
        tensile_strength_field (str): field in array giving tensile strength, default is
                                    "Tensile Strength (MPa)"
        heat_field (str):           filed in array giving heat ID, default is
                                    "Heat/Lot ID"
        input_temp_units (str):     temperature units, default is "C"
        input_stress_units (str):   stress units, default is "MPa"
        analysis_temp_units (str):  temperature units for analysis,
                                    default is "K"
        analysis_stress_units (str):    analysis stress units, default is
                                        "MPa"
        room_temperature (float):       room temperature value in analysis units
        rt_threshold (float):           tolerance for finding RT values
        F_yield (float):            factor on the yield strength correlation, default 1.0
        F_tensile (float):          factor on the tensile strength correlation, default 1.1
    """

    def __init__(
        self,
        order_yield,
        order_tensile,
        min_yield,
        min_tensile,
        *args,
        room_temperature=21.0,
        rt_threshold=10.0,
        F_yield=1.0,
        F_tensile=1.1,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.order_yield = order_yield
        self.order_tensile = order_tensile
        self.room_temperature = room_temperature
        self.rt_threshold = rt_threshold

        self.min_yield = min_yield
        self.min_tensile = min_tensile

        self.F_yield = F_yield
        self.F_tensile = F_tensile

    def _heat_rt_props(self, field):
        """
        Calculate the heat-specific room temperature values of field

        Args:
            field (np.array): input field
        """
        rt_values = np.zeros_like(field)
        for name, inds in self.heat_indices.items():
            T_vals = self.temperature[inds]
            T_rt = np.logical_and(
                T_vals > self.room_temperature - self.rt_threshold,
                T_vals < self.room_temperature + self.rt_threshold,
            )
            if np.all(np.logical_not(T_rt)):
                raise RuntimeError(f"Heat {name} is missing room temperature data")
            rt_values[inds] = np.mean(field[inds][T_rt])

        return rt_values

    def analyze(self):
        """
        Run the regression analysis
        """
        rt_yield = self._heat_rt_props(self.yield_strength)
        rt_tensile = self._heat_rt_props(self.tensile_strength)

        self.R_yield = self.yield_strength / rt_yield
        self.R_tensile = self.tensile_strength / rt_tensile

        self.poly_yield, self.R2_yield = methods.asme_tensile_analysis(
            self.temperature, self.R_yield, self.order_yield, Tref=self.room_temperature
        )
        self.poly_tensile, self.R2_tensile = methods.asme_tensile_analysis(
            self.temperature,
            self.R_tensile,
            self.order_tensile,
            Tref=self.room_temperature,
        )

        return self

    def Sy(self, T):
        """
        Design yield strength at temperature T

        Args:
            T:      temperature data
        """
        return np.minimum(
            np.polyval(self.poly_yield, T - self.room_temperature)
            * self.F_yield
            * self.min_yield,
            self.min_yield,
        )

    def Su(self, T):
        """
        Design tensile strength at temperature T

        Args:
            T:      temperature data
        """
        return np.minimum(
            np.polyval(self.poly_tensile, T - self.room_temperature)
            * self.F_tensile
            * self.min_tensile,
            self.min_tensile,
        )

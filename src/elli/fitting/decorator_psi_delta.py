"""Decorator functions for convenient fitting"""
# Encoding: utf-8
from typing import Callable
import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.graph_objects as go
from lmfit import minimize, Parameters
from ipywidgets import widgets
from IPython.display import display
from ..result import Result
from ..utils import calcPseudoDiel, calc_rho
from .params_hist import ParamsHist

class FitRho():
    """A class to fit psi/delta or rho based ellipsometry data with two degress of freedom"""

    def set_psi_delta(self, update_exp:bool=False, update_names:bool=False) -> None:
        """Sets Plot to Psi/Delta values

        Args:
            update_exp (bool, optional):
                Flag to change the experimental data as well. Defaults to False.
            update_names (bool, optional):
                Flag to change the label names. Defaults to False.
        """
        data = self.model(self.exp_data.index, self.params)
        self.fig.update_layout(yaxis_title="Ψ/Δ (°)")
        self.fig.data[2].y = data.psi
        self.fig.data[3].y = data.delta

        if update_exp:
            self.fig.data[0].y = self.exp_data.loc[:, 'Ψ']
            self.fig.data[1].y = self.exp_data.loc[:, 'Δ']

        if update_names:
            self.fig.data[0].name = 'Ψ'
            self.fig.data[1].name = 'Δ'
            self.fig.data[2].name = 'Ψ_tmm'
            self.fig.data[3].name = 'Δ_tmm'

    def set_rho(self, update_exp:bool=False, update_names:bool=False) -> None:
        """Sets Plot to Rho values

        Args:
            update_exp (bool, optional):
                Flag to change the experimental data as well. Defaults to False.
            update_names (bool, optional):
                Flag to change the label names. Defaults to False.
        """
        data = self.model(self.exp_data.index, self.params)
        self.fig.update_layout(yaxis_title="ρ")
        self.fig.data[2].y = data.rho.real
        self.fig.data[3].y = data.rho.imag

        if update_exp:
            exp_rho = calc_rho(self.exp_data)
            self.fig.data[0].y = exp_rho.apply(lambda x: x.real).values
            self.fig.data[1].y = exp_rho.apply(lambda x: x.imag).values

        if update_names:
            self.fig.data[0].name = 'ρr'
            self.fig.data[1].name = 'ρi'
            self.fig.data[2].name = 'ρr_tmm'
            self.fig.data[3].name = 'ρi_tmm'

    def set_pseudo_diel(self, update_exp:bool=False, update_names:bool=False):
        """Sets Plot to Pseudo Dielectric function values

        Args:
            update_exp (bool, optional): Flag to change the experimental data as well.
                                         Defaults to False.
            update_names (bool, optional): Flag to change the label names.
                                           Defaults to False.
        """
        data = self.model(self.exp_data.index, self.params)
        peps = calcPseudoDiel(pd.DataFrame(data.rho, index=self.exp_data.index).iloc[:, 0],
                                          self.angle)
        self.fig.update_layout(yaxis_title="ϵ")
        self.fig.data[2].y = peps.loc[:, 'ϵ1']
        self.fig.data[3].y = peps.loc[:, 'ϵ2']

        if update_exp:
            exp_peps = calcPseudoDiel(calc_rho(self.exp_data), self.angle)
            self.fig.data[0].y = exp_peps.loc[:, 'ϵ1']
            self.fig.data[1].y = exp_peps.loc[:, 'ϵ2']

        if update_names:
            self.fig.data[0].name = 'ϵ1'
            self.fig.data[1].name = 'ϵ2'
            self.fig.data[2].name = 'ϵ1_tmm'
            self.fig.data[3].name = 'ϵ2_tmm'

    def update_params(self, change:dict):
        """Update plot after a change of fitting parameters

        Args:
            change (dict): A dictionary containing the ipywidgets change event
            selected (dict): The selected value of the data display dropdown widget
        """
        self.params[change.owner.description].value = change.new

        with self.fig.batch_update():
            update = self.update_dict.get(self.selector.value)
            if update is not None:
                update()

    def update_selection(self, change:dict):
        """Update plot after selection of displayed data

        Args:
            change (dict): A dictionary containing the ipywidgets change event
        """
        with self.fig.batch_update():
            update = self.update_dict.get(change.new)
            if update is not None:
                update(update_exp=True, update_names=True)

    def fit_button_clicked(self):
        """Fit and update plot after the fit button has been clicked

        Args:
            selected (dict): Dict containing the current widget information
                of the selection dropdown.
        """
        self.fit()
        if isinstance(self.params, ParamsHist):
            self.params.commit()
        self.params.update_params(self.fitted_params)
        self.update_widgets()

        with self.fig.batch_update():
            update = self.update_dict.get(self.selector.value)
            if update is not None:
                update()

    def re_undo_button_clicked(self, button:widgets.Button):
        """Redo or undo an operation on the paramters history object

        Args:
            button (widgets.Button):
                The button instance, which triggered the event.
        """
        if button.description == 'Undo':
            self.last_params = self.params.pop()
            self.update_widgets()
        elif self.last_params is not None:
            self.params.update_params(self.last_params)
            self.update_widgets()
            self.last_params = None

    def update_widgets(self):
        """Updates the widget values according to the current parameters."""
        for param in self.params:
            widget = self.param_widgets.get(param)
            if widget is not None:
                widget.value = self.params[param].value

    def create_widgets(self):
        """Create ipywidgets for parameter estimation"""
        self.param_widgets = {}
        self.selector = widgets.Dropdown(
            options=['Psi/Delta', 'Rho', 'Pseudo Diel.'],
            value='Psi/Delta',
            description='Display: ',
            disabled=False
        )
        self.selector.observe(self.update_selection, names='value')

        for param in self.params.valuesdict():
            curr_widget = widgets.BoundedFloatText(self.params[param],
                                                   min=self.params[param].min,
                                                   max=self.params[param].max,
                                                   description=param,
                                                   continuous_update=False)
            curr_widget.observe(self.update_params, names='value')
            self.param_widgets[param] = curr_widget

        fit_button = widgets.Button(description='Fit')
        fit_button.on_click(lambda _: self.fit_button_clicked())
        undo_button = widgets.Button(description='Undo')
        undo_button.on_click(self.re_undo_button_clicked)
        redo_button = widgets.Button(description='Redo')
        redo_button.on_click(self.re_undo_button_clicked)

        display(widgets.VBox([widgets.HBox(list(self.param_widgets.values()) +
                                           [self.selector, fit_button, undo_button, redo_button],
                                           layout=widgets.Layout(width='100%',
                                                                 display='inline-flex',
                                                                 flex_flow='row wrap')),
                              self.fig]))

    def fit_function(self,
                     params:Parameters,
                     lbda:npt.NDArray,
                     rhor:npt.NDArray,
                     rhoi:npt.NDArray) -> npt.NDArray:
        """The fit function to minimize the fitting problem

        Args:
            params (Parameters): The lmfit fitting Parameters to construct the simulation
            lbda (npt.NDArray): Wavelengths in nm
            rhor (npt.NDArray): The real part of the experimental rho
            rhoi (npt.NDArray): The imaginary part of the experimental rho

        Returns:
            npt.NDArray:
                Residual between the calculation with current parameters and experimental data
        """
        result = self.model(lbda, params)

        resid_rhor = rhor - result.rho.real
        resid_rhoi = rhoi - result.rho.imag

        return np.concatenate((resid_rhor, resid_rhoi))

    def fit(self, method='leastsq'):
        """Execute lmfit with the current fitting parameters

        Args:
            method (str, optional): The fitting method to use.
                                    Any method supported by scipys curve_fit is allowed.
                                    Defaults to 'leastsq'.

        Returns:
            Result: The fitting result
        """
        rho = calc_rho(self.exp_data)
        res = minimize(self.fit_function,
                       self.params,
                       args=(rho.index.to_numpy(), rho.values.real, rho.values.imag),
                       method=method)

        self.fitted_params = res.params
        return res

    def plot(self):
        """Plot the fit results as Psi/Delta"""
        fit_result = self.model(self.exp_data.index.to_numpy(), self.fitted_params)

        return go.FigureWidget(pd.concat([self.exp_data,
                                            pd.DataFrame({'Ψ_fit': fit_result.psi,
                                                        'Δ_fit': fit_result.delta},
                                                        index=self.exp_data.index)]
                                            ).plot())

    def plot_rho(self):
        """Plot the fit results as Rho"""
        rho = calc_rho(self.exp_data)
        fit_result = self.model(rho.index.to_numpy(), self.fitted_params)

        return go.FigureWidget(pd.DataFrame({'ρr': rho.apply(lambda x: x.real),
                                             'ρi': rho.apply(lambda x: x.imag),
                                             'ρcr': fit_result.rho.real,
                                             'ρci': fit_result.rho.imag},
                                             index=rho.index).plot())

    def __init__(self,
                 exp_data:pd.DataFrame,
                 params:Parameters,
                 model:Callable[[npt.NDArray, Parameters], Result],
                 angle:float = 70):
        """Intialize the psi/delta fitting class

        Args:
            exp_data (pd.DataFrame): The dataframe containing an experimental mueller matrix.
                                     It should contain 2 columns with labels Ψ and Δ.
            params (Parameters): Fitting start parameters
            model (Callable[[npt.NDArray, Parameters], Result]):
                A function taking wavelengths as first parameter and fitting parameters as second,
                which returns a pyEllis Result object.
                This function contains the actual model which should be fitted.
            angle (float, optional): The angle of incident of the measurement.
                                     Used to calculate the Pseudo-Dielectric function.
                                     Defaults to 70.
        """
        self.model = model
        self.exp_data = exp_data
        self.params = params
        self.fitted_params = params.copy()
        self.angle = angle
        self.param_widgets = {}
        self.selector = widgets.Dropdown()
        self.last_params = None
        self.fig = go.FigureWidget(pd.concat([exp_data,
                    pd.DataFrame({'Ψ_tmm': model(exp_data.index, params).psi,
                                 'Δ_tmm': model(exp_data.index, params).delta},
                                 index=exp_data.index)]).plot(backend='plotly'))
        self.fig.update_layout(yaxis_title="Ψ/Δ (°)", xaxis_title="Wavelength (nm)")

        self.update_dict = {'Psi/Delta': self.set_psi_delta,
                            'Rho': self.set_rho,
                            'Pseudo Diel.': self.set_pseudo_diel}

        self.create_widgets()

def fit(exp_data:pd.DataFrame,
        params:Parameters,
        angle:float = 70) -> Callable[[npt.NDArray, Parameters], Result]:
    """A parameters decorator for fitting psi/delta valus. Displays an ipywidget float box for
    each fitting parameter and an interactive plot to estimate parameters.

    Args:
        exp_data (pd.DataFrame): The dataframe containing an experimental mueller matrix.
                                 It should contain 2 columns with labels Ψ and Δ.
        params (Parameters): Fitting start parameters
        angle (float, optional): The angle of incident of the measurement.
                                 Used to calculate the Pseudo-Dielectric function.
                                 Defaults to 70.

    Returns:
        Callable[[npt.NDArray, Parameters], Result]:
            fitting parameters as second,
            which returns a pyEllis Result object.
            This function contains the actual model which should be fitted and is automatically
            provided when used as a decorator.
    """
    return lambda model: FitRho(exp_data, params, model, angle)

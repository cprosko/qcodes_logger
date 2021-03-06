from qcodes import Station, Parameter, Instrument
from qcodes.utils.metadata import Metadatable
from collections.abc import Sequence
from typing import Any, Union
from warnings import warn


class DynamicStation(Station):
    """qcodes.Station with memory of different component configurations.

    When selecting a configuration for the DynamicStation, a list of
    configuration keys is provided. The DynamicStation will then search the
    cached configurations, and ensure that all components & parameters included
    in the configuration list are added to the station, and that all those which
    are NOT included in the configuration list are removed from the station.

    Arguments:
    ----------
    component_configurations (dict): Dictionary of possible, not mutually
        exclusive, sets of components and parameters to include in the station.
    """

    def __init__(
        self,
        *components: Metadatable,
        component_configurations: dict[str, Union[Parameter, Instrument]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*components, **kwargs)
        self._component_configurations = dict()
        self.set_component_configurations(component_configurations)

    def set_component_configurations(
        self, component_configurations: dict[str, Union[Parameter, Instrument]]
    ) -> None:
        # TODO: Implement a validator of some sort for this function
        self._component_configurations = component_configurations

    def adjust_station_to_meas_setup(
        self, config: Sequence[str], verbose: bool = True
    ) -> None:
        configs = self._component_configurations
        components_to_ensure = sum([configs[k] for k in config], [])
        components_to_remove = set(
            sum([configs[k] for k in configs.keys() if k not in config], [])
        )
        components_to_remove.difference_update(components_to_ensure)
        if verbose:
            print(
                "Ensuring components:",
                components_to_ensure,
                "Removing components:",
                components_to_remove,
            )
        # REMOVE UNUSED COMPONENTS
        must_remove_components = []
        for component in self.components:
            if component in [
                c.name for c in components_to_remove
            ] and component not in [c.name for c in components_to_ensure]:
                must_remove_components.append(component)
            elif component not in [c.name for c in components_to_ensure]:
                warn(
                    f"A component, {component}, exists in the qcodes.Station "
                    "which is not in the list of components used for "
                    "measurements, nor in the list of components NOT used for "
                    "the measurement. Consider adding this component to one of "
                    "the possible DynamicStation configurations."
                )
        for component in must_remove_components:
            self.remove_component(component)
        # ADD USED COMPONENTS
        for component in list(set(components_to_ensure)):
            if component.name not in self.components:
                self.add_component(component)
        if verbose:
            print(self.components)

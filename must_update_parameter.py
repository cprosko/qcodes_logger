from qcodes import Parameter, Station
from qcodes.utils.validators import Strings
from collections.abc import Sequence
from typing import Optional


class MustUpdateParameter(Parameter):
    """Parameter which may be asserted that it must be changed after retrieval.

    To assert that a MustUpdateParameter must be changed between measurements,
    one must execute qcodes_logger.check_parameters_updated() at the beginning
    of each measurement.

    Arguments:
    ----------
    name (str): Name of the parameter.

    Keyword Arguments:
    ------------------
    new_value_must_differ (bool): Whether or not each new set value must differ
        from the previous set value. Attempting to set the parameter to the same
        value twice in this case will raise an exception.
    strict (bool): Whether or not the parameter should be asserted that it must
        be updated between each call to self.get(), instead of only between each
        call of qcodes_logger.check_parameters_updated.
    **kwargs: Keyword arguments to pass to the __init__ function of the
        qcodes.Parameter class.

    Example usage:
    --------------
    At the very beginning of any QCoDes measurement, to assert that this
    parameter was changed since the last measurement, set
    MustUpdateParameter._latest_value_in_measurement to False.
    """

    def __init__(
        self,
        name: str,
        new_value_must_differ: Optional[bool] = True,
        strict: bool = True,
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self._latest_value_in_measurement = False
        self._latest_value_read = False
        self._new_value_must_differ = new_value_must_differ
        self._value = None
        self.strict = strict
        if self.label is None:
            # TODO: Check if this is necessary or if Qcodes already handles it.
            self.label = name

    # you must provide a get method, a set method, or both.
    def get_raw(self):
        if self._latest_value_read and self.strict:
            raise Exception(
                f"Current value of {self.name} has already been read, "
                f"update to a new value or set {self.name}.strict = False "
                "to disable this behavior."
            )
        self._latest_value_read = True
        return self._value

    def set_raw(self, val):
        if self._value == val and self._new_value_must_differ:
            raise Exception(
                "New measurement description must differ from the previous one!"
            )
        self._latest_value_in_measurement = (
            False  # This is only changed to 'True' by measurement code
        )
        self._latest_value_read = False
        self._value = val
        return self._value


class MeasurementDescription(MustUpdateParameter):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, vals=Strings(), new_value_must_differ=True, **kwargs)
        self.__doc__ = (
            "A string description of the current measurement. "
            "Contains a checker which asserts that this parameter "
            "is changed between every measurement run."
        )


def check_parameters_updated(
    params: Optional[Sequence[MustUpdateParameter]] = None,
    verbose: Optional[bool] = True,
) -> None:
    if params is None:
        station = Station.default
        params = [
            station[c]
            for c in station.components
            if isinstance(station[c], MustUpdateParameter)
        ]
    if verbose:
        print(params)
    for param in params:
        if param._latest_value_in_measurement:
            raise Exception(
                f"The latest value of {param.label}: {param()}{param.unit} "
                "has already been recorded in a previous measurement. Update "
                "the value of this parameter and try again."
            )
        else:
            param._latest_value_in_measurement = True

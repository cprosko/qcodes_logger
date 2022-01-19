from qcodes import Parameter


class MustUpdateParameter(Parameter):
    """A parameter which can be asserted that it must be changed between measurements,
    provided measurement code runs 'check_parameters_updated' on it.

    Arguments:
    ----------
    name (str): Name of the parameter

    Keyword Arguments:
    ------------------
    new_value_must_differ (bool): Whether or not each new set value must differ from the
        previous set value. Attempting to set the parameter to the same value twice in
        this case will raise an exception.
    **kwargs: Keyword arguments to pass to the __init__ function of the qcodes.Parameter class.

    Example usage:
    --------------
    At the very beginning of any QCoDes measurement, to assert that this parameter was changed
    since the last measurement, set MustUpdateParameter._latest_value_in_measurement to False.
    """

    def __init__(self, name, new_value_must_differ=True, **kwargs):
        super().__init__(name, **kwargs)
        self._latest_value_in_measurement = False
        self._latest_value_read = False
        self._new_value_must_differ = new_value_must_differ
        self._value = None
        if self.label is None:
            # TODO: Check if this is necessary or if Qcodes already handles it.
            self.label = name

    # you must provide a get method, a set method, or both.
    def get_raw(self):
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

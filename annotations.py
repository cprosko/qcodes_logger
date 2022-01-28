from qcodes import load_by_id
from collections.abc import Sequence
from typing import Optional, Any, Union

_ANNOTATION_KEY = "post_measurement_annotation"
_ERROR_KEY = "errors_in_measurement"
_PLOTTR_KEY = "inspectr_tag"
_CROSS_KEY = "cross"
_ADDITIONAL_ANNOTATION_KEY = "\nADDITIONAL ANNOTATION: \n"


def annotate_runs(
    run_ids: Union[int, Sequence[int]],
    annotation: Optional[str] = None,
    error_state: Optional[bool] = None,
    other_metadata: Optional[dict[Any]] = None,
    flag_in_plottr: Optional[bool] = True,
) -> None:
    """Add annotation as metadata to a QCoDes measurement.

    Arguments:
    ----------
    run_ids (int | Sequence[int]): run_id or iterable of run_ids to add the
        metadata to.

    Keyword Arguments:
    ------------------
    annotation (Optional[str]): String annotation to add to the measurement,
        stored in the dataset's metadata under the key
        'post_measurement_annotation'.
    error_state (Optional[bool]): Whether or not the measurement should be
        flagged with a bool as containing error(s). Stored in dataset's
        metadata under the key 'errors_in_measurement'.
    other_metadata (Optional[dict[Any]]): Dictionary of other metadata to add
        or update in the dataset.
    flag_in_plottr (bool), default = True: Whether or not to flag measurements
        with a 'cross' in plottr-inspectr if they have error_state = True.
    """
    if isinstance(run_ids, int):
        run_ids = (run_ids,)
    for run_id in run_ids:
        dataset = load_by_id(run_id)
        if annotation is not None:
            dataset.add_metadata(_ANNOTATION_KEY, annotation)
        if error_state is not None:
            dataset.add_metadata("errors_in_measurement", error_state)
            if flag_in_plottr and error_state is True:
                dataset.add_metadata(_PLOTTR_KEY, _CROSS_KEY)
        if other_metadata is not None:
            for k, v in other_metadata.items():
                dataset.add_metadata(k, v)


def append_annotation(
    run_ids: Union[int, Sequence[int]],
    annotation: Optional[str] = None,
    error_state: Optional[bool] = None,
    other_metadata: Optional[dict[Any]] = None,
    flag_in_plottr: Optional[bool] = True,
) -> None:
    """Append annotations to QCoDes measurements without overwriting.

    Arguments:
    ----------
    run_ids (int | Sequence[int]): run_id or iterable of run_ids to add the
        metadata to.

    Keyword Arguments:
    ------------------
    annotation (Optional[str]): String annotation to add to the measurement,
        stored in the dataset's metadata under the key
        'post_measurement_annotation'. Is appended to any existing annotation
        with a flag that this is a new annotation in between.
    error_state (Optional[bool]): Whether or not the measurement should be
        flagged with a bool as containing error(s). Stored in dataset's
        metadata under the key 'errors_in_measurement'.
    other_metadata (Optional[dict[Any]]): Dictionary of other metadata to add
        or update in the dataset.
    flag_in_plottr (bool), default = True: Whether or not to flag measurements
        with a 'cross' in plottr-inspectr if they have error_state = True.
    """
    if isinstance(run_ids, int):
        run_ids = (run_ids,)
    for run_id in run_ids:
        dataset = load_by_id(run_id)
        metadata = dataset.metadata
        full_annotation = ""
        if _ANNOTATION_KEY in metadata:
            full_annotation += metadata[_ANNOTATION_KEY]
            if annotation is not None:
                full_annotation += _ADDITIONAL_ANNOTATION_KEY
        if annotation is not None:
            full_annotation += annotation
        dataset.add_metadata(_ANNOTATION_KEY, annotation)
        if error_state is not None:
            dataset.add_metadata(_ERROR_KEY, error_state)
            if flag_in_plottr and error_state is True:
                dataset.add_metadata(_PLOTTR_KEY, _CROSS_KEY)
        if other_metadata is not None:
            for k, v in other_metadata.items():
                dataset.add_metadata(k, v)

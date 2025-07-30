import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Sequence

from ome_types import OME
from ome_types.model import UnitsTime

log = logging.getLogger(__name__)


@dataclass
class StandardMetadata:
    """
    A simple container for embedded metadata fields.

    Attributes
    ----------
    binning: Optional[str]
        Binning configuration.

    column: Optional[str]
        Column information.

    dimensions_present: Optional[Sequence[str]]
        List or sequence of dimension names.

    image_size_c: Optional[int]
        Channel dimension size.

    image_size_t: Optional[int]
        Time dimension size.

    image_size_x: Optional[int]
        Spatial X dimension size.

    image_size_y: Optional[int]
        Spatial Y dimension size.

    image_size_z: Optional[int]
        Spatial Z dimension size.

    imaged_by: Optional[str]
        The experimentalist who produced this data.

    imaging_date: Optional[str]
        Date this file was imaged.

    objective: Optional[str]
        Objective.

    pixel_size_x: Optional[float]
        Physical pixel size along X.

    pixel_size_y: Optional[float]
        Physical pixel size along Y.

    pixel_size_z: Optional[float]
        Physical pixel size along Z.

    position_index: Optional[int]
        Position index, if applicable.

    row: Optional[str]
        Row information.

    timelapse: Optional[bool]
        Is the data a timelapse?

    timelapse_interval: Optional[timedelta]
        Average time interval between timepoints.

    total_time_duration: Optional[timedelta]
        Total time duration of imaging, measured from the beginning of the first
        time point to the beginning of the final time point.

    FIELD_LABELS: dict[str, str]
        Mapping of the above attribute names to readable labels.
    """

    binning: Optional[str] = None
    column: Optional[str] = None
    dimensions_present: Optional[Sequence[str]] = None
    image_size_c: Optional[int] = None
    image_size_t: Optional[int] = None
    image_size_x: Optional[int] = None
    image_size_y: Optional[int] = None
    image_size_z: Optional[int] = None
    imaged_by: Optional[str] = None
    imaging_datetime: Optional[datetime] = None
    objective: Optional[str] = None
    pixel_size_x: Optional[float] = None
    pixel_size_y: Optional[float] = None
    pixel_size_z: Optional[float] = None
    position_index: Optional[int] = None
    row: Optional[str] = None
    timelapse: Optional[bool] = None
    timelapse_interval: Optional[timedelta] = None
    total_time_duration: Optional[timedelta] = None

    FIELD_LABELS = {
        "binning": "Binning",
        "column": "Column",
        "dimensions_present": "Dimensions Present",
        "image_size_c": "Image Size C",
        "image_size_t": "Image Size T",
        "image_size_x": "Image Size X",
        "image_size_y": "Image Size Y",
        "image_size_z": "Image Size Z",
        "imaged_by": "Imaged By",
        "imaging_datetime": "Imaging Datetime",
        "objective": "Objective",
        "pixel_size_x": "Pixel Size X",
        "pixel_size_y": "Pixel Size Y",
        "pixel_size_z": "Pixel Size Z",
        "position_index": "Position Index",
        "row": "Row",
        "timelapse": "Timelapse",
        "timelapse_interval": "Timelapse Interval",
        "total_time_duration": "Total Time Duration",
    }

    def to_dict(self) -> dict:
        """
        Convert the metadata into a dictionary using readable labels.

        Returns:
            dict: A mapping where keys are the readable labels defined in FIELD_LABELS,
                  and values are the corresponding metadata values.
        """
        return {
            self.FIELD_LABELS[field]: getattr(self, field)
            for field in self.FIELD_LABELS
        }


def binning(ome: OME) -> Optional[str]:
    """
    Extracts the binning setting from the OME metadata.

    Returns
    -------
    Optional[str]
        The binning setting as a string. Returns None if not found.
    """
    try:
        # DetectorSettings under each Channel holds the binning info
        channels = ome.images[0].pixels.channels or []
        for channel in channels:
            ds = channel.detector_settings
            if ds and ds.binning:
                return str(ds.binning.value)
    except Exception as exc:
        log.warning("Failed to extract Binning setting: %s", exc, exc_info=True)
    return None


def imaged_by(ome: OME) -> Optional[str]:
    """
    Extracts the name of the experimenter (user who imaged the sample).

    Returns
    -------
    Optional[str]
        The username of the experimenter. Returns None if not found.
    """
    try:
        img = ome.images[0]
        # Prefer explicit ExperimenterRef if present
        if img.experimenter_ref and ome.experimenters:
            exp = next(
                (e for e in ome.experimenters if e.id == img.experimenter_ref.id), None
            )
            if exp and exp.user_name:
                return exp.user_name
        # Fallback to first Experimenter
        if ome.experimenters:
            return ome.experimenters[0].user_name
    except Exception as exc:
        log.warning("Failed to extract Imaged By: %s", exc, exc_info=True)
    return None


def imaging_datetime(ome: OME) -> Optional[datetime]:
    """
    Extracts the acquisition datetime from the OME metadata.

    Returns
    -------
    Optional[datetime]
        The acquisition datetime as provided in the metadata,
        including its original timezone.

        None: if the acquisition datetime is not found or cannot be parsed.
    """
    try:
        img = ome.images[0]
        acq = img.acquisition_date
        return acq
    except Exception as exc:
        log.warning("Failed to extract Acquisition Datetime: %s", exc, exc_info=True)
        return None


def objective(ome: OME) -> Optional[str]:
    """
    Extracts the microscope objective details.

    Returns
    -------
    Optional[str]
        The formatted objective magnification and numerical aperture.
        Returns the raw string (e.g. "40x/1.2W").
    """
    try:
        img = ome.images[0]
        instrs = ome.instruments or []
        instr = None
        # Prefer explicit InstrumentRef
        if img.instrument_ref:
            instr = next((i for i in instrs if i.id == img.instrument_ref.id), None)
        # Fallback to first Instrument
        if not instr and instrs:
            instr = instrs[0]
        if instr and instr.objectives:
            obj = instr.objectives[0]
            mag = round(float(obj.nominal_magnification))
            na = obj.lens_na
            imm = obj.immersion.value if obj.immersion else ""
            raw_obj = f"{mag}x/{na}{imm}"
            return raw_obj
    except Exception as exc:
        log.warning("Failed to extract Objective: %s", exc, exc_info=True)
    return None


def _convert_to_timedelta(delta_t: float, unit: Optional[UnitsTime]) -> timedelta:
    """
    Converts delta_t to a timedelta object based on the provided unit.
    """
    if unit is None:
        # Assume seconds if unit is None
        return timedelta(seconds=delta_t)

    unit_value = unit.value  # Access the string representation of the enum

    if unit_value == "ms":
        return timedelta(milliseconds=delta_t)
    elif unit_value == "µs":
        return timedelta(microseconds=delta_t)
    elif unit_value == "ns":
        return timedelta(microseconds=delta_t / 1000.0)
    else:
        # Default to seconds for unrecognized units
        log.warning("No units found for timedelta, defaulting to seconds.")
        return timedelta(seconds=delta_t)


def total_time_duration(ome: OME, scene_index: int) -> Optional[timedelta]:
    """
    Computes the total time duration from the beginning of the first
    timepoint to the beginning of the final timepoint.
    """
    try:
        image = ome.images[scene_index]
        planes = image.pixels.planes

        # Initialize variables to track the maximum the_t and corresponding plane
        max_t = -1
        target_plane = None

        for p in planes:
            if p.the_z == 0 and p.the_c == 0 and p.the_t is not None:
                if p.the_t > max_t:
                    max_t = p.the_t
                    target_plane = p

        if target_plane is None or target_plane.delta_t is None:
            return None

        return _convert_to_timedelta(target_plane.delta_t, target_plane.delta_t_unit)
    except Exception:
        return None


def timelapse_interval(ome: OME, scene_index: int) -> Optional[timedelta]:
    """
    Computes the average time interval between consecutive timepoints.
    """
    try:
        image = ome.images[scene_index]
        size_t = image.pixels.size_t
        if size_t is None or size_t < 2:
            return None

        total_duration = total_time_duration(ome, scene_index)
        if total_duration is None:
            return None

        return total_duration / (size_t - 1)
    except Exception:
        return None

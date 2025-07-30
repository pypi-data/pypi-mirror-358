import logging
from math import ceil
from typing import Optional
from matchms.typing import SpectrumType


logger = logging.getLogger("matchms")


def require_minimum_number_of_peaks(
    spectrum_in: SpectrumType,
    n_required: int = 10,
    ratio_required: Optional[float] = None,
    clone: Optional[bool] = True,
) -> Optional[SpectrumType]:
    """Spectrum will be set to None when it has fewer peaks than required.

    Parameters
    ----------
    spectrum_in:
        Input spectrum.
    n_required:
        Number of minimum required peaks. Spectra with fewer peaks will be set
        to 'None'.
    ratio_required:
        Set desired ratio between minimum number of peaks and parent mass.
        Default is None.
    clone:
        Optionally clone the Spectrum.

    Returns
    -------
    Spectrum or None
        Untouched Spectrum or 'None'.
    """
    if spectrum_in is None:
        return None

    spectrum = spectrum_in.clone() if clone else spectrum_in

    parent_mass = spectrum.get("parent_mass", None)
    if parent_mass and ratio_required:
        n_required_by_mass = int(ceil(ratio_required * parent_mass))
        threshold = max(n_required, n_required_by_mass)
    else:
        threshold = n_required

    if spectrum.peaks.intensities.size < threshold:
        logger.info(
            "Spectrum with %s (<%s) peaks was set to None.", str(spectrum.peaks.intensities.size), str(threshold)
        )
        return None

    return spectrum

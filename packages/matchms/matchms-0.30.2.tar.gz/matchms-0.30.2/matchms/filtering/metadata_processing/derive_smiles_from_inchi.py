import logging
from typing import Optional
from matchms.filtering.filter_utils.smile_inchi_inchikey_conversions import (
    convert_inchi_to_smiles,
    is_valid_inchi,
    is_valid_smiles,
)
from matchms.typing import SpectrumType


logger = logging.getLogger("matchms")


def derive_smiles_from_inchi(spectrum_in: SpectrumType, clone: Optional[bool] = True) -> Optional[SpectrumType]:
    """Find missing smiles and derive from Inchi where possible.

    Parameters
    ----------
    spectrum_in:
        Input spectrum.
    clone:
        Optionally clone the Spectrum.#

    Returns
    -------
    Spectrum or None
        Spectrum with added SMILES, or `None` if not present.
    """
    if spectrum_in is None:
        return None

    spectrum = spectrum_in.clone() if clone else spectrum_in
    inchi = spectrum.get("inchi")
    smiles = spectrum.get("smiles")

    if not is_valid_smiles(smiles) and is_valid_inchi(inchi):
        smiles = convert_inchi_to_smiles(inchi)
        if smiles:
            smiles = smiles.rstrip()
            spectrum.set("smiles", smiles)
            logger.info("Added smiles %s to metadata (was converted from InChI)", smiles)
        else:
            logger.warning("Could not convert InChI %s to smiles.", inchi)

    return spectrum

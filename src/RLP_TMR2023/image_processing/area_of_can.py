import numpy as np
import numpy.typing as npt

from RLP_TMR2023.image_processing.image_filtering import otsu_filtering


def get_area_of_can(image: npt.NDArray[np.uint8]) -> int:
    otsu_filtered = otsu_filtering(image)

    return np.count_nonzero(otsu_filtered)

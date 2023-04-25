import cv2
import numpy as np
import numpy.typing as npt

from RLP_TMR2023.image_processing.blue_filter import blue_filter
from RLP_TMR2023.constants.color_filters import BLUE_LOWER_HSV, BLUE_UPPER_HSV


def trimmer_image(image: npt.NDArray[np.uint8], percentage_trimmed: int) -> npt.NDArray[np.uint8]:
    """
    Cut the image to only show the blue part

    """
    percentage_crop = int(percentage_trimmed * 480 / 100)
    blue_image = blue_filter(image)
    cropped_image = blue_image[percentage_crop:480, 0:640]
    return cropped_image  # type: ignore


def check_water(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Check if the water is present in the image

    """
    new_image = trimmer_image(image, 80)
    # make binarize render in white and black
    mask = cv2.inRange(new_image, BLUE_LOWER_HSV, BLUE_UPPER_HSV)
    output = cv2.bitwise_and(new_image, new_image, mask=mask)
    # count the number of white pixels
    ratio_water = cv2.countNonZero(mask) / (image.size / 3)
    color_percent = (ratio_water * 100) / .3
    return output, color_percent


def main():
    camera = cv2.VideoCapture(0)
    while True:
        _, img = camera.read()
        img = cv2.flip(img, 1)

        cut_image = trimmer_image(img, 80)

        water_image = check_water(img)

        cv2.imshow("Original", img)
        cv2.imshow("Cut and filtered blue", cut_image)
        cv2.imshow("Water", water_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()

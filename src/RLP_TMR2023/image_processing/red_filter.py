import cv2
import numpy as np
import numpy.typing as npt

from RLP_TMR2023.constants.color_filters import RED_LOWER_HSV, RED_UPPER_HSV
from RLP_TMR2023.image_processing.image_filtering import hsv_filter


def red_filter(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Filter an image using blue HSV params

    :param image: The image to filter
    :return: The filtered image
    """

    # lower = np.array([0, 20, 0])
    # upper = np.array([50, 255, 255])
    lower = np.array(RED_LOWER_HSV)
    upper = np.array(RED_UPPER_HSV)

    return hsv_filter(image, lower, upper, 5)  # type: ignore


def main():
    camera = cv2.VideoCapture(0)
    while True:
        _, img = camera.read()
        img = cv2.flip(img, 1)

        red_image = red_filter(img)

        cv2.imshow("Original", img)
        cv2.imshow("Filtered red", red_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()

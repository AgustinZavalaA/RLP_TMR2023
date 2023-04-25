import cv2
import numpy as np
import numpy.typing as npt

from image_filtering import hsv_filter


def blue_filter(image: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    Filter an image using blue HSV params

    :param image: The image to filter
    :return: The filtered image
    """

    # lower = np.array([0, 20, 0])
    # upper = np.array([50, 255, 255])
    lower = np.array([69, 37, 0])
    upper = np.array([134, 255, 255])

    return hsv_filter(image, lower, upper, 5)


def main():
    camera = cv2.VideoCapture(0)
    while True:
        _, img = camera.read()
        img = cv2.flip(img, 1)

        blue_image = blue_filter(img)

        cv2.imshow("Original", img)
        cv2.imshow("Filtered blue", blue_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()

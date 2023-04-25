import cv2
import numpy as np
import numpy.typing as npt

from blue_filter import blue_filter


def trimmer_image(image: npt.NDArray[np.uint8], percentage: int) -> npt.NDArray[np.uint8]:
    """
    Cut the image to only show the blue part

    """
    percentage_crop = int(percentage * 480 / 100)
    print(percentage_crop)
    blue_image = blue_filter(image)
    cropped_image = blue_image[percentage_crop:480, 0:640]
    return cropped_image


def main():
    camera = cv2.VideoCapture(0)
    while True:
        _, img = camera.read()
        img = cv2.flip(img, 1)

        cut_image = trimmer_image(img, 80)

        cv2.imshow("Original", img)
        cv2.imshow("Cut and filtered blue", cut_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()
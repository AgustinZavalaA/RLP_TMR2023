import cv2
import numpy as np
import numpy.typing as npt

from RLP_TMR2023.image_processing.blue_filter import blue_filter


def trimmer_image(image: npt.NDArray[np.uint8], percentage_trimmed: int) -> npt.NDArray[np.uint8]:
    """
    Cut the image to only show the blue part

    """
    percentage_crop = int(percentage_trimmed * 480 / 100)
    blue_image = blue_filter(image)
    cropped_image = blue_image[percentage_crop:480, 0:640]
    return cropped_image  # type: ignore


def check_water_percentage(image: npt.NDArray[np.uint8]) -> float:
    """
    Check if the water is present in the image
    """
    new_image = trimmer_image(image, 80)
    # count the number of white pixels
    ratio_water = cv2.countNonZero(new_image) / (image.size / 3)
    color_percent = (ratio_water * 100) / .3
    return float(color_percent)  # type: ignore


def check_is_water(image_percentage: float) -> bool:
    if image_percentage > 50:
        return True
    else:
        return False


def main():
    camera = cv2.VideoCapture(0)
    while True:
        _, img = camera.read()
        img = cv2.flip(img, 1)

        cut_image = trimmer_image(img, 80)

        water_image = check_water_percentage(img)

        water_percentage = check_is_water(water_image)

        cv2.imshow("Original", img)
        cv2.imshow("Cut and filtered blue", cut_image)
        print(f"percentage color: {water_image} %")
        print(f"percentage: {type(water_percentage)}", water_percentage)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()

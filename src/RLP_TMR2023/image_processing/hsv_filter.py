import cv2
import numpy as np
import numpy.typing as npt


def hsv_filter(image: npt.NDArray[np.uint8], lower: npt.NDArray[np.uint8], upper: npt.NDArray[np.uint8],
               kernel_size: int) -> npt.NDArray[np.uint8]:
    """
    Filter an image using HSV color space

    :param image: The image to filter
    :param lower: The lower bound of the filter
    :param upper: The upper bound of the filter
    :param kernel_size: The size of the kernel to use for morphological operations
    :return: The filtered image
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    filtered = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((kernel_size, kernel_size), "uint8")
    filtered: npt.NDArray[np.uint8] = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
    filtered: npt.NDArray[np.uint8] = cv2.dilate(filtered, kernel, iterations=1)

    return filtered


def main():
    camera = cv2.VideoCapture(0)

    nothing = lambda x: None

    cv2.namedWindow('marking')

    cv2.createTrackbar('H Lower', 'marking', 0, 179, nothing)
    cv2.createTrackbar('H Higher', 'marking', 179, 179, nothing)
    cv2.createTrackbar('S Lower', 'marking', 0, 255, nothing)
    cv2.createTrackbar('S Higher', 'marking', 255, 255, nothing)
    cv2.createTrackbar('V Lower', 'marking', 0, 255, nothing)
    cv2.createTrackbar('V Higher', 'marking', 255, 255, nothing)
    cv2.createTrackbar('Kernel', 'marking', 1, 7, nothing)

    while True:
        _, img = camera.read()
        img = cv2.flip(img, 1)

        img = cv2.imread("/home/agustin/Downloads/can.jpg")

        h_l = cv2.getTrackbarPos('H Lower', 'marking')
        h_h = cv2.getTrackbarPos('H Higher', 'marking')
        s_l = cv2.getTrackbarPos('S Lower', 'marking')
        s_h = cv2.getTrackbarPos('S Higher', 'marking')
        v_l = cv2.getTrackbarPos('V Lower', 'marking')
        v_h = cv2.getTrackbarPos('V Higher', 'marking')

        lower_region = np.array([h_l, s_l, v_l], np.uint8)
        upper_region = np.array([h_h, s_h, v_h], np.uint8)
        kernel_size = cv2.getTrackbarPos('Kernel', 'marking')

        red = hsv_filter(img, lower_region, upper_region, kernel_size)

        res1 = cv2.bitwise_and(img, img, mask=red)

        cv2.imshow("Masking ", res1)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            print(f"{lower_region=}, {upper_region=}, {kernel_size=}")
            break


if __name__ == "__main__":
    main()

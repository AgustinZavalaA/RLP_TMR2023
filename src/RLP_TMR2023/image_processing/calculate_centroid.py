import numpy as np
import cv2
import numpy.typing as npt

from hsv_filter_JQ import otsu
from dataclasses import dataclass


@dataclass
class BoundingBox:
    """
    Bounding box of an object detected by the model
    All coordinates are relative to the center of the image
    """
    x: float
    y: float
    width: float
    height: float


@dataclass
class Detection:
    category: str
    score: float
    bounding_box: BoundingBox


def draw_br_and_centroid(filtered_image: npt.NDArray[np.uint8], out) -> list[tuple[Detection, tuple[int, int]]]:
    contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    print(contours)
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(out, [box], 0, (0, 0, 255), 2)

        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        cv2.circle(out, (cx, cy), 5, (255, 0, 255), -1)

        detections.append((Detection(category="Can", score=1, bounding_box=rect), (cx, cy)))
    return detections


def calculate_bounding_rect_and_centroid(filtered_image: npt.NDArray[np.uint8]) -> \
        list[tuple[Detection, tuple[int, int]]]:
    contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    center_width, center_height = filtered_image.shape[1] // 2, filtered_image.shape[0] // 2

    for cnt in contours:
        # rect = cv2.minAreaRect(cnt)
        x, y, w, h = cv2.boundingRect(cnt)

        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        detection = Detection(category="Can", score=1,
                              bounding_box=BoundingBox(x=cx - center_width, y=cy - center_height, width=w, height=h))
        detections.append((detection, (cx, cy)))

    return detections


def biggest_rect_strategy(detections: list[tuple[Detection, tuple[int, int]]]) -> list[
    tuple[Detection, tuple[int, int]]]:
    biggest_can = max(detections, key=lambda x: x[0].bounding_box.width * x[0].bounding_box.height)
    return [biggest_can]


def closest_centroid_to_middle_strategy(detections: list[tuple[Detection, tuple[int, int]]]) -> list[
    tuple[Detection, tuple[int, int]]]:
    closest_can = min(detections, key=lambda x: x[0].bounding_box.x)
    return [closest_can]


def can_candidates(filtered_image: npt.NDArray[np.uint8], strategy) -> list[tuple[Detection, tuple[int, int]]]:
    detections = calculate_bounding_rect_and_centroid(filtered_image)

    return strategy(detections)


def main():
    camera = cv2.VideoCapture(0)
    while True:
        _, img = camera.read()
        # img = cv2.flip(img, 1)

        img = cv2.imread("/home/yisus/Documents/Codes/Python/RLP_TMR2023/src/RLP_TMR2023/temp_can_directory/black_can"
                         ".jpeg")

        filtered_img = otsu(img)

        draw_br_and_centroid(filtered_img, img)
        print(can_candidates(filtered_img, biggest_rect_strategy))
        print(can_candidates(filtered_img, closest_centroid_to_middle_strategy))
        print()

        cv2.imshow("Original", img)
        cv2.imshow("Filtered", filtered_img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    main()

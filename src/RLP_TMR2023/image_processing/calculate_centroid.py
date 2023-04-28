from typing import Callable

import cv2
import numpy as np
import numpy.typing as npt

from RLP_TMR2023.common_types.common_types import BoundingBox, Detection
from RLP_TMR2023.image_processing.image_filtering import otsu_filtering


def draw_br_and_centroid(filtered_image: npt.NDArray[np.uint8], out) -> list[tuple[Detection, tuple[int, int]]]:
    contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(out, [box], 0, (0, 0, 255), 2)

        m = cv2.moments(cnt)
        if m["m00"] == 0:
            continue
        cx = int(m["m10"] / m["m00"])
        cy = int(m["m01"] / m["m00"])

        cv2.circle(out, (cx, cy), 5, (255, 0, 255), -1)
        # TODO: remove Detection return
        detections.append((Detection(category="Can", score=1, bounding_box=rect, frame_height=1, frame_width=1,
                                     approx_size=1), (cx, cy)))
    return detections


def calculate_bounding_rect_and_centroid(filtered_image: npt.NDArray[np.uint8]) -> \
        list[tuple[Detection, tuple[int, int]]]:
    contours, hierarchy = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []

    for cnt in contours:
        # rect = cv2.minAreaRect(cnt)
        x, y, w, h = cv2.boundingRect(cnt)

        moments = cv2.moments(cnt)
        if moments["m00"] == 0:
            continue
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])

        # TODO: remove unused detection
        detection = Detection(category="Can", score=1,
                              bounding_box=BoundingBox(x=cx, y=cy, width=w, height=h),
                              frame_width=1, frame_height=1, approx_size=1)
        detections.append((detection, (cx, cy)))

    return detections


def biggest_rect_strategy(detections: list[tuple[Detection, tuple[int, int]]]) -> \
        list[tuple[Detection, tuple[int, int]]]:
    biggest_can = max(detections, key=lambda x: x[0].bounding_box.width * x[0].bounding_box.height)
    return [biggest_can]


def closest_centroid_to_middle_strategy(detections: list[tuple[Detection, tuple[int, int]]]) -> \
        list[tuple[Detection, tuple[int, int]]]:
    closest_can = min(detections, key=lambda x: x[0].bounding_box.x)
    return [closest_can]


def can_candidates(filtered_image: npt.NDArray[np.uint8],
                   strategy:
                   Callable[[list[tuple[Detection, tuple[int, int]]]], list[tuple[Detection, tuple[int, int]]]]) -> \
        list[tuple[Detection, tuple[int, int]]]:
    detections = calculate_bounding_rect_and_centroid(filtered_image)

    return strategy(detections)


def main():
    camera = cv2.VideoCapture(0)
    while True:
        _, img = camera.read()
        img = cv2.flip(img, 1)

        filtered_img = otsu_filtering(img)

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

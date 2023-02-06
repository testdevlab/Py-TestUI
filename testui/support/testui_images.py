import os
import threading
import time

import cv2
import numpy as np
import imutils

from testui.support import logger

found_image = False
matched = 0.0
matching_list = []


def compare_video_image(
    video,
    comparison,
    threshold,
    image_match,
    frame_rate_reduction=1,
    max_scale=2.0,
    path=""
):
    global matching_list
    global matched
    global found_image

    found_image = False
    matched = 0.0
    matching_list = []

    root_dir = path
    logger.log(root_dir)
    cap = cv2.VideoCapture(os.path.join(root_dir, video))
    template = cv2.imread(os.path.join(root_dir, comparison))
    i = 0
    percentage = 0.0
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret and i % frame_rate_reduction == 0:
            logger.log(f"frame evaluation = {i}")
            found, percentage = __compare(
                frame, template, threshold, image_match, root_dir, max_scale, 0.1, 50
            )
            if found:
                cap.release()
                logger.log(f"Match found in the {i}th frame of the video")
                return True, percentage
        elif not ret:
            break
        # sleep(frame_rate_reduction)
        i += 1
    cap.release()
    return False, percentage


def __compare(
    image,
    template,
    threshold: float,
    image_match: str,
    root_dir: str,
    max_scale: float,
    min_scale=0.1,
    divisions=25
):
    (tH, tW) = template.shape[:2]
    # loop over the scales of the image
    found = None
    global found_image
    global matched
    global matching_list
    maxVal = 0.0
    for scale in np.linspace(min_scale, max_scale, divisions)[::-1]:
        # resize the image according to the scale, and keep track of the ratio
        # of the resizing.
        resized = imutils.resize(image, width=int(image.shape[1] * scale))
        r = image.shape[1] / float(resized.shape[1])
        # if the resized image is smaller than the template, then break from
        # the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break
        result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        # if we have found a new maximum correlation value, then update the
        # bookkeeping variable
        if found is None or maxVal > found[0]:
            lock = threading.Lock()
            lock.acquire()
            if found_image:
                lock.release()
                return True, matched
            matching_list.append(maxVal)
            lock.release()
            found = (maxVal, maxLoc, r)
            if maxVal > threshold:
                if image_match != "" and found is not None:
                    # unpack the bookkeeping variable and compute the (x, y)
                    # coordinates of the bounding box based on the resized ratio
                    (_, maxLoc, r) = found
                    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
                    (endX, endY) = (
                        int((maxLoc[0] + tW) * r),
                        int((maxLoc[1] + tH) * r),
                    )
                    # draw a bounding box around the detected result and display
                    # the image
                    cv2.rectangle(
                        image, (startX, startY), (endX, endY), (0, 0, 255), 2
                    )
                    cv2.imwrite(os.path.join(root_dir, image_match), image)
                    logger.log(os.path.join(root_dir, image_match))
                lock.acquire()
                found_image = True
                lock.release()
                matched = maxVal
                return True, maxVal
    matched = max(matching_list)
    return False, matched


def compare_images(
    original: str,
    comparison: str,
    threshold=0.9,
    image_match="",
    max_scale=2.0,
    min_scale=0.3,
    path=""
):
    # Read the images from the file
    global found_image
    global matched
    global matching_list

    start = time.time()
    matched = 0.0
    matching_list = []
    found_image = False
    root_dir = path
    if not os.path.exists(comparison):
        comparison = os.path.join(root_dir, comparison)
        if not os.path.exists(comparison):
            raise Exception(f"There is no image in {comparison}")
    if not os.path.exists(original):
        original = os.path.join(root_dir, original)
        if not os.path.exists(original):
            raise Exception(f"There is no image in {original}")
    template = cv2.imread(comparison)
    image = cv2.imread(original)
    # loop over the scales of the image
    threads = []
    parts = max_scale / 5.0
    min_scale = min(min_scale, parts)

    threads.append(
        threading.Thread(
            target=__compare,
            args=(
                image,
                template,
                threshold,
                image_match,
                root_dir,
                parts,
                min_scale,
            ),
        )
    )
    threads.append(
        threading.Thread(
            target=__compare,
            args=(
                image,
                template,
                threshold,
                image_match,
                root_dir,
                parts * 2.0,
                parts,
            ),
        )
    )
    threads.append(
        threading.Thread(
            target=__compare,
            args=(
                image,
                template,
                threshold,
                image_match,
                root_dir,
                parts * 3.0,
                parts * 2.0,
            ),
        )
    )
    threads.append(
        threading.Thread(
            target=__compare,
            args=(
                image,
                template,
                threshold,
                image_match,
                root_dir,
                parts * 4.0,
                parts * 3.0,
            ),
        )
    )
    threads.append(
        threading.Thread(
            target=__compare,
            args=(
                image,
                template,
                threshold,
                image_match,
                root_dir,
                parts * 5.0,
                parts * 4.0,
            ),
        )
    )
    for thread in threads:
        thread.start()
    while not found_image:
        alive = False
        for thread in threads:
            if thread.is_alive():
                alive = True
        if not alive:
            break

    logger.log(f"Image recognition took {time.time() - start}s")
    return found_image, max(matching_list)


def get_point_match(
    original: str, comparison: str, threshold=0.9, device_name="Device"
):
    _ = device_name

    # Read the images from the file
    template = cv2.imread(comparison)
    (tH, tW) = template.shape[:2]
    image = cv2.imread(original)
    found = None
    # loop over the scales of the image
    for scale in np.linspace(0.2, 2.0, 30)[::-1]:
        # resize the image according to the scale, and keep track of the ratio
        # of the resizing
        resized = imutils.resize(image, width=int(image.shape[1] * scale))
        r = image.shape[1] / float(resized.shape[1])
        # if the resized image is smaller than the template, then break from
        # the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break
        result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        # if we have found a new maximum correlation value, then update the
        # bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
            if maxVal > threshold:
                break

    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

    return startX + (endX - startX) // 2, startY + (endY - startY) // 2


def draw_match(
    original: str, comparison: str, threshold=0.9, device_name="Device"
):
    method = cv2.TM_CCOEFF_NORMED

    # Read the images from the file
    large_image = cv2.imread(comparison)
    small_image = cv2.imread(original)

    logger.log_debug(
        f'{device_name}: Comparing "{original}" with "{comparison}"'
    )
    res = cv2.matchTemplate(small_image, large_image, method)

    loc = np.where(res >= threshold)
    _, w, h = large_image.shape[::-1]
    # For each match...
    suh = None
    for pt in zip(*loc[::-1]):
        suh = cv2.rectangle(
            small_image, pt, (pt[0] + w, pt[1] + h), (0, 66, 255), 1
        )
    cv2.imwrite("something.png", suh)


def size(image_path):
    img = cv2.imread(image_path)
    height, width, _ = img.shape
    return width, height


class ImageRecognition:
    def __init__(
        self, original: str, comparison="", threshold=0.9, device_name="Device", path=""
    ):
        self.__original = original
        self.__comparison = comparison
        self.__threshold = threshold
        self.__device_name = device_name
        if path == "":
            path = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
        self.__path = path

    def compare(self, image_match="", max_scale=2.0, min_scale=0.3):
        _, p1 = compare_images(
            self.__original,
            self.__comparison,
            self.__threshold,
            image_match,
            max_scale,
            min_scale,
            self.__path
        )
        if self.__threshold > p1:
            logger.log_debug(
                f"{self.__device_name}: Image match not found between: "
                f"{self.__original} and {self.__comparison}. "
                f"Threshold={self.__threshold}, matched = {p1}"
            )
            return False, p1

        logger.log_debug(
            f"{self.__device_name}: Image match found between: "
            f"{self.__original} and {self.__comparison}. "
            f"Threshold={self.__threshold}, matched = {p1}"
        )
        return True, p1

    def compare_video(
        self, image_match="", frame_rate_reduction=1, max_scale=2.0
    ):
        found, p = compare_video_image(
            self.__original,
            self.__comparison,
            self.__threshold,
            image_match,
            frame_rate_reduction,
            max_scale,
            self.__path
        )
        if found:
            logger.log_debug(
                f"{self.__device_name}: Image match found between "
                f"video: {self.__original} and image {self.__comparison}. "
                f"Threshold={self.__threshold}, matched = {p}"
            )
            return True

        logger.log_debug(
            f"{self.__device_name}: Image match not found between "
            f"video: {self.__original} and image {self.__comparison}. "
            f"Threshold={self.__threshold}, matched = {p}"
        )
        return False

    def get_middle_point(self):
        get_point_match(
            self.__original,
            self.__comparison,
            self.__threshold,
            self.__device_name,
        )
        return self

    def draw_image_match(self):
        draw_match(
            self.__original,
            self.__comparison,
            self.__threshold,
            self.__device_name,
        )
        return self

    def image_original_size(self):
        path = self.__original
        if self.__path != "":
            path = os.path.join(self.__path, self.__original)
        logger.log(f"Checking size of image: {path}")
        size_image = size(path)
        logger.log(f"The size of the image is {size_image}")
        return Dimensions(size_image[0], size_image[1])

    def image_comparison_size(self):
        size_image = size(self.__comparison)
        logger.log(f"The size of the image is {size_image}")
        return Dimensions(size_image[0], size_image[1])

    def crop_original_image(
        self, center_x, center_y, width, height, image_name="cropped_image.png"
    ):
        # Read the images from the file
        path = os.path.join(self.__path, self.__original)
        img = cv2.imread(path)
        y = center_y - height // 2
        if y < 0:
            y *= -1
        x = center_x - width // 2
        if x < 0:
            x *= -1
        img_2 = img[y:y + height, x:x + width]
        cv2.imwrite(image_name, img_2)
        return self


class Dimensions:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
    path="",
):
    """
    Compare an image to a video and return the percentage of similarity
    :param video: the video to compare
    :param comparison: the image to compare
    :param threshold: the threshold of similarity
    :param image_match: the image to save if a match is found
    :param frame_rate_reduction: the frame rate reduction
    :param max_scale: the maximum scale of the image
    :return: True if a match is found, False otherwise
    """
    global matching_list
    global matched
    global found_image

    found_image = False
    matched = 0.0
    matching_list = []

    root_dir = path
    logger.log_debug(f"root directory: {root_dir}")
    cap = cv2.VideoCapture(os.path.join(root_dir, video))
    template = cv2.imread(os.path.join(root_dir, comparison))
    if template is None:
        logger.log_warn(
            "trying to compare with an image that doesn't exist!"
            f"{os.path.join(root_dir, comparison)}"
        )
        return False, 0.0
    i = 0
    percentage = 0.0
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret and i % frame_rate_reduction == 0:
            logger.log(f"frame evaluation = {i}")
            found, percentage = __compare(
                frame,
                template,
                threshold,
                image_match,
                root_dir,
                max_scale,
                0.1,
                50,
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
    divisions=25,
):
    """
    Compare a template image to a larger image and return the percentage of
    similarity
    :param image: the larger image
    :param template: the template image
    :param threshold: the threshold of similarity
    :param image_match: the image to save if a match is found
    :param root_dir: the root directory of the project
    :param max_scale: the maximum scale of the image
    :param min_scale: the minimum scale of the image
    :return: True if a match is found, False otherwise
    """
    (tH, tW) = template.shape[:2]
    # loop over the scales of the image
    found = None
    global found_image
    global matched
    global matching_list
    max_val = 0.0
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
        (_, max_val, _, max_loc) = cv2.minMaxLoc(result)
        # if we have found a new maximum correlation value, then update the
        # bookkeeping variable
        if found is None or max_val > found[0]:
            lock = threading.Lock()
            lock.acquire()
            if found_image:
                lock.release()
                return True, matched
            matching_list.append(max_val)
            lock.release()
            found = (max_val, max_loc, r)
            if max_val > threshold:
                if image_match != "" and found is not None:
                    # unpack the bookkeeping variable and compute the (x, y)
                    # coordinates of the bounding box based on the resized ratio
                    (_, max_loc, r) = found
                    (start_x, start_y) = (
                        int(max_loc[0] * r),
                        int(max_loc[1] * r),
                    )
                    (end_x, end_y) = (
                        int((max_loc[0] + tW) * r),
                        int((max_loc[1] + tH) * r),
                    )
                    # draw a bounding box around the detected result and display
                    # the image
                    cv2.rectangle(
                        image,
                        (start_x, start_y),
                        (end_x, end_y),
                        (0, 0, 255),
                        2,
                    )
                    cv2.imwrite(os.path.join(root_dir, image_match), image)
                    logger.log(os.path.join(root_dir, image_match))
                lock.acquire()
                found_image = True
                lock.release()
                matched = max_val
                return True, max_val
    matched = max(matching_list)
    return False, matched


def compare_images(
    original: str,
    comparison: str,
    threshold=0.9,
    image_match="",
    max_scale=2.0,
    min_scale=0.3,
    path="",
):
    """
    Compare two images and return a boolean if they are similar or not
    :param original: The original image
    :param comparison: The image to compare
    :param threshold: The threshold to compare the images
    :param image_match: The image to save the match
    :param max_scale: The maximum scale to compare the images
    :param min_scale: The minimum scale to compare the images
    :return: A boolean if the images are similar or not
    """
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
    """
    Get the point where the images match. If the images don't match, return None
    :param original: The original image
    :param comparison: The image to compare to
    :param threshold: The threshold to match the images
    :param device_name: The device name
    :return: The point where the images match
    """
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
        (_, max_val, _, max_loc) = cv2.minMaxLoc(result)
        # if we have found a new maximum correlation value, then update the
        # bookkeeping variable
        if found is None or max_val > found[0]:
            found = (max_val, max_loc, r)
            if max_val > threshold:
                break

    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (_, max_loc, r) = found
    (start_x, start_y) = (int(max_loc[0] * r), int(max_loc[1] * r))
    (end_x, end_y) = (int((max_loc[0] + tW) * r), int((max_loc[1] + tH) * r))

    return start_x + (end_x - start_x) // 2, start_y + (end_y - start_y) // 2


def draw_match(
    original: str, comparison: str, threshold=0.9, device_name="Device"
):
    """
    Draws a rectangle around the match of the two images.
    :param original: The original image
    :param comparison: The image to compare to
    :param threshold: The threshold to match the images
    :param device_name: The device name
    """
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
    """
    Gets the size of an image.
    :param image_path: The path to the image.
    :return: The width and height of the image.
    """
    img = cv2.imread(image_path)
    height, width, _ = img.shape
    return width, height


class ImageRecognition:
    """
    Class for image recognition.
    """

    def __init__(
        self,
        original: str,
        comparison="",
        threshold=0.9,
        device_name="Device",
        path="./logs",
    ):
        self.__original = original
        self.__comparison = comparison
        self.__threshold = threshold
        self.__device_name = device_name
        self.__path = path

    def compare(self, image_match="", max_scale=2.0, min_scale=0.3):
        """
        Compares the image to a given image.
        :param image_match: The image to compare to.
        :param max_scale: The maximum scale to compare the image to.
        :param min_scale: The minimum scale to compare the image to.
        :return: True if the image is found, False if not.
        """
        _, p1 = compare_images(
            self.__original,
            self.__comparison,
            self.__threshold,
            image_match,
            max_scale,
            min_scale,
            self.__path,
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
        """
        Compares the image to a video
        :param image_match: The image to match
        :param frame_rate_reduction: The frame rate reduction
        :param max_scale: The max scale
        :return: True if the image is found in the video
        """

        found, p = compare_video_image(
            self.__original,
            self.__comparison,
            self.__threshold,
            image_match,
            frame_rate_reduction,
            max_scale,
            self.__path,
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
        """
        Returns the middle point of the image match
        :return: ImageRecognition
        """
        get_point_match(
            self.__original,
            self.__comparison,
            self.__threshold,
            self.__device_name,
        )
        return self

    def draw_image_match(self):
        """
        Draws a rectangle around the image match
        :return: ImageRecognition
        """
        draw_match(
            self.__original,
            self.__comparison,
            self.__threshold,
            self.__device_name,
        )
        return self

    def image_original_size(self):
        """
        Returns the size of the original image
        :return: Dimensions
        """
        path = self.__original
        if self.__path != "":
            path = os.path.join(self.__path, self.__original)
        logger.log(f"Checking size of image: {path}")
        size_image = size(path)
        logger.log(f"The size of the image is {size_image}")
        return Dimensions(size_image[0], size_image[1])

    def image_comparison_size(self):
        """
        Returns the size of the comparison image
        :return: Dimensions
        """
        size_image = size(self.__comparison)
        logger.log(f"The size of the image is {size_image}")
        return Dimensions(size_image[0], size_image[1])

    def crop_original_image(
        self, center_x, center_y, width, height, image_name="cropped_image.png"
    ):
        """
        Crops the original image and saves it in the root directory
        :param center_x: int
        :param center_y: int
        :param width: int
        :param height: int
        :param image_name: str
        :return: ImageRecognition
        """
        # Read the images from the file
        path = os.path.join(self.__path, self.__original)
        img = cv2.imread(path)
        y = center_y - height // 2
        if y < 0:
            y *= -1
        x = center_x - width // 2
        if x < 0:
            x *= -1
        img_2 = img[y : y + height, x : x + width]
        cv2.imwrite(image_name, img_2)
        return self


class Dimensions:
    """Class to store the dimensions of an image"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

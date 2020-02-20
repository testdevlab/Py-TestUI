import os

import cv2
import numpy as np
import imutils

from testui.support import logger


def compare_video_image(video, comparison, threshold, image_match, frame_rate_reduction=1, max_scale=2.0):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cap = cv2.VideoCapture(root_dir + '/' + video)
    template = cv2.imread(root_dir + '/' + comparison)
    i = 0
    percentage = 0.0
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret and i % frame_rate_reduction == 0:
            found, percentage = __compare(frame, template, threshold, image_match, root_dir, max_scale)
            if found:
                cap.release()
                logger.log(f'Match found in the {i}th frame of the video')
                return True, percentage
        elif not ret:
            break
        # sleep(frame_rate_reduction)
        i += 1
    cap.release()
    return False, percentage


def __compare(image, template, threshold: float, image_match: str, root_dir: str, max_scale: float):
    (tH, tW) = template.shape[:2]
    # loop over the scales of the image
    found = None
    maxVal = 0.0
    for scale in np.linspace(0.1, max_scale)[::-1]:
        # resize the image according to the scale, and keep track of the ratio of the resizing
        resized = imutils.resize(image, width=int(image.shape[1] * scale))
        r = image.shape[1] / float(resized.shape[1])
        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break
        result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        # if we have found a new maximum correlation value, then update the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
            if maxVal > threshold:
                if image_match != '' and found is not None:
                    # unpack the bookkeeping variable and compute the (x, y) coordinates
                    # of the bounding box based on the resized ratio
                    (_, maxLoc, r) = found
                    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
                    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
                    # draw a bounding box around the detected result and display the image
                    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
                    cv2.imwrite(root_dir + '/' + image_match, image)
                return True, maxVal

    return False, maxVal


def compare_images(original: str, comparison: str, threshold=0.9, image_match='', max_scale=2.0):
    # Read the images from the file
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    template = cv2.imread(root_dir + '/' + comparison)
    image = cv2.imread(root_dir + '/' + original)
    # loop over the scales of the image
    return __compare(image, template, threshold, image_match, root_dir, max_scale)


def get_point_match(original: str, comparison: str, threshold=0.9, device_name='Device'):
    # Read the images from the file
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    template = cv2.imread(root_dir + '/' + comparison)
    (tH, tW) = template.shape[:2]
    image = cv2.imread(root_dir + '/' + original)
    found = None
    # loop over the scales of the image
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        # resize the image according to the scale, and keep track of the ratio of the resizing
        resized = imutils.resize(image, width=int(image.shape[1] * scale))
        r = image.shape[1] / float(resized.shape[1])
        # if the resized image is smaller than the template, then break
        # from the loop
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break
        result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        # if we have found a new maximum correlation value, then update the bookkeeping variable
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


def draw_match(original: str, comparison: str, threshold=0.9, device_name='Device'):
    method = cv2.TM_CCOEFF_NORMED

    # Read the images from the file
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    large_image = cv2.imread(root_dir + '/' + comparison)
    small_image = cv2.imread(root_dir + '/' + original)

    logger.log_debug(f'{device_name}: Comparing "{original}" with "{comparison}"')
    res = cv2.matchTemplate(small_image, large_image, method)

    loc = np.where(res >= threshold)
    null, w, h = large_image.shape[::-1]
    # For each match...
    suh = None
    for pt in zip(*loc[::-1]):
        suh = cv2.rectangle(small_image, pt, (pt[0] + w, pt[1] + h), (0, 66, 255), 1)
    cv2.imwrite('something.png', suh)


def size(image_path):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    img = cv2.imread(root_dir + '/' + image_path)
    height, width, _ = img.shape
    return width, height


class ImageRecognition(object):
    def __init__(self, original: str, comparison='', threshold=0.9, device_name='Device'):
        self.__original = original
        self.__comparison = comparison
        self.__threshold = threshold
        self.__device_name = device_name

    def compare(self, image_match='', max_scale=2.0):
        found, p1 = compare_images(
            self.__original, self.__comparison, self.__threshold, image_match, max_scale)
        if not found:
            found, p = compare_images(
                self.__comparison, self.__original, self.__threshold, image_match, max_scale)
            if found:
                logger.log_debug(f'{self.__device_name}: Image match found between: {self.__original} '
                                 f'and {self.__comparison}. Threshold={self.__threshold}, matched = {p}')
                return True, p
            else:
                if p1 > p:
                    p = p1
                logger.log_debug(f'{self.__device_name}: Image match not found between: {self.__original} '
                                 f'and {self.__comparison}. Threshold={self.__threshold}, matched = {p}')
                return False, p
        else:
            logger.log_debug(f'{self.__device_name}: Image match found between: {self.__original} '
                             f'and {self.__comparison}. Threshold={self.__threshold}, matched = {p1}')
            return True, p1

    def compare_video(self, image_match='', frame_rate_reduction=1, max_scale=2.0):
        found, p = compare_video_image(
            self.__original, self.__comparison, self.__threshold, image_match, frame_rate_reduction, max_scale
        )
        if found:
            logger.log_debug(f'{self.__device_name}: Image match found between video: {self.__original} '
                             f'and image {self.__comparison}. Threshold={self.__threshold}, matched = {p}')
            return True
        else:
            logger.log_debug(f'{self.__device_name}: Image match not found between video: {self.__original} '
                             f'and image {self.__comparison}. Threshold={self.__threshold}, matched = {p}')
            return False

    def get_middle_point(self):
        get_point_match(self.__original, self.__comparison, self.__threshold, self.__device_name)
        return self

    def draw_image_match(self):
        draw_match(self.__original, self.__comparison, self.__threshold, self.__device_name)
        return self

    def image_original_size(self):
        size_image = size(self.__original)
        logger.log(f'The size of the image is {size_image}')
        return Dimensions(size_image[0], size_image[1])

    def image_comparison_size(self):
        size_image = size(self.__comparison)
        logger.log(f'The size of the image is {size_image}')
        return Dimensions(size_image[0], size_image[1])

    def crop_original_image(self, center_x, center_y, width, height, image_name='cropped_image.png'):
        # Read the images from the file
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img = cv2.imread(root_dir + '/' + self.__original)
        y = center_y - height // 2
        if y < 0:
            y *= -1
        x = center_x - width // 2
        if x < 0:
            x *= -1
        img_2 = img[y:y + height, x:x + width]
        cv2.imwrite(root_dir + '/' + image_name, img_2)
        return self


class Dimensions(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

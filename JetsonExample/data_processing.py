#
# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import math
from PIL import Image
import numpy as np
import os



def load_label_categories(label_file_path):
    categories = [line.rstrip("\n") for line in open(label_file_path)]
    return categories


LABEL_FILE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "labels.txt"
)
ALL_CATEGORIES = load_label_categories(LABEL_FILE_PATH)

# 2026-27 Override classes, in the same order as the Roboflow dataset export /
# models/override_lite.onnx's training data.yaml. The index here IS the classID
# sent to the V5 Brain, so a mismatched order silently misclassifies - if you
# retrain on a different/reordered class list, update this file to match.
CATEGORY_NUM = len(ALL_CATEGORIES)


class PreprocessYOLO(object):
    """
    A simple class for loading images with PIL and reshaping them to the specified
    input resolution.
    """

    def __init__(self, yolo_input_resolution, channels_first=True):
        """
        Initialize with the input resolution, which will stay fixed in this sample.

        Keyword arguments:
        yolo_input_resolution -- two-dimensional tuple with the target network's (spatial)
        input resolution in HW order
        channels_first -- True for NCHW input (TensorRT/ONNX, e.g. the CUDA YOLOv11 backend),
        False for NHWC input (TFLite/Coral)
        """
        self.yolo_input_resolution = yolo_input_resolution
        self.channels_first = channels_first

    def process(self, input_image, dtype):
        """
        Load an image from the specified input array,
        and return it together with a pre-processed version required for feeding it into
        the network.

        Keyword arguments:
        input_image -- numpy array of the image to be processed
        """
        image_raw, image_resized = self._load_and_resize(input_image, dtype)
        image_preprocessed = self._shuffle_and_normalize(image_resized, dtype)
        return image_raw, image_preprocessed

    def _load_and_resize(self, input_image, dtype):
        """
        Load an image from the specified array and resize it to the input resolution.
        Return the input image before resizing as a PIL Image (required for visualization),
        and the resized image as a NumPy float array.

        Keyword arguments:
        input_image -- numpy array of the image to be loaded
        """

        image_raw = Image.fromarray(input_image)
        # Expecting yolo_input_resolution in (height, width) format, adjusting to PIL
        # convention (width, height) in PIL:
        new_resolution = (self.yolo_input_resolution[1], self.yolo_input_resolution[0])
        image_resized = image_raw.resize(new_resolution, resample=Image.BICUBIC)
        image_resized = np.array(image_resized, dtype=dtype, order="C")
        return image_raw, image_resized

    def _shuffle_and_normalize(self, image, dtype):
        """Normalize a NumPy array representing an image to the range [0, 1], and
        convert it from HWC format ("channels last") to NCHW format ("channels first"
        with leading batch dimension).

        Keyword arguments:
        image -- image as three-dimensional NumPy float array, in HWC format
        """
        if (dtype == np.float32):
            image /= 255.0
        elif (dtype == np.int8):
            image -= 128
        if self.channels_first:
            # HWC to CHW format:
            image = np.transpose(image, [2, 0, 1])
        # (C)HW to N(C)HW format
        image = np.expand_dims(image, axis=0)
        # Convert the image to row-major order, also known as "C order":
        image = np.array(image, dtype=dtype, order="C")
        return image


class PostprocessYOLO(object):
    """Post-processes the single anchor-free output tensor produced by a YOLOv11
    (Ultralytics) ONNX export.

    This replaces the previous YOLOv3 anchor-box decoder (fixed anchors, 2 grid
    scales, per-cell sigmoid decode) used by the 2025-26 Push Back model. YOLOv11's
    exported graph already outputs decoded boxes, so no anchor/grid math is needed
    here - just thresholding, coordinate scaling, and NMS.
    """

    def __init__(
        self,
        conf_threshold,
        nms_threshold,
        yolo_input_resolution,
    ):
        """Initialize with all values that will be kept when processing several frames.

        Keyword arguments:
        conf_threshold -- confidence threshold, float value between 0 and 1
        nms_threshold -- threshold for non-max suppression algorithm,
        float value between 0 and 1
        yolo_input_resolution -- two-dimensional tuple with the target network's (spatial)
        input resolution in HW order
        """
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self.input_resolution_yolo = yolo_input_resolution

    def process(self, outputs, resolution_raw):
        """Take the single YOLOv11 output tensor from a TensorRT forward pass,
        post-process it, and return a list of bounding boxes for detected objects
        together with their category and their confidences in separate lists.

        Keyword arguments:
        outputs -- list containing one output tensor from a TensorRT engine, already
        reshaped to (1, 4 + CATEGORY_NUM, num_predictions) by the caller
        resolution_raw -- the original spatial resolution from the input PIL image in WH order
        """
        # (1, 4 + CATEGORY_NUM, num_predictions) -> (num_predictions, 4 + CATEGORY_NUM)
        predictions = np.squeeze(outputs[0], axis=0).transpose(1, 0)

        boxes_cxcywh = predictions[:, :4]
        class_scores = predictions[:, 4:]
        classes = np.argmax(class_scores, axis=-1)
        confidences = class_scores[np.arange(len(classes)), classes]

        keep = confidences >= self.conf_threshold
        boxes_cxcywh = boxes_cxcywh[keep]
        classes = classes[keep]
        confidences = confidences[keep]

        if boxes_cxcywh.shape[0] == 0:
            return None, None, None

        # Boxes are centroid-based in model-input pixel space (e.g. 0-640); convert to
        # top-left x,y,width,height and scale from the model's input resolution to the
        # original captured image resolution.
        input_h, input_w = self.input_resolution_yolo
        orig_w, orig_h = resolution_raw
        scale_x = orig_w / input_w
        scale_y = orig_h / input_h

        cx, cy, w, h = (boxes_cxcywh[:, i] for i in range(4))
        x = (cx - w / 2.0) * scale_x
        y = (cy - h / 2.0) * scale_y
        w = w * scale_x
        h = h * scale_y
        boxes = np.stack((x, y, w, h), axis=-1)

        # Apply per-class non-max suppression to cluster adjacent bounding boxes.
        nms_boxes, nms_classes, nms_scores = list(), list(), list()
        for category in set(classes):
            idxs = np.where(classes == category)
            box = boxes[idxs]
            confidence = confidences[idxs]

            keep_idx = self._nms_boxes(box, confidence)

            nms_boxes.append(box[keep_idx])
            nms_classes.append(classes[idxs][keep_idx])
            nms_scores.append(confidence[keep_idx])

        if not nms_classes:
            return None, None, None

        boxes = np.concatenate(nms_boxes)
        categories = np.concatenate(nms_classes)
        confidences = np.concatenate(nms_scores)

        return boxes, categories, confidences

    def _nms_boxes(self, boxes, box_confidences):
        """Apply the Non-Maximum Suppression (NMS) algorithm on the bounding boxes with their
        confidence scores and return an array with the indexes of the bounding boxes we want to
        keep (and display later).

        Keyword arguments:
        boxes -- a NumPy array containing N bounding-box coordinates that survived filtering,
        with shape (N,4); 4 for x,y,height,width coordinates of the boxes
        box_confidences -- a Numpy array containing the corresponding confidences with shape N
        """
        x_coord = boxes[:, 0]
        y_coord = boxes[:, 1]
        width = boxes[:, 2]
        height = boxes[:, 3]

        areas = width * height
        ordered = box_confidences.argsort()[::-1]

        keep = list()
        while ordered.size > 0:
            # Index of the current element:
            i = ordered[0]
            keep.append(i)
            xx1 = np.maximum(x_coord[i], x_coord[ordered[1:]])
            yy1 = np.maximum(y_coord[i], y_coord[ordered[1:]])
            xx2 = np.minimum(
                x_coord[i] + width[i], x_coord[ordered[1:]] + width[ordered[1:]]
            )
            yy2 = np.minimum(
                y_coord[i] + height[i], y_coord[ordered[1:]] + height[ordered[1:]]
            )

            width1 = np.maximum(0.0, xx2 - xx1 + 1)
            height1 = np.maximum(0.0, yy2 - yy1 + 1)
            intersection = width1 * height1
            union = areas[i] + areas[ordered[1:]] - intersection

            # Compute the Intersection over Union (IoU) score:
            iou = intersection / union

            # The goal of the NMS algorithm is to reduce the number of adjacent bounding-box
            # candidates to a minimum. In this step, we keep only those elements whose overlap
            # with the current bounding box is lower than the threshold:
            indexes = np.where(iou <= self.nms_threshold)[0]
            ordered = ordered[indexes + 1]

        keep = np.array(keep)
        return keep

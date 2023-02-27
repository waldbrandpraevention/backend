"""Functions for the ai prediction"""

import os
import time
import tensorflow as tf
import numpy as np
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from api.dependencies.classes import EventType
from pydantic import BaseModel

THRESHOLD = .30

class Result():
    """Result inforamtion"""
    event_type: int | None = None
    confidence: int | None = None
    picture: JpegImageFile | None = None

def load_image_into_numpy_array(path):
    """Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
      path: the file path to the image

    Returns:
      uint8 numpy array with shape (img_height, img_width, 3)
    """
    return np.array(Image.open(path))


LABEL_FILENAME = 'labelmap.pbtxt'
PATH_TO_LABELS = "./simulation/labelmap.pbtxt"

PATH_TO_SAVED_MODEL = "./simulation/saved_model"

category_index = label_map_util.create_category_index_from_labelmap(
  PATH_TO_LABELS, use_display_name=True)

print('Loading model...', end='')
start_time = time.time()

# Load saved model and build the detection function
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)

end_time = time.time()
elapsed_time = end_time - start_time
print(f'Done! Took {elapsed_time} seconds')

IMG_PATH = "./assets/raw"
directory = os.fsencode(IMG_PATH)

def ai_prediction(path: str):
    """Generates an ai prediction using computer vision and object detection

    Args:
        path (str): path to the image

    Returns:
        Result: result
    """
    #for file in os.listdir(directory):

    #filename = os.fsdecode(path)
    #image_path = os.path.join(img_path, filename)
    image_path = path
    print(f'Running inference for {image_path}... ', end='')

    image_np = load_image_into_numpy_array(image_path)

    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image_np)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # input_tensor = np.expand_dims(image_np, 0)
    detections = detect_fn(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections
    #print("num:")
    #print(num_detections)
    #print("\n")

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    image_np_with_detections = image_np.copy()

    classes = [cls for cls in detections['detection_classes']
                  [detections['detection_scores'] > THRESHOLD]]
    #classes = [category_index.get(cls)['name'] for cls in classes]
    percantages = detections['detection_scores'][:len(classes)]
    #print("output:\n")
    #print(classes)
    #print("per:\n")
    #print(percantages)

    viz_utils.visualize_boxes_and_labels_on_image_array(
          image_np_with_detections,
          detections['detection_boxes'],
          detections['detection_classes'],
          detections['detection_scores'],
          category_index,
          use_normalized_coordinates=True,
          max_boxes_to_draw=200,
          min_score_thresh=THRESHOLD,
          agnostic_mode=False)

    #plt.figure()
    #plt.imshow(image_np_with_detections)
    image = Image.fromarray(image_np_with_detections)
    #im.save("./assets/predicted/out_{}.png".format(counter))
    print('Done')
    results = []
    size = len(classes)
    for i in range(size):
        result = Result()
        result.event_type = classes[i]
        result.confidence = int(percantages[i] * 100 + 0.5)
        result.picture = image
        results.append(result)
    return results


#ai_prediction("./assets/raw/111171_waldbrand-longEdge512.jpg")

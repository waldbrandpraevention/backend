import os

import tensorflow as tf
from tensorflow import keras
from api.dependencies.classes import EventType

class Result():
    event_type: EventType | None = None
    confidence: int | None = None
    picture_path :str| None = None
    ai_predictions :dict| None = None
    csv_file_path :str| None = None

def ai_evaluation(path: str)
    #do stuff

    result = Result()
    return result


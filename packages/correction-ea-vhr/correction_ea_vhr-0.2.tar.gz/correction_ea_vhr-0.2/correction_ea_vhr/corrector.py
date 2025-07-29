import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
from .utils import calcular_media_incertidumbre

class EaVHRCorrector:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "model", "VHR.h5")
        self.model = load_model(model_path, custom_objects={"mse": MeanSquaredError()})

    def corregir(self, X, Y):
        pred = self.model.predict(X)
        E = Y / (pred + 1)
        media, incertidumbre = calcular_media_incertidumbre(E)
        return media, incertidumbre, pred

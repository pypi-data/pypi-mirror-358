import numpy as np

def calcular_media_incertidumbre(datos):
    n = len(datos)
    media = np.mean(datos)
    incertidumbre = np.std(datos, ddof=1) / np.sqrt(n)
    return media, incertidumbre

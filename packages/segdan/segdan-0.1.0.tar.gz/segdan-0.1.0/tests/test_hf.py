import os 
import sys
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import huggingface_hub
import yaml
from PIL import Image
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.datasets.traindataset import TrainingDataset
from src.utils.imagelabelutils import ImageLabelUtils

if __name__ == "__main__":

    
    # image_path = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\train\images"
    # label_path = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\train\labels\train_annotations.json"
    # multilabel_path = r"C:\Users\joortif\Desktop\datasets\Preprocesados\melanoma_3c\train\labels"
    # nc = 80
    # background = None
    # output_path = r"C:\Users\joortif\Desktop\datasets\testing_splits\txt"

    # dataset = TrainingDataset(img_path=image_path, multilabel_label_path=multilabel_path, output_path=output_path, label_format="txt", original_label_path=label_path)

    # dataset.split(nc, 0.7, 0.2, 0.1, True, "pixel_distribution", background)

    dict = ImageLabelUtils.get_classes_from_csv(r"C:\Users\joortif\Desktop\datasets\results\results_covid\analysis\metrics.csv", background=255)
    print(dict)

    # # Directorio principal donde se encuentran los folds
    # directorio_base = r"C:\Users\joortif\Desktop\datasets\results_coffee\split"

    # # Lista para almacenar los nombres de archivos en las carpetas val
    # archivos_val_images = set()
    # archivos_val_labels = set()

    # # Variable para marcar si hay archivos repetidos
    # hay_repetidos = False

    # # Recorre los folds
    # for i in range(1, 6):  # Cambia el rango según la cantidad de folds
    #     fold = f'fold_{i}'
    #     fold_path = os.path.join(directorio_base, fold)
        
    #     # Directorios de val/images y val/labels
    #     val_images_path = os.path.join(fold_path, 'val', 'images')
    #     val_labels_path = os.path.join(fold_path, 'val', 'labels')
        
    #     # Comprueba si los directorios existen
    #     if os.path.exists(val_images_path) and os.path.exists(val_labels_path):
    #         # Nombres de archivos en val/images
    #         for archivo in os.listdir(val_images_path):
    #             if archivo.endswith(('.jpg', '.png', '.jpeg')):  # Cambia las extensiones si es necesario
    #                 nombre_archivo = os.path.splitext(archivo)[0]
    #                 if nombre_archivo in archivos_val_images:
    #                     print(f"Archivo repetido en val/images: {archivo}")
    #                     hay_repetidos = True
    #                 archivos_val_images.add(nombre_archivo)
            
    #         # Nombres de archivos en val/labels
    #         for archivo in os.listdir(val_labels_path):
    #             if archivo.endswith(('.txt', '.xml')):  # Cambia las extensiones si es necesario
    #                 nombre_archivo = os.path.splitext(archivo)[0]
    #                 if nombre_archivo in archivos_val_labels:
    #                     print(f"Archivo repetido en val/labels: {archivo}")
    #                     hay_repetidos = True
    #                 archivos_val_labels.add(nombre_archivo)

    # # Resultado final
    # if not hay_repetidos:
    #     print("No hay archivos repetidos en las carpetas val.")
    # else:
    #     print("Se han encontrado archivos repetidos.")







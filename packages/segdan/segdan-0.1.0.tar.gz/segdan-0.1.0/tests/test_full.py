import os 
import sys
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import yaml
import json



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from imagedatasetanalyzer import ImageLabelDataset, ImageDataset

from src.datasets.traindataset import TrainingDataset
from src.reduction.reduction import reduce_dataset
from src.analysis.analysis import analyze_data
from src.clustering.clustering import cluster_images, get_embeddings
from src.transformers.transformerfactory import TransformerFactory
from src.utils.imagelabelutils import ImageLabelUtils
from src.utils.confighandler import ConfigHandler
from src.extensions.extensions import LabelExtensions


logger = logging.getLogger("SegmentationPipeline")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def process_analysis(config, transformer, images_dir, output_path, verbose):

    analysis_config = config["analysis"]
    reduced_path = None

    if analysis_config["analyze"]: 
        analyze_data(config, transformer, images_dir, verbose, logger)

    if analysis_config["cluster_images"]:
        image_dataset = ImageDataset(images_dir)
        embeddings = get_embeddings(config, image_dataset, verbose, logger)
        best_model_config = cluster_images(analysis_config, image_dataset, embeddings, output_path, verbose, logger)

        if analysis_config["reduction"]:
            reduced_path = reduce_dataset(analysis_config, best_model_config, image_dataset, embeddings, dataset_path, output_path)
        
    return reduced_path

def process_training(config, dataset_path, output_path, verbose, logger):
    
    labels_dir = ImageLabelUtils.get_labels_dir(dataset_path)
    imgs_dir = os.path.join(dataset_path, "images")
    output_dir = os.path.join(output_path, "splits")

    training_config = config["training"]
        
    if labels_dir is None:
            
        print("Training process terminated: The dataset does not contain a valid 'labels' directory.\n"
              "Segmentation models require corresponding label files for each image to learn properly. \n" 
              "Please ensure your dataset structure follows this format: \n"
              "/dataset_path \n"
              "\t /images    (Contains input images) \n"
              "\t /labels    (Contains corresponding label masks) \n")
        
        return

    # Cargar los archivos JSON
def load_json(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Guardar el archivo JSON combinado
def save_json(data, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    # Función para fusionar los JSONs
def merge_coco(json1, json2):
        merged = json1.copy()
        
        # Ajustar IDs para evitar duplicados
        max_image_id = max(img["id"] for img in json1["images"]) if json1["images"] else 0
        max_ann_id = max(ann["id"] for ann in json1["annotations"]) if json1["annotations"] else 0
        
        # Mapear IDs de imágenes del segundo JSON para evitar colisiones
        id_map = {}
        for img in json2["images"]:
            new_id = max_image_id + img["id"]
            id_map[img["id"]] = new_id
            img["id"] = new_id
            merged["images"].append(img)
        
        # Ajustar IDs en anotaciones
        for ann in json2["annotations"]:
            ann["id"] = max_ann_id + ann["id"]
            ann["image_id"] = id_map[ann["image_id"]]  # Asignar nuevo ID de imagen
            merged["annotations"].append(ann)
        
        # Evitar duplicados en categorías
        existing_categories = {cat["id"]: cat for cat in json1["categories"]}
        for cat in json2["categories"]:
            if cat["id"] not in existing_categories:
                merged["categories"].append(cat)
        
        return merged

if __name__ == "__main__":
    
    # Archivos de entrada
    json1 = load_json(r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\train\labels\train_annotations.json")
    json2 = load_json(r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\valid\labels\valid_annotations.json")

    # Combinar los JSON
    merged_json = merge_coco(json1, json2)

    # Guardar el resultado
    save_json(merged_json, r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\train\anotaciones_combinadas.json")

    print("✅ Archivos combinados exitosamente en 'anotaciones_combinadas.json'")


#if __name__ == "__main__":

"""    yaml_path = os.path.join(os.getcwd(), "segdan", "data", "config.yaml")

    config = ConfigHandler.load_config_file(yaml_path)

    transformer = TransformerFactory()

    dataset_path = config["dataset_path"]
    output_path = config["output_path"]
    use_reduced = config["analysis"]["use_reduced"]

    images_dir = os.path.join(dataset_path, "images")
    verbose = config["verbose"]

    if config["analysis"]: 
        reduced_path = process_analysis(config, transformer, images_dir, output_path, verbose)

    if config["training"]:

        if use_reduced:
            dataset_path = reduced_path
        
        process_training(config, dataset_path, output_path, use_reduced, verbose, logger)"""




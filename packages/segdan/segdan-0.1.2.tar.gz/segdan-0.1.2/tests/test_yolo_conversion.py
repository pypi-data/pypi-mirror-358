import os
import sys
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.transformers.yolo_to_multilabel import YOLOToMultilabelTransformer
from src.transformers.json_to_multilabel import JSONToMultilabelTransformer
from src.transformers.multilabel_to_instance_seg import MultilabelToInstanceSegmentationTransformer

from transformers import pipeline
from PIL import Image
import requests

import os
import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image
from typing import List

import os
import cv2
import numpy as np
from tqdm import tqdm
from PIL import Image
from typing import List, Dict

import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict

class YOLOtoMultilabel:

    def __init__(self, logger=None):
        self.logger = logger

    def transform(self, label_path: str, image_path: str, output_dir: str, class_colors_dict: Dict[int, List[int]], fill_background: int | None):
        os.makedirs(output_dir, exist_ok=True)

        # Leer las etiquetas YOLO
        objects = self._read_yolo(label_path)
        
        # Abrir la imagen correspondiente
        image = Image.open(image_path)
        w, h = image.size
        
        # Crear una máscara vacía (tamaño de la imagen)
        mask = self._create_empty_mask(h, w, fill_background)
        
        # Para cada objeto en las etiquetas de YOLO
        for class_id, points in objects:
            mask_obj = np.zeros((h, w, 3), dtype=np.uint8)  # Inicializamos con 3 canales (RGB)
            
            # Escalar las coordenadas de los objetos al tamaño de la imagen
            points = self._scale_polygon(points, h, w)
            
            # Obtener el color de la clase desde el diccionario
            if class_id in class_colors_dict:
                color = class_colors_dict[class_id]
            else:
                # Si no se encuentra el ID de clase en el diccionario, se usa un color por defecto
                color = [0, 0, 0]  # Negro (puedes elegir otro valor predeterminado)
            
            # Rellenar la máscara con el color de la clase
            cv2.fillPoly(mask_obj, [points.astype(np.int32)], color)
            
            # Añadir el objeto a la máscara final
            #mask[mask_obj > 0] = mask_obj[mask_obj > 0]
        
        # Guardar la máscara multilabel con colores
        self._save_multilabel_mask(mask, label_path, output_dir)
        
        return mask

    def _read_yolo(self, label_path: str) -> List:
        """
        Lee las etiquetas en formato YOLO de un archivo de texto.
        Retorna una lista de objetos, donde cada objeto es una tupla con el id de clase y las coordenadas del polígono.
        """
        objects = []
        with open(label_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                class_id = int(parts[0])
                # Convertir las coordenadas a una lista de puntos
                points = np.array([float(p) for p in parts[1:]], dtype=np.float32).reshape(-1, 2)
                objects.append((class_id, points))
        return objects
    
    def _create_empty_mask(self, h: int, w: int, fill_background: int | None) -> np.ndarray:
        """
        Crea una máscara vacía del tamaño de la imagen. Si `fill_background` no es `None`, rellena el fondo.
        """
        if fill_background is not None:
            return np.full((h, w, 3), fill_background, dtype=np.uint8)  # Tres canales para RGB
        return np.zeros((h, w, 3), dtype=np.uint8)  # Tres canales para RGB
    
    def _scale_polygon(self, points: np.ndarray, h: int, w: int) -> np.ndarray:
        """
        Escala las coordenadas de los puntos para que coincidan con las dimensiones de la imagen.
        """
        points[:, 0] *= w  # Escalar las coordenadas x
        points[:, 1] *= h  # Escalar las coordenadas y
        return points

    def _save_multilabel_mask(self, mask: np.ndarray, label_path: str, output_dir: str):
        """
        Guarda la máscara multilabel como una imagen en el directorio de salida.
        """
        mask_name = os.path.basename(label_path).replace('.txt', '.png')  # Usar el nombre de la etiqueta para la máscara
        mask_path = os.path.join(output_dir, mask_name)
        cv2.imwrite(mask_path, mask)


if __name__ == "__main__":

    yolo_converter = YOLOtoMultilabel()

    class_colors_dict = {
    50: [0, 255, 0],
    49: [0, 0, 255], 
    45: [255, 0, 0],

    }

    image_path = r"C:\Users\joortif\Desktop\datasets\Completos\coco8-seg\train\images\000000000009.jpg"

    # Transformar las etiquetas de YOLO a máscaras multilabel
    converted_masks = yolo_converter.transform(
        label_path=r"C:\Users\joortif\Desktop\datasets\Completos\coco8-seg\train\labels\000000000009.txt",
        output_dir=r"C:\Users\joortif\Desktop\results",
        image_path=image_path,
        class_colors_dict=class_colors_dict,  # Diccionario de colores por clase
        fill_background=[0,0,0]  # 0 para fondo vacío, o cualquier valor que quieras para el fondo
    )
    
    

    # Cargar el modelo de estimación de profundidad
    pipe = pipeline("depth-estimation", model="Intel/dpt-swinv2-tiny-256")

    # Cargar una imagen
      # Reemplaza con la ruta de tu imagen
    image = Image.open(image_path)

    # Aplicar el modelo sobre la imagen
    depth_map = pipe(image)

    depth_map['depth'].show()

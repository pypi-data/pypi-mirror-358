import os
import sys
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from converters.yolo_to_multilabel import YOLOToMultilabelConverter
from converters.json_to_multilabel import JSONToMultilabelConverter
from converters.multilabel_to_instance_seg import MultilabelToInstanceSegmentationConverter


if __name__ == "__main__":

    def overlay_mask_on_image(image_path, mask_path, output_path=None):
        """
        Superpone la máscara de segmentación sobre la imagen original y muestra el resultado.
        
        :param image_path: Ruta de la imagen original.
        :param mask_path: Ruta de la máscara de segmentación.
        :param output_path: Ruta donde guardar la imagen superpuesta (opcional).
        """
        # Cargar la imagen original con PIL
        with Image.open(image_path) as image:
            image = Image.open(image_path).convert('RGB')
            
            # Cargar la máscara (en escala de grises)
            mask = Image.open(mask_path).convert('L')
            mask = np.array(mask)

            # Convertir la imagen a un array de numpy para manipularla
            image_np = np.array(image)

            # Crear una máscara de color (verde en este caso) para los píxeles no cero
            colored_mask = np.zeros_like(image_np)  # Crear una máscara del mismo tamaño que la imagen
            colored_mask[mask == 0] = [0, 255, 0]  # Asignar el color verde a los píxeles no cero en la máscara
            colored_mask[mask == 1] = [255, 0, 0]
            colored_mask[mask == 2] = [0, 0, 255]
            colored_mask[mask == 3] = [0, 0, 125]
            # Superponer la imagen original y la máscara con algo de transparencia
            overlay = np.where(colored_mask == 0, image_np, (0.6 * colored_mask + 0.4 * image_np).astype(np.uint8))

            # Mostrar la imagen original con la máscara superpuesta
            plt.figure(figsize=(10, 10))
            plt.imshow(overlay)
            plt.axis('off')  # Ocultar los ejes
            #plt.show()
            plt.close()

            # Si se especificó un `output_path`, guardar la imagen superpuesta
            if output_path:
                # Guardar la imagen superpuesta usando PIL
                overlay_image = Image.fromarray(overlay)
                overlay_image.save(output_path)
                #print(f"✅ Imagen superpuesta guardada en: {output_path}")


    transformer = JSONToMultilabelTransformer()

    img_path = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\train\images"
    lbl_path = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\train\labels"
    output_dir = r"C:\Users\joortif\Desktop\Resultados_SegDAN\transformers\YoloToMultilabel"
    output_superposition = r"C:\Users\joortif\Desktop\Resultados_SegDAN\transformers\superposiciones_c3depth"

    res = transformer.transform(lbl_path, img_path, 3, output_dir=output_dir, verbose=True)

    saved_counts = {0: 0, 1: 0, 2: 0}

    images = os.listdir(img_path)

    for i, image in enumerate(images):
        image_name, _ = os.path.splitext(image)
        mask_name = f"{image_name}.png"
        mask_path = os.path.join(output_dir, mask_name)

        # Verificar si la máscara existe
        if not os.path.exists(mask_path):
            continue
        
        # Cargar la máscara para identificar qué clases contiene
        mask = np.array(Image.open(mask_path).convert("L"))

        # Identificar las clases presentes en la máscara
        unique_classes = np.unique(mask)

        for class_id in unique_classes:
            if class_id in saved_counts and saved_counts[class_id] < 10:
                output_path = os.path.join(output_superposition, f"superposicion_{class_id}_{saved_counts[class_id]}.png")
                overlay_mask_on_image(os.path.join(img_path, image), mask_path, output_path)
                saved_counts[class_id] += 1

            # Si ya tenemos 10 imágenes de cada clase, terminar el proceso
            if all(count >= 10 for count in saved_counts.values()):
                print("✅ Se han guardado 10 imágenes por clase. Proceso terminado.")
                exit()
    
    # YOLO TO MULTILABEL
    """transformer = YOLOToMultilabelTransformer()

    objects = transformer.transform(lbl_path, img_path, '.jpg', 80, output_path=output_dir, verbose=True)"""

    """
    # MULTILABEL TO MULTICHANNEL
    
    batch_masks = np.array([
    [[0, 1, 1, 1], 
     [1, 0, 2, 0], 
     [0, 3, 2, 0]],  # Primera imagen
    [[3, 2, 3, 3], 
     [2, 1, 2, 0], 
     [4, 0, 5, 0]]   # Segunda imagen
    ])

    transformer = MultilabelToInstanceSegmentationTransformer()

    # Convertir el batch a formato multicanal sin la clase 0
    multichannel_batch = transformer.transform(batch_masks, background=0)


    for i, instance_mask in enumerate(multichannel_batch):
        print(f"Instancia {i + 1} pertenece a la clase {np.unique(instance_mask[instance_mask != 0])}:")
        print(instance_mask)
    print(multichannel_batch.shape)"""

    
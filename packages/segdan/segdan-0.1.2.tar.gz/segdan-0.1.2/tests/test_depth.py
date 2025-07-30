import os
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from transformers import pipeline

def draw_mask_yolo_order(label_path, image_path, class_colors_dict, fill_background=None, save_path="mask_yolo_order.png"):
    image = Image.open(image_path)
    w, h = image.size
    mask = np.full((h, w, 3), fill_background if fill_background else 0, dtype=np.uint8)

    with open(label_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])
        points = np.array([float(p) for p in parts[1:]], dtype=np.float32).reshape(-1, 2)
        points[:, 0] *= w
        points[:, 1] *= h
        color = class_colors_dict.get(class_id, [0, 0, 0])
        cv2.fillPoly(mask, [points.astype(np.int32)], color)

    cv2.imwrite(save_path, mask)
    print(f"[✔] Máscara YOLO-order guardada en {save_path}")

def transform_yolo_with_depth(
    label_path: str,
    image_path: str,
    output_path: str,
    class_colors_dict: dict,
    depth_model: str = "Intel/dpt-swinv2-tiny-256",
    fill_background: int | list = [0, 0, 0]
):
    image = Image.open(image_path)
    w, h = image.size
    pipe = pipeline("depth-estimation", model=depth_model)
    depth_result = pipe(image)
    depth_map = np.array(depth_result['depth'].resize((w, h)))

    objects = []
    with open(label_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            class_id = int(parts[0])
            points = np.array([float(p) for p in parts[1:]], dtype=np.float32).reshape(-1, 2)
            points[:, 0] *= w
            points[:, 1] *= h
            objects.append((class_id, points))

    object_depths = []
    for class_id, polygon in objects:
        mask_obj = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask_obj, [polygon.astype(np.int32)], 255)
        depth_values = depth_map[mask_obj == 255]
        if depth_values.size > 0:
            depth_mean = np.mean(depth_values)
            object_depths.append((depth_mean, class_id, polygon))

    object_depths.sort(key=lambda x: x[0], reverse=True)

    mask = np.full((h, w, 3), fill_background, dtype=np.uint8)
    for _, class_id, polygon in object_depths:
        color = class_colors_dict.get(class_id, [0, 0, 0])
        cv2.fillPoly(mask, [polygon.astype(np.int32)], color)

    cv2.imwrite(output_path, mask)
    print(f"[✔] Máscara ordenada por profundidad guardada en: {output_path}")

def triple_comparison_matplotlib(original_img_path, mask_yolo_path, mask_depth_path, output_path="full_comparison_matplotlib.png"):
    # Leer las imágenes y convertir a RGB para que matplotlib las muestre correctamente
    img_orig = cv2.cvtColor(cv2.imread(original_img_path), cv2.COLOR_BGR2RGB)
    mask_yolo = cv2.cvtColor(cv2.imread(mask_yolo_path), cv2.COLOR_BGR2RGB)
    mask_depth = cv2.cvtColor(cv2.imread(mask_depth_path), cv2.COLOR_BGR2RGB)

    # Crear figura
    fig, axs = plt.subplots(1, 2, figsize=(18, 6))


    axs[0].imshow(mask_yolo)
    axs[0].set_title("Máscara sin profundidad")
    axs[0].axis("off")

    axs[1].imshow(mask_depth)
    axs[1].set_title("Máscara con profundidad")
    axs[1].axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[✅] Comparación guardada como: {output_path}")

def show_original_and_depth(image_path, depth_model="Intel/dpt-swinv2-tiny-256", output_path="original_vs_depth.png"):
    # Cargar imagen original
    image = Image.open(image_path)
    w, h = image.size

    # Estimar profundidad
    pipe = pipeline("depth-estimation", model=depth_model)
    depth_result = pipe(image)
    depth_image = np.array(depth_result['depth'].resize((w, h)))

    # Normalizar a 0-255 para mostrar como escala de grises
    depth_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
    depth_uint8 = depth_normalized.astype(np.uint8)

    # Convertir imagen original a RGB para matplotlib
    img_rgb = np.array(image)

    # Crear figura
    fig, axs = plt.subplots(1, 2, figsize=(18, 6))

    axs[0].imshow(img_rgb)
    axs[0].set_title("Imagen original")
    axs[0].axis("off")

    axs[1].imshow(depth_uint8, cmap="gray")
    axs[1].set_title("Mapa de profundidad (grises)")
    axs[1].axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[📸] Comparación imagen-original y profundidad guardada en: {output_path}")


if __name__ == "__main__":
    # Configuración
    image_path = r"C:\Users\joortif\Desktop\datasets\Completos\coco8-seg\train\images\000000000009.jpg"
    label_path = r"C:\Users\joortif\Desktop\datasets\Completos\coco8-seg\train\labels\000000000009.txt"
    output_dir = r"C:\Users\joortif\Desktop\results"

    os.makedirs(output_dir, exist_ok=True)

    mask_yolo_path = os.path.join(output_dir, "mask_wrong.png")
    mask_depth_path = os.path.join(output_dir, "mask_correct.png")
    comparison_path = os.path.join(output_dir, "comparison.png")

    class_colors_dict = {
        50: [255, 165, 0],   # Naranja → bien visible sobre fondo oscuro
        49: [0, 128, 255],   # Azul cielo → contraste fuerte
        45: [0, 255, 0],     # Verde brillante → ya lo tenías, es correcto
    }

    # Paso 1: sin orden de profundidad (erróneo)
    draw_mask_yolo_order(
        label_path=label_path,
        image_path=image_path,
        class_colors_dict=class_colors_dict,
        fill_background=[0, 0, 0],
        save_path=mask_yolo_path
    )

    # Paso 2: con orden por profundidad (correcto)
    transform_yolo_with_depth(
        label_path=label_path,
        image_path=image_path,
        output_path=mask_depth_path,
        class_colors_dict=class_colors_dict,
        depth_model="Intel/dpt-swinv2-tiny-256",
        fill_background=[0, 0, 0]
    )

    # Paso 3: comparar lado a lado
    triple_comparison_matplotlib(image_path, mask_yolo_path, mask_depth_path, output_path=comparison_path)
    original_vs_depth_path = os.path.join(output_dir, "original_vs_depth.png")
    show_original_and_depth(
        image_path=image_path,
        depth_model="Intel/dpt-swinv2-tiny-256",
        output_path=original_vs_depth_path
    )

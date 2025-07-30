import os
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm

def contar_objetos(nombre_imagen_base,
                            ruta_imagenes=r"C:\Users\joortif\Desktop\datasets\Preprocesados\Sidewalk_dataset\train\images",
                            ruta_labels=r"C:\Users\joortif\Desktop\datasets\Preprocesados\Sidewalk_dataset\train\labels",
                            clase_objetivo=2,
                            nombre_clase="acera",
                            color=(0, 0, 255), alpha=0.5):
    """
    Cuenta los objetos de la clase 11 (vehicle-car) en una imagen de segmentación
    y los dibuja sobre la imagen original.
    
    Args:
        nombre_imagen_base (str): nombre del archivo sin extensión.
        ruta_imagenes (str): carpeta donde están las imágenes originales (.jpg).
        ruta_labels (str): carpeta donde están las máscaras de segmentación (.png).
        clase_objetivo (int): valor de la clase a detectar (por defecto 11 para "vehicle-car").
    """
    # Rutas completas
    ruta_imagen = os.path.join(ruta_imagenes, nombre_imagen_base + ".png")
    ruta_mascara = os.path.join(ruta_labels, nombre_imagen_base + ".png")

    # Cargar imagen y máscara
    imagen = cv2.imread(ruta_imagen)
    imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    mascara = np.array(Image.open(ruta_mascara))

    # Crear máscara binaria para la clase objetivo
    mascara_clase = np.uint8(mascara == clase_objetivo) * 255

    # Encontrar contornos
    contornos, _ = cv2.findContours(mascara_clase, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Crear overlay
    overlay = imagen_rgb.copy()
    for contour in contornos:
        cv2.drawContours(overlay, [contour], -1, color, thickness=cv2.FILLED)

    # Fusionar con la imagen original
    image_with_overlay = cv2.addWeighted(overlay, alpha, imagen_rgb, 1 - alpha, 0)

    # Añadir texto
    num_objetos = len(contornos)
    cv2.putText(image_with_overlay, f'{nombre_clase} detectados: {num_objetos}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Mostrar resultado
    plt.figure(figsize=(10, 6))
    plt.imshow(image_with_overlay)
    plt.title(f'{nombre_imagen_base} - {num_objetos} {nombre_clase}(s) detectados')
    plt.axis('off')
    plt.show()

def calculate_pixel_distribution(mask_paths, background: int | None = None):
    all_distributions = []
    unique_classes = set()
    per_image_summary = []

    for mask_path in tqdm(mask_paths, desc="Calculating pixel distribution for each class"):
        with Image.open(mask_path) as mask_image:
            mask = np.array(mask_image)
            unique, counts = np.unique(mask, return_counts=True)

            if background is not None:
                mask_exclude_idx = np.where(unique == background)[0]
                if len(mask_exclude_idx) > 0:
                    unique = np.delete(unique, mask_exclude_idx)
                    counts = np.delete(counts, mask_exclude_idx)

            unique_classes.update(unique)

            total = counts.sum()
            dist_dict = {class_id: count for class_id, count in zip(unique, counts)}
            all_distributions.append(dist_dict)

            # Resumen legible: porcentaje por clase
            summary = {int(cls): round(100 * count / total, 2) for cls, count in dist_dict.items()}
            per_image_summary.append(summary)

    sorted_classes = sorted(unique_classes)
    num_classes = len(sorted_classes)

    matrix_distributions = np.zeros((len(mask_paths), num_classes))
    for i, distribution in enumerate(all_distributions):
        for class_id, count in distribution.items():
            class_index = sorted_classes.index(class_id)
            matrix_distributions[i, class_index] = count

    row_sums = matrix_distributions.sum(axis=1, keepdims=True)
    matrix_distributions = np.divide(matrix_distributions, row_sums, where=row_sums != 0)

    return {
        "distributions": matrix_distributions,
        "num_classes": num_classes,
        "class_ids_present": sorted_classes,
        "per_image_percentages": per_image_summary
    }

def superponer_mascara_con_colores(nombre_imagen_base,
                                    ruta_imagenes,
                                    ruta_labels,
                                    dict_colores,
                                    alpha=0.5):
    """
    Superpone la máscara de segmentación sobre la imagen original utilizando un diccionario
    de colores por clase. Las clases no presentes en el diccionario (como 'void') se dejan sin color.

    Args:
        nombre_imagen_base (str): Nombre base del archivo (sin extensión).
        ruta_imagenes (str): Ruta donde están las imágenes (.png o .jpg).
        ruta_labels (str): Ruta donde están las máscaras (.png).
        dict_colores (dict): Diccionario {id_clase: (R, G, B)}.
        alpha (float): Transparencia de la máscara sobrepuesta.
    """
    import os
    import numpy as np
    import cv2
    from PIL import Image
    import matplotlib.pyplot as plt

    # Rutas completas
    ruta_imagen = os.path.join(ruta_imagenes, nombre_imagen_base + ".png")
    ruta_mascara = os.path.join(ruta_labels, nombre_imagen_base + ".png")

    # Leer imagen y máscara
    imagen = cv2.imread(ruta_imagen)
    imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    mascara = np.array(Image.open(ruta_mascara))

    # Crear máscara RGB con color por clase
    overlay = np.zeros_like(imagen_rgb)
    for clase_id, color in dict_colores.items():
        mask_clase = (mascara == clase_id)
        overlay[mask_clase] = color

    # Superponer máscara coloreada con transparencia
    imagen_final = cv2.addWeighted(overlay, alpha, imagen_rgb, 1 - alpha, 0)

    # Mostrar imagen
    plt.figure(figsize=(10, 6))
    plt.imshow(imagen_final)
    plt.axis("off")
    plt.show()

    return imagen_final

import numpy as np
import matplotlib.pyplot as plt

def generar_datos_y_graficar(num_grupos=3, puntos_por_grupo=50, 
                             seleccionadas=3, criterio='cercanas', semilla=42, rango_centro=20, desviacion=1.0,  colores_grupos=None):
    """
    Genera datos agrupados y los grafica, marcando centroides y puntos seleccionados.

    Parámetros:
    - num_grupos: cantidad de clusters.
    - puntos_por_grupo: puntos por cluster.
    - seleccionadas: número de puntos a marcar en rojo por cluster.
    - criterio: cómo seleccionar esos puntos ('cercanas', 'lejanas', 'aleatorias').
    - semilla: para reproducibilidad.
    """
    
    np.random.seed(semilla)
    
    datos = []
    etiquetas = []
    
    centros = np.random.uniform(0, rango_centro, size=(num_grupos, 2))
    
    for i, centro in enumerate(centros):
        grupo = np.random.randn(puntos_por_grupo, 2) *  desviacion +centro
        datos.append(grupo)
        etiquetas += [i] * puntos_por_grupo
    
    datos = np.vstack(datos)
    etiquetas = np.array(etiquetas)
    
    centroides = np.array([datos[etiquetas == i].mean(axis=0) for i in range(num_grupos)])
    
    plt.figure(figsize=(8, 6))

    if colores_grupos is None:
        cmap = plt.cm.get_cmap('tab10', num_grupos)
        colores = [cmap(i) for i in range(num_grupos)]
    else:
        if len(colores_grupos) < num_grupos:
            raise ValueError("La lista de colores debe tener al menos tantos colores como grupos.")
        colores = colores_grupos
    
    for i in range(num_grupos):
        grupo_datos = datos[etiquetas == i]
        # Calcular distancias al centroide
        distancias = np.linalg.norm(grupo_datos - centroides[i], axis=1)
        
        if criterio == 'cercanas':
            indices_selec = np.argsort(distancias)[:seleccionadas]
        elif criterio == 'lejanas':
            indices_selec = np.argsort(distancias)[-seleccionadas:]
        elif criterio == 'aleatorias':
            indices_selec = np.random.choice(len(grupo_datos), seleccionadas, replace=False)
        else:
            raise ValueError("Criterio debe ser 'cercanas', 'lejanas' o 'aleatorias'")
        
        plt.scatter(grupo_datos[:, 0], grupo_datos[:, 1], 
                    color=colores[i], label=f'Grupo {i+1}', alpha=0.5)
        plt.scatter(grupo_datos[indices_selec, 0], grupo_datos[indices_selec, 1], 
                    color='red', edgecolor='black', s=50, label=f'Seleccionados G{i+1}')
        #plt.scatter(centroides[i, 0], centroides[i, 1], color=colores[i], 
        #            marker='X', s=200, edgecolor='black', label=f'Centroide {i+1}')
        
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    colores_normalizados = [
    (102/255, 194/255, 165/255),
    (252/255, 141/255,  98/255),
    (141/255, 160/255, 203/255),
    (231/255, 138/255, 195/255)
]
    generar_datos_y_graficar(num_grupos=4, criterio='aleatorias', seleccionadas=0, rango_centro=8, desviacion=0.5, colores_grupos=colores_normalizados)




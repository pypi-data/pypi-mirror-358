import os
import numpy as np
from sklearn.decomposition import PCA
import plotly.express as px
from PIL import Image
import base64
from tqdm import tqdm

# === RUTAS ===
embedding_path = r"C:\Users\joortif\Desktop\datasets\embeddings_melanoma.npy"
images_folder = r"C:\Users\joortif\Desktop\datasets\Completos\melanoma_3c\full_converted\images"

# === CARGA DE EMBEDDINGS ===
embeddings = np.load(embedding_path)

# === OBTENER RUTAS DE IMÁGENES ===
# Asegúrate de que las imágenes estén en el mismo orden que los embeddings
image_paths = sorted([
    os.path.join(images_folder, fname)
    for fname in os.listdir(images_folder)
    if fname.lower().endswith(('.jpg', '.jpeg', '.png'))
])

assert len(image_paths) == len(embeddings), "El número de imágenes no coincide con el número de embeddings"

# === REDUCCIÓN PCA A 2D ===
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)

# === ENCODEAR MINIATURAS PARA EL HOVER ===
def encode_image_base64(image_path, size=(64, 64)):
    try:
        img = Image.open(image_path).convert("RGB")
        img.thumbnail(size)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error cargando {image_path}: {e}")
        return ""

from io import BytesIO
hover_images = [encode_image_base64(path) for path in tqdm(image_paths)]

# === CREAR GRAFICO INTERACTIVO CON PLOTLY ===
fig = px.scatter(
    x=embeddings_2d[:, 0],
    y=embeddings_2d[:, 1],
    hover_data={"Image": hover_images},
    labels={"x": "PCA 1", "y": "PCA 2"}
)

fig.update_traces(marker=dict(size=8, color="blue", opacity=0.7))
fig.update_layout(hovermode='closest', title="Embeddings visualizados con PCA")

fig.show()

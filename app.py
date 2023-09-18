import streamlit as st
import os
from process_video import process_video

# Configurar diretório de upload
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)

# Função para detecção
def detect(video):
    # Salvar o arquivo enviado pelo usuário
    file_path = os.path.join(uploads_dir, video.name)
    with open(file_path, "wb") as f:
        f.write(video.read())  # Lê os dados do arquivo e escreve no arquivo local

    st.write(f"Arquivo de vídeo carregado: {video.name}")

    if video.name.endswith('.mp4') or video.name.endswith('.avi') or video.name.endswith('.wmv'):
        processed_data = process_video(file_path)
    else:
        processed_data = {'pCRT': 123, 'incerteza': 456}

    st.write(f"Resultados do processamento: {processed_data}")

# Interface do Streamlit
st.title("Detecção de pyCRT por video")
st.write("Carregue um arquivo de vídeo para detecção.")

uploaded_file = st.file_uploader("Carregar vídeo", type=["mp4", "avi", "wmv"])
if uploaded_file is not None:
    detect(uploaded_file)

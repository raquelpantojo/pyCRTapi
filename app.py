"""
atualizado dia 21-09 

dicas: https://github.com/whitphx/streamlit-webrtc

"""

import streamlit as st
import os
import cv2
import numpy as np
from process_video import process_video  # Importe a função process_video do seu módulo
import threading


from rembg import remove
from PIL import Image
from io import BytesIO
import base64


import streamlit as st

# Define o layout da página
st.set_page_config(
    page_title="Cálculo do Tempo de Enchimento capilar",
    page_icon=":information_source:",
    layout="wide"
)

# Use HTML para criar um layout personalizado
st.markdown("""
    <style>
        .container {
            display: flex;
            justify-content: space-between;
        }
        .title {
            font-size: 36px;
        }
        .menu {
            margin-top: 25px;
            margin-right: 20px;
        }
    </style>
    <div class="container">
        <div class="title">Cálculo do Tempo de Enchimento capilar</div>
        <div class="menu">
            <a href="#sobre">Sobre</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# Ancoragem para a seção "Sobre"
st.markdown("<a id='sobre'></a>", unsafe_allow_html=True)

# Conteúdo da seção "Sobre"
st.header("Sobre")
st.write("Desenvolvido por:")
st.image("logo_lab.png", use_column_width=True, width=50)
st.image("logo_usp.png", use_column_width=True, width=50)

# Adicionar um link no sidebar
st.markdown(
    """
[Visite nosso site](https://sites.usp.br/photobiomed/)
"""
)






# Configurar diretório de upload
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)



# Global variable for the stop event
stop_event = threading.Event()


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


def fix_image(upload):
    image = Image.open(upload, resample=Image.LANCZOS)
    #st.write("Original Image :camera:")
    #st.image(image)

    fixed = remove(image)
    st.write("Fixed Image :wrench:")
    st.image(fixed)
    













# Function to capture video from the camera
def capturar_video(camera_index, output_filename):
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        st.error(f"Não foi possível acessar a câmera {camera_index}.")
        return

output_filename = None  # Inicialize a variável global    

# Função para verificar se há imagens de pele em um vídeo
def verifica_imagens_de_pele(video):
    cap = cv2.VideoCapture(video.name)
    tem_imagem_de_pele = True
    imagem_ycrcb = None  # Inicialize a variável imagem_ycrcb com None
    imagem_cinza = None
    imagem_hsv = None
    skinMask = None
    skin = None
    mascara_hsv = None

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Converta o frame para escala de cinza para simplificar a detecção de pele
        imagem_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Converta a imagem para o espaço de cores YCrCb
        #Converta a imagem para o espaço de cores HSV
        imagem_hsv = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

        # Defina os valores de limite para a cor da pele no espaço HSV
        lower_hsv = np.array([0, 20, 80], dtype="uint8")
        upper_hsv = np.array([255, 255, 255], dtype="uint8")

        # Aplique a máscara para detectar a pele no espaço HSV
        mascara_hsv = cv2.inRange(imagem_hsv, lower_hsv, upper_hsv)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (12, 12))
        skinMask = cv2.erode(mascara_hsv, kernel, iterations=3)
        skinMask = cv2.dilate(mascara_hsv, kernel, iterations=3)

        # blur the mask to help remove noise, then apply the
        # mask to the frame
        skinMask = cv2.GaussianBlur(skinMask, (13, 13), 5)
        skin = cv2.bitwise_and(frame, frame, mask=skinMask)

        imagem_ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        # Defina os valores de limite para a cor da pele no espaço YCrCb
        lower_ycrcb = np.array([0, 136, 0], dtype="uint8")
        upper_ycrcb = np.array([255, 173, 127], dtype="uint8")

        # Aplique a máscara para detectar a pele no espaço YCrCb
        mascara_ycrcb = cv2.inRange(imagem_ycrcb, lower_ycrcb, upper_ycrcb)
        

        # Combine as duas máscaras resultantes usando uma operação AND
        mascara_combinada = cv2.bitwise_and(mascara_hsv, mascara_ycrcb)

    
        #print(f"imagem_hsv shape: {imagem_hsv.shape}")
        tem_pixels = np.any(mascara_combinada)
        #print(f"imagem_ycrcb shape: {imagem_ycrcb.shape}")          
        if tem_pixels:
            tem_imagem_de_pele = True
            break
                

    cap.release()

    return tem_imagem_de_pele  # Retorna também a skin_mask e a imagem_ycrcb


# Interface do Streamlit
st.title("Detecção de pyCRT")
st.write("Carregue um arquivo de vídeo para realizar o teste do CRT.")

opcao = st.radio("Selecione uma opção:", ("Fazer um video", "Enviar Vídeo Existente"))

camera_index = st.camera_input("Fazer um vídeo")  # Pode escolher entre diferentes câmeras

if opcao == "Fazer um video":
        # Fazer video:
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                st.image(frame, channels="BGR", use_column_width=True)
        cap.release()

        if st.button("Iniciar Gravação", key=f"start_button_{camera_index}"):
            output_filename = f"video_capturado_camera_{camera_index}.avi"
            capturar_video(camera_index, output_filename)  # Inicie a gravação

            # Após a gravação, exiba o vídeo gravado
            st.write("Vídeo Capturado:")
            st.video(output_filename)
            
        # Verifique se camera_index não é None antes de chamar capturar_video
        if camera_index is not None:
            output_filename = f"video_capturado_camera_{camera_index}.avi"
            
            if st.button("Iniciar Gravação"):
                capturar_video(camera_index, output_filename)  # Chame a função para gravar o vídeo

                # Após a gravação, exiba o vídeo gravado
                st.write("Vídeo Capturado:")
                st.video(output_filename)

else:
    uploaded_file = st.file_uploader("Carregar vídeo", type=["mp4", "avi", "wmv"])
    if uploaded_file is not None:
        video_path = os.path.join(uploads_dir, uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())  # Salva o arquivo enviado pelo usuário
        # Verifique as imagens de pele e processe o vídeo
        tem_pele = verifica_imagens_de_pele(uploaded_file)
        
        if tem_pele == True:
            st.write("Imagens de pele foram encontradas.")
            st.video(video_path)
            

            st.write("Processando vídeo...")
            processed_data = process_video(video_path)  # Processar o vídeo
            st.write(f"Resultados do processamento: {processed_data}")

            # Capturar e exibir o quadro 50 no espaço YCrCb
            cap = cv2.VideoCapture(video_path)
            frame_number = 50  # Número do quadro desejado
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            # Salve o quadro em um arquivo temporário
            temp_frame_filename = "temp_frame.jpg"
            cv2.imwrite(temp_frame_filename, frame)
            fix_image(upload=temp_frame_filename)  # Passe o arquivo temporário para a função
            cap.release()
            
        else:
            st.write("Imagens de pele não foram encontradas, envie um novo vídeo")
    


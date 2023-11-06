"""
atualizado dia 28-09

dicas: https://github.com/whitphx/streamlit-webrtc
https://bgremoval.streamlit.app/

"""

import streamlit as st
import os
import cv2
import numpy as np
from process_video import process_video  # Importe a função process_video do seu módulo
import threading

from PIL import Image
from io import BytesIO

## yolo v5
#import torch
#import tempfile

# Carregue o modelo YOLOv5 'finger.pt' localmente
model = torch.hub.load('ultralytics/yolov5', 'custom', path='finger.pt', force_reload=True)

#model = torch.hub.load('ultralytics/yolov5', 'custom', path='finger.pt', trust_repo='check')



# Define o layout da página
st.set_page_config(
    page_title="Cálculo do Tempo de Enchimento capilar",
    page_icon=":health_worker:",
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
            <a href="#sobre" id="sobre-link">Sobre</a>
        </div>
    </div>
""", unsafe_allow_html=True)



# Configurar diretório de upload
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)



# Função para realizar a detecção em um frame
def detect_finger(image):
    results = model(image)

    return results



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
st.write("Carregue um arquivo de vídeo para realizar o teste do CRT.")
opcao = st.radio("Selecione uma opção:", ("Fazer um video", "Enviar Vídeo Existente"))


if opcao == "Fazer um video":
        # Fazer video:
        camera_index = st.camera_input("Fazer um vídeo")  # Pode escolher entre diferentes câmeras
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
            
            """
            if uploaded_file is not None:
                # Salve o vídeo em um arquivo temporário
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                    temp_filename = temp_file.name
                    temp_file.write(uploaded_file.read())

                # Abra o vídeo com o caminho do arquivo temporário
                video_capture = cv2.VideoCapture(temp_filename)

                # Inicialize variáveis
                detections_found = 0  # Quantas detecções encontradas
                target_detections = 3  # Quantidade de detecções desejadas

                # Abra o vídeo de saída para salvar as detecções
                frame_width = int(video_capture.get(3))
                frame_height = int(video_capture.get(4))
                out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width, frame_height))

                # Loop para processar cada frame do vídeo
                while detections_found < target_detections:
                    ret, frame = video_capture.read()
                    if not ret:
                        break

                    # Realize a detecção no frame
                    results = detect_finger(frame)
                    detected_frame = results.render()[0]

                    # Se uma detecção foi encontrada, exiba o frame
                    if len(results.xyxy[0]) > 0:
                        detection = results.xyxy[0][0]  # Pegue a primeira detecção
                        xmin, ymin, xmax, ymax = detection[0:4]  # Valores x, y, largura (w) e altura (h)
                        
                        x1, y1, x2, y2 = map(int, detection[0:4])  
                        roi = frame[y1:y2, x1:x2]
                        
                        st.image(roi,channels ="BGR")
                        st.image(detected_frame, caption=f"Detecção {detections_found + 1}", use_column_width=True,channels ="BGR")
                        
                        #st.write(f"x: {x}, y: {y}, largura (w): {w}, altura (h): {h}")
                        
                        # Converte para números inteiros
                        #x1 = int(x - w / 2)
                        #y1 = int(y - h / 2)
                        #x2 = int(x + w / 2)
                        #y2 = int(y + h / 2)
                        
                        st.write(f"YOLO xmin: {xmin}, ymin: {ymin}, xmax: {xmax}, ymax: {ymax}")
                        st.write(f"OpenCV x: {x1}, y: {y1}, x2: {x2}, y2: {y2}")
                        
                
                        detections_found += 1

                    # Escreva o frame no vídeo de saída
                    out.write(detected_frame)

                # Fecha o vídeo de saída
                out.release()
                     # Certifique-se de apagar o arquivo temporário após o uso
            os.remove(temp_filename)
            """
            


       



            # Remover o fundo do vídeo
            #output_video_path = "video_com_fundo_removido"  # Especifique o caminho de saída desejado
            #remove_image(frame)  # Chame a função para remover o fundo do vídeo

            #st.write("Vídeo com fundo removido:")
            #st.image(output_video_path)
                    
            
        else:
            st.write("Imagens de pele não foram encontradas, envie um novo vídeo")
    




st.write("Desenvolvido por")
# Ancoragem para a seção "Sobre"
st.markdown("<a id='sobre'></a>", unsafe_allow_html=True)


# Conteúdo da seção "Sobre"
with st.markdown("<a id='sobre'></a>", unsafe_allow_html=True):
#with st.beta_expander("Sobre", expanded=False):
    st.write("Desenvolvido por:")

    # Crie duas colunas para exibir as imagens lado a lado
    col1, col2 = st.beta_columns(2)

    # Adicione as imagens nas colunas
    with col1:
        st.image("logo_lab.png", use_column_width=True, width=40)

    with col2:
        st.image("logo_usp.png", use_column_width=True, width=40)

    # Adicionar um link no sidebar
    st.markdown(
        """
    [Visite nosso site](https://sites.usp.br/photobiomed/)
    """)

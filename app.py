"""
atualizado dia 06-10
16h35 Tentativa de adicionar o Yolo com a detecção pCRT --- ok
:: Próximos passos:
:: Reduzir o tamanho da imagem com detecção.
:: Testar os valores de CRT com roi manual e roi do Yolo.


-
dicas: https://github.com/whitphx/streamlit-webrtc
https://bgremoval.streamlit.app/

"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import streamlit as st
import os
import cv2
import numpy as np
from process_video import process_video  # Importe a função process_video do seu módulo
import threading

from PIL import Image
from io import BytesIO

## yolo v5
import torch
import tempfile

# Depuração 
#import pdb; pdb.set_trace()

# Carregue o modelo YOLOv5 'finger.pt' localmente
model = torch.hub.load('ultralytics/yolov5', 'custom', path='finger.pt', force_reload=True,trust_repo=True)

#model = torch.hub.load('ultralytics/yolov5', 'custom', path='finger.pt', trust_repo='check')


# Função para realizar a detecção em um frame
def detect_finger(image):
    results = model(image)
    return results



# Define o layout da página
st.set_page_config(
    page_title=":raised_hand_with_fingers_splayed: Cálculo do Tempo de Enchimento capilar",
    page_icon=":health:",
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
    st.write("Ainda não é possivel fazer imagens com sua câmera")

if opcao == "Enviar Vídeo Existente":
    uploaded_file = st.file_uploader("Carregar vídeo", type=["mp4", "avi", "wmv"])
    
    if uploaded_file is not None:
        # Verifique as imagens de pele e processe o vídeo
        tem_pele = verifica_imagens_de_pele(uploaded_file)
        
        if tem_pele == True:
            st.write("Imagens de pele foram encontradas.")
            #st.video(video_path)
            
            # Para usar o Yolov5
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
            out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width, frame_height))

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
                    #xmin, ymin, xmax, ymax = detection[0:4]  # Valores x, y, largura (w) e altura (h)
                    #x_min, y_min, x_max, y_max = detection[0:4]
                    

                            
                    x1, y1, x2, y2 = map(int, detection[0:4])  
                    roi = frame[y1:y2, x1:x2]
                    roi_pcrt=(x1, y1, x2, y2)
                    st.write(f"Yolov5 x: {x1}, y: {y1}, x2: {x2}, y2: {y2}")      
                                                
                    # Redimensione a imagem para o tamanho desejado
                    new_width = 200  # Largura desejada
                    new_height = 150  # Altura desejada
                    roi_resized = cv2.resize(roi, (new_width, new_height))

                    # Exiba a imagem redimensionada
                    st.image(roi_resized, channels="BGR")        
                    #st.image(roi,channels ="BGR")
                    detected_frame_resized =cv2.resize(detected_frame, (new_width, new_height))
                    #st.image(detected_frame, caption=f"Detecção {detections_found + 1}", use_column_width=True,channels ="BGR")
                    st.image(detected_frame, caption=f"Detecção {detections_found + 1}", use_column_width=True,channels ="BGR")
                             
                    # Converte para números inteiros
                    xo1 = int((x1 + x2) / 2)
                    yo1 = int((y1 + y2) / 2)
                    xo2 = int(x2 - x1)
                    yo2 = int(y2 - y1)
                            
                    #t.write(f"YOLO xmin: {xmin}, ymin: {ymin}, xmax: {xmax}, ymax: {ymax}")
                    
                    st.write(f"OpenCV x: {xo1}, y: {yo1}, x2: {xo2}, y2: {yo2}")
                           
                    st.write("Processando vídeo...")
                    processed_data = process_video(temp_filename,roi_pcrt)  # Processar o vídeo
                    st.write(f"Resultados do processamento: {processed_data}")
                            
                    detections_found += 1

                    # Escreva o frame no vídeo de saída
                out.write(detected_frame)

            out.release()

                # Certifique-se de apagar o arquivo temporário após o uso
            os.remove(temp_filename)        
                
        else:
            st.write("Imagens de pele não foram encontradas, envie um novo vídeo")
        
else:
     st.write("Erro: Imagens de pele não foram encontradas, envie um novo vídeo")



# Crie um expander para a seção "Sobre"
expander = st.expander("+ Informações:")
# Conteúdo da seção "Sobre" dentro do expander
with expander:
    st.write("Desenvolvido por:")

    # Crie duas colunas para exibir as imagens lado a lado
    col1, col2 = st.beta_columns(2)

    # Adicione as imagens nas colunas
    with col1:
        st.image("logo_lab.png", use_column_width=True, width=50)

    with col2:
        st.image("logo_usp.png", use_column_width=True, width=50)

    # Adicionar um link no sidebar
    st.markdown(
        """
    [Visite nosso site](https://sites.usp.br/photobiomed/)
    [Informações sobre o pCRT](https://pycrt.readthedocs.io/en/latest/index.html)
        """)
    
    
    
    

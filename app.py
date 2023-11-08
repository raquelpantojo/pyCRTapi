"""
atualizado dia 06-10
16h35 Tentativa de adicionar o Yolo com a detecção pCRT --- ok
:: Próximos passos:
:: Reduzir o tamanho da imagem com detecção. -- ok 
:: Testar os valores de CRT com roi manual e roi do Yolo. -- ok


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

from PIL import Image
from io import BytesIO

from collections.abc import Iterable

## yolo v5
import torch
import tempfile
from collections.abc import Iterable

# YOLOv5 Model Loading
# Função para realizar a detecção da ponta do dedo
# Carregue o modelo YOLOv5 'finger.pt' localmente
model = torch.hub.load('ultralytics/yolov5', 'custom', path='finger.pt', force_reload=True,trust_repo=True)


# Streamlit Configuration
st.set_page_config(
    page_title="Cálculo do Tempo de Enchimento Capilar",
    layout="wide"
)

# Set the title of your Streamlit app
st.title(" :bar_chart: Cálculo do Tempo de Enchimento Capilar")

# Define a custom theme for the sidebar
custom_sidebar = """
.sidebar {
    background-color: #808000; /* Olive Green color code */
}
"""

# Apply the custom theme
st.markdown(f'<style>{custom_sidebar}</style>', unsafe_allow_html=True)
#st.markdown(f'<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


options = ["Calculo do CRT", "Resultados"]
icons = ["activity", "clipboard-data"]

import streamlit as st


# Define a dictionary that maps options to their corresponding icons
options = {
    "Calculo do CRT": " 👉 Calculo do CRT"}

# Use st.selectbox to display the options with icons
selected_option = st.sidebar.selectbox("Selecione uma opção:", list(options.keys()), format_func=lambda option: options[option], key="menu_options")




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
#opcao = st.radio("Selecione uma opção:", ("Fazer um video", "Enviar Vídeo Existente"))

#if opcao == "Fazer um video":
#    st.write("Ainda não é possivel fazer imagens com sua câmera")

# Exiba o ícone selecionado usando HTML
if selected_option == "Calculo do CRT":
  
#if opcao == option1:
    #"Enviar Vídeo Existente":
    uploaded_file = st.file_uploader(":file_folder: Carregar vídeo", type=["mp4", "avi", "wmv"])
    
    if uploaded_file is not None:
        # Verifique as imagens de pele e processe o vídeo
        tem_pele = verifica_imagens_de_pele(uploaded_file)
        
        if tem_pele == True:
            st.write("Imagens de pele foram encontradas.")
            st.write("Aguarde alguns minutos até carregar seu video")
            
            # Para usar o Yolov5
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_filename = temp_file.name
                temp_file.write(uploaded_file.read())
                
            
            # Abra o vídeo com o caminho do arquivo temporário
            video_capture = cv2.VideoCapture(temp_filename)

            # Inicialize variáveis
            detections_found = 0  # Quantas detecções encontradas
            target_detections = 1  # Quantidade de detecções desejadas

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
                    # Exiba a imagem redimensionada
                    roi = frame[y1:y2, x1:x2]
                    
                
                       
                                                
                    # Redimensione a imagem para o tamanho desejado
                    new_width = 150  # Largura desejada
                    new_height = 150  # Altura desejada
                    roi_resized = cv2.resize(roi, (new_width, new_height))
                    st.image(roi_resized, channels="BGR")     
                    # Converte para OpenCV
                    xo1 = int(((x1 + x2) / 2)-50)
                    yo1 = int(((y1 + y2) / 2)-50)
                    xo2 = int((x2 - x1))
                    yo2 = int((y2 - y1))
                    roi_pcrt=(xo1, yo1, xo2, yo2) 
                    #roi_pcrt=(230, 275, 97, 137)  

                       
                    
                    #detected_frame_resized =cv2.resize(detected_frame, (new_width, new_height))
                    #st.image(detected_frame, caption=f"Detecção {detections_found + 1}", use_column_width=True,channels ="BGR")
                    st.image(detected_frame, caption=f"Detecção {detections_found + 1}", width=detected_frame.shape[1] // 4, channels="BGR")


                    #st.write(f"Yolov5 x: {x1}, y: {y1}, x2: {x2}, y2: {y2}")   
                    #st.write(f"OpenCV x: {xo1}, y: {yo1}, x2: {xo2}, y2: {yo2}")
                           
                    st.write("Processando vídeo...")
                    #processed_data = process_video(temp_filename,roi_pcrt)  # Processar o vídeo
                    pycrtvalue, pycrtincert= process_video(temp_filename,roi_pcrt)
                    
                    # Depois de obter pycrtvalue e pycrtincert
                    if pycrtvalue > 5 and pycrtincert > 2 and pycrtincert/pycrtvalue < 0.10:
                        st.warning("Os valores do pCRT são maiores do que o esperado. \n Por favor, faça outro vídeo.")

                    #st.write(f"Resultados do processamento: {processed_data}")

                    #col1,col2 = st.columns((2))
                    
                    #for pycrtvalue, pycrtincert in processed_data.items():
                                    #st.write(f"{key}: {value}")
                    #with col1:
                    
                    st.write(f'<span style="font-size: 24px;">pCRT(s): <b>{pycrtvalue}</b> ± <b>{pycrtincert}</b>  </span>', unsafe_allow_html=True)


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



st.markdown("<br>" * 5)

# Crie um expander para a seção "Sobre"
expander = st.expander("+ Informações:")
with expander:
    st.write("Desenvolvido por:")
    st.image("logo_lab.png", use_column_width=True, width=50)
    st.image("logo_usp.png", use_column_width=True, width=50)
    
st.markdown("<br>" * 5) 
st.markdown("[Visite nosso site](https://sites.usp.br/photobiomed/)")
st.markdown("[Informações sobre o pCRT](https://pycrt.readthedocs.io/en/latest/index.html)")
    
    

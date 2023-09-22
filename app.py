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


# Configurar diretório de upload
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)



# Global variable for the stop event
stop_event = threading.Event()

# Function to capture video from the camera
def capturar_video(camera_index, output_filename):
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        st.error(f"Não foi possível acessar a câmera {camera_index}.")
        return

    # Defina as configurações para a gravação de vídeo
    width, height = int(cap.get(3)), int(cap.get(4))
    frame_rate = 30  # Taxa de quadros do vídeo (você pode ajustar conforme necessário)

    # Defina o codec de vídeo e crie o objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec de vídeo (no exemplo, está usando XVID)
    out = cv2.VideoWriter(output_filename, fourcc, frame_rate, (width, height))
    
    st.write(f"Pressione o botão para começar a gravar da câmera {camera_index}")

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            st.error(f"Erro ao capturar vídeo da câmera {camera_index}.")
            break

        out.write(frame)  # Escreve o quadro no arquivo de vídeo
        st.image(frame, channels="BGR", use_column_width=True)
    
    cap.release()
    out.release()

# Streamlit app
st.title("Video Capture and Display Example")

# Permitir que o usuário selecione uma câmera
camera_index = st.number_input("Digite o índice da câmera:", min_value=0, step=1)

output_filename = "captured_video.avi"

# Botões "Start" e "Stop" diretamente ao lado da câmera
start_button = st.button("Start")
stop_button = st.button("Stop")

if start_button:
    video_thread = threading.Thread(target=capturar_video, args=(int(camera_index), output_filename))
    video_thread.start()

if stop_button:
    # Set the stop event to stop video capture
    stop_event.set()


# Display the captured video
if os.path.exists(output_filename):
    st.write("Captured Video:")
    st.video(output_filename)


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

        #limite_percentagem_pele = 1  # Defina um limite de porcentagem aqui
        print(f"imagem_hsv shape: {imagem_hsv.shape}")
        print(f"imagem_ycrcb shape: {imagem_ycrcb.shape}")          
        if np.count_nonzero(skinMask) > 0:
            tem_imagem_de_pele = True
            break
                

    cap.release()

    return tem_imagem_de_pele, skin, imagem_hsv, imagem_ycrcb  # Retorna também a skin_mask e a imagem_ycrcb


# Interface do Streamlit
st.title("Detecção de pyCRT")
st.write("Carregue um arquivo de vídeo para realizar o teste do CRT.")

opcao = st.radio("Selecione uma opção:", ("Fazer um video", "Enviar Vídeo Existente"))

camera_index = st.camera_input("Fazer um vídeo")  # Pode escolher entre diferentes câmeras

if opcao == "Fazer um video"and os.path.exists(output_filename):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                st.image(frame, channels="BGR", use_column_width=True)
        cap.release()


        st.write("Vídeo Capturado:")
        st.video(output_filename)

        if st.button("Iniciar Gravação", key=f"start_button_{camera_index}"):
            output_filename = f"video_capturado_camera_{camera_index}.avi"
            capturar_video(camera_index, output_filename)  # Inicie a gravação

            # Após a gravação, exiba o vídeo gravado
            st.video(output_filename)
        # Verifique se camera_index não é None antes de chamar capturar_video
        if camera_index is not None:
            output_filename = f"video_capturado_camera_{camera_index}.avi"
            
            if st.button("Iniciar Gravação"):
                capturar_video(camera_index, output_filename)  # Chame a função para gravar o vídeo

                # Após a gravação, exiba o vídeo gravado
                st.video(output_filename)

else:
    uploaded_file = st.file_uploader("Carregar vídeo", type=["mp4", "avi", "wmv"])
    if uploaded_file is not None:
        video_path = os.path.join(uploads_dir, uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())  # Salva o arquivo enviado pelo usuário
        # Verifique as imagens de pele e processe o vídeo
        tem_pele, mascara_final, imagem_hsv, imagem_ycrcb = verifica_imagens_de_pele(uploaded_file)
        if tem_pele:
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
            if ret:
                frame_ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                st.image(frame_ycrcb, channels="BGR", use_column_width=True, caption=f"Quadro {frame_number} em YCrCb")

            cap.release()

        else:
            st.write("Não foram encontradas imagens de pele.")
            st.video(video_path)




# Exibir os logos no rodapé com o texto "Desenvolvido por:" e fundo preto
st.markdown(
    """
<style>
.sidebar .sidebar-content {
    background-color: #000000;
    color: white;
}
</style>
""",
    unsafe_allow_html=True,
)

st.sidebar.write("Desenvolvido por:")
st.sidebar.image("logo_lab.png", use_column_width=True, width=150)
st.sidebar.image("logo_usp.png", use_column_width=True, width=150)

# Adicionar um link no sidebar
st.sidebar.markdown(
    """
[Visite nosso site](https://sites.usp.br/photobiomed/)
"""
)

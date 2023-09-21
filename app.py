import streamlit as st
import os
import cv2
import numpy as np
from process_video import process_video  # Importe a função process_video do seu módulo

# Configurar diretório de upload
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)



# Função para capturar a imagem da webcam
def capturar_imagem():
    cap = cv2.VideoCapture(0)  # 0 representa a câmera padrão (geralmente a webcam)
    
    if not cap.isOpened():
        st.error("Não foi possível acessar a webcam.")
        return

    st.write("Pressione o botão para capturar uma imagem da webcam")
    if st.button("Capturar"):
        ret, frame = cap.read()
        if ret:
            # Exibe a imagem capturada
            st.image(frame, channels="BGR", use_column_width=True, caption="Imagem Capturada")
            # Salva a imagem capturada em um arquivo (opcional)
            cv2.imwrite("imagem_capturada.jpg", frame)
        else:
            st.error("Não foi possível capturar a imagem.")

        cap.release()

capturar_imagem()



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

opcao = st.radio("Selecione uma opção:", ("Tirar uma Foto da Câmera", "Enviar Vídeo Existente"))

if opcao == "Fazer um video":
    img_file_buffer = st.camera_input("Tirar uma foto")
    if img_file_buffer is not None:
        st.image(img_file_buffer, use_column_width=True, caption="Imagem Capturada")
        # Você pode processar a imagem aqui se necessário.
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

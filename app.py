import streamlit as st
import cv2
import numpy as np

# Configurações do Streamlit
st.set_page_config(page_title='Capturar e Salvar Vídeo', layout='centered')

# Inicialize a captura de vídeo usando a OpenCV
cap = cv2.VideoCapture(0)  # Use 0 para a câmera padrão, você pode ajustar o índice se tiver várias câmeras.

# Verifique se a captura de vídeo foi inicializada com sucesso
if not cap.isOpened():
    st.error('Erro ao inicializar a captura de vídeo')
else:
    st.success('Captura de vídeo inicializada com sucesso')

# Botão para iniciar a gravação
start_recording = st.button('Iniciar Gravação')
recording = False
out = None

if start_recording:
    # Inicialize a gravação de vídeo
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Escolha o codec apropriado
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))  # Defina o nome do arquivo, codec, taxa de quadros e resolução
    recording = True
    st.success('Iniciando gravação de vídeo. Clique em "Parar Gravação" para interromper.')

# Loop principal do aplicativo
while True:
    ret, frame = cap.read()
    if ret:
        # Se estiver gravando, salve o quadro no arquivo de saída
        if recording and out is not None:
            out.write(frame)

        # Exiba o quadro no aplicativo
        st.image(frame, channels='BGR', use_column_width=True)

        if not recording and out is not None:
            out.release()
            break

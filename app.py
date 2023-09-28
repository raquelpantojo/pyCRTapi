import streamlit as st
import cv2
import os
from pyCRT import PCRT
import numpy as np
import time

from PIL import Image

def start_capture():
    cap = cv2.VideoCapture(1)
    out = cv2.VideoWriter('video1.avi', cv2.VideoWriter_fourcc(*'XVID'), 24.0, (1280, 720))

    st.image(np.zeros((1, 1, 3)))  # Placeholder para o vídeo

    st.write("Iniciando captura de vídeo. Aguarde...")

    number = 0
    textmsg = ""
    increment_time = 0.1
    roi = (562, 332, 150, 161)  # Região de interesse na imagem da câmera

    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            st.write("Erro na captura de vídeo. Verifique sua câmera.")
            break
        
        out.write(frame)

        # Converter o quadro OpenCV em um formato compatível com o Streamlit (Pillow)
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        st.image(pil_image, use_column_width=True)  # Exibir a imagem

        st.write(f"Cronômetro: {number:.1f}")
        if number > 2 and number <= 4:
            textmsg = 'Posicione o dedo indicador no círculo'
        if number > 5 and number <= 11:
            textmsg = 'Aperte'
        if number >= 11:
            textmsg = 'Libere'
        if number >= 12:
            textmsg = 'Aguarde'
        if number >= 16:
            textmsg = 'Calcule o CRT'
            # Interrompa a captura aqui e faça o cálculo do CRT
            pycrt = PCRT.fromVideoFile("video1.avi", roi=roi, displayVideo=False, exclusionCriteria=0.6)
            pycrtvalue = round(pycrt.pCRT[0], 2)
            pycrtincert = round(pycrt.pCRT[1], 2)

            st.write(f"pCRT: {pycrtvalue} s")
            st.write(f"Incerteza: {pycrtincert} s")

            break

        time.sleep(increment_time)
        number += increment_time

    cap.release()

# Função principal do Streamlit
def main():
    st.title("Aplicativo de Captura de Vídeo")
    st.sidebar.header("Configurações")

    video_resolution = st.sidebar.selectbox("Resolução de Vídeo", ["480p", "720p", "1080p", "4k"])
    st.write(f"Resolução selecionada: {video_resolution}")

    if st.button("Iniciar Captura de Vídeo"):
        start_capture()

if __name__ == "__main__":
    main()

import streamlit as st
import cv2
import numpy as np

def main():
    st.title("Aplicação de Captura de Vídeo")

    option = st.radio("Selecione uma opção:", ("Fazer um vídeo", "Enviar Vídeo Existente"))

    if option == "Fazer um vídeo":
        camera_index = st.camera_input("Selecione uma câmera")  # Escolha a câmera

        st.write("Iniciando a captura de vídeo. Aguarde...")

        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            st.write("Erro ao iniciar a câmera. Verifique a configuração da câmera.")
            return

        out = cv2.VideoWriter('video1.avi', cv2.VideoWriter_fourcc(*'XVID'), 24.0, (1280, 720))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            st.image(frame, channels="BGR", use_column_width=True)

            out.write(frame)

        cap.release()
        out.release()

    elif option == "Enviar Vídeo Existente":
        st.write("Opção 'Enviar Vídeo Existente' selecionada. Faça o upload de um vídeo existente.")

if __name__ == "__main__":
    main()

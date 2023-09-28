import streamlit as st
import cv2
import numpy as np

def main():
    st.title("Aplicação de Captura de Vídeo")

    option = st.radio("Selecione uma opção:", ("Fazer um vídeo", "Enviar Vídeo Existente"))

    if option == "Fazer um vídeo":
        camera_index = st.camera_input("Câmera:")  # Escolha a câmera

        st.write("Iniciando a captura de vídeo. Aguarde...")

        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            st.write("Erro ao iniciar a câmera. Verifique a configuração da câmera.")
            return

        out = None
        recording = False

        start_stop_button = st.button("Iniciar Gravação" if not recording else "Parar Gravação")  # Botão para iniciar e parar a gravação

        if start_stop_button:
            recording = not recording
            if recording:
                out = cv2.VideoWriter('video1.avi', cv2.VideoWriter_fourcc(*'XVID'), 24.0, (1280, 720))
            else:
                out.release()

        while recording:
            ret, frame = cap.read()
            if not ret:
                break

            st.image(frame, channels="BGR", use_column_width=True)

            if recording:
                out.write(frame)

        cap.release()

        if out:
            st.write("Gravação concluída. Clique no botão abaixo para ver o vídeo.")
            if st.button("Mostrar Vídeo Gravado"):
                show_video('video1.avi')

    elif option == "Enviar Vídeo Existente":
        st.write("Opção 'Enviar Vídeo Existente' selecionada. Faça o upload de um vídeo existente.")

def show_video(video_path):
    video_file = open(video_path, 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

if __name__ == "__main__":
    main()

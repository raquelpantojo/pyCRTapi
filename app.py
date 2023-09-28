import streamlit as st
from streamlit_webrtc import webrtc_streamer
from webrtc_streamer import VideoProcessorBase
import cv2

# Configura a permissão da câmera
st.set_option('server.enableCORS', False)

# Variável para controlar a gravação
recording = False
out = None

# Defina a classe VideoProcessor para processar os quadros de vídeo e salvar em um arquivo
class VideoProcessor(VideoProcessorBase):
    def __init__(self, output_file):
        self.output_file = output_file
        self.out = None

    def recv(self, frame):
        if recording:
            if self.out is None:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.out = cv2.VideoWriter(self.output_file, fourcc, 24.0, (frame.width, frame.height))
            self.out.write(frame.to_ndarray(format="bgr24"))
        else:
            if self.out:
                self.out.release()
                self.out = None

def main():
    st.title("Aplicação de Captura e Gravação de Vídeo")

    output_file = "video1.avi"

    webrtc_ctx = webrtc_streamer(
        key="example",
        mode=0,
        video_processor_factory=VideoProcessor,
        async_processing=True,
        output_file=output_file,
    )

    global recording
    start_stop_button = st.button("Iniciar Gravação" if not recording else "Parar Gravação")
    
    if start_stop_button:
        recording = not recording

    if recording:
        st.write("Gravação em andamento. Clique no botão 'Parar Gravação' para encerrar.")
    else:
        st.write("Clique no botão 'Iniciar Gravação' para iniciar a gravação.")

    if st.button("Mostrar Vídeo Gravado"):
        show_video(output_file)

def show_video(video_path):
    video_file = open(video_path, 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

if __name__ == "__main__":
    main()

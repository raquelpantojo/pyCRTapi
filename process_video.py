# process_video.py

from pyCRT import PCRT
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import cv2

def process_video(video_path,roi):
    # Process the video using pyCRT
    #roi=(872, 477, 195, 205)
    #roi=(872, 477, 195, 205)
    #roi = (191, 454, 109, 143)
    #pcrt = PCRT.fromVideoFile(video_path)
   pcrt = PCRT.fromVideoFile(video_path,roi=roi,displayVideo=False,exclusionMethod='best fit',exclusionCriteria=9999999)
    
   #(1.9553732602812774, 0.15108928992342496)
   
   # Get the values you want from the pcrt object
   pycrtvalue = pcrt.pCRT[0].__round__(2) 
   pycrtincert = pcrt.pCRT[1].__round__(2) 
    


   # Inicialize a captura de vídeo
   cap = cv2.VideoCapture(video_path)

   # Inicialize listas para armazenar os valores médios dos canais RGB
   mean_red_values = []
   mean_green_values = []
   mean_blue_values = []

   while True:
      ret, frame = cap.read()
      if not ret:
         break

      # Divida o quadro em canais RGB
      b, g, r = cv2.split(frame)

      # Calcule a média dos canais RGB e adicione à lista
      mean_red = np.mean(r)
      mean_green = np.mean(g)
      mean_blue = np.mean(b)

      mean_red_values.append(mean_red)
      mean_green_values.append(mean_green)
      mean_blue_values.append(mean_blue)

   # Crie uma lista de tempo (em segundos) com base no número de quadros
   frame_count = len(mean_red_values)
   frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
   time_values = [i / frame_rate for i in range(frame_count)]

   # Plote os valores médios ao longo do tempo
   plt.plot(time_values, mean_red_values, 'r', label='Canal R')
   plt.plot(time_values, mean_green_values, 'g', label='Canal G')
   plt.plot(time_values, mean_blue_values, 'b', label='Canal B')

   # Configuração do gráfico
   plt.xlabel('Tempo (s)')
   plt.ylabel('Valor Médio')
   plt.title('Valores Médios dos Canais RGB ao Longo do Tempo')
   plt.legend()

   # Exibir o gráfico
   plt.show()

   # Libere a captura de vídeo
   cap.release()

    
   return {'pCRT': pycrtvalue, 'incerteza': pycrtincert}

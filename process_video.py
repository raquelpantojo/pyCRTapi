# process_video.py

from pyCRT import PCRT
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
    
   # Gerar gráfico do canal verde
    plt.figure()
    plt.imshow(pcrt.video.data[:, :, 1], cmap='Greens')  # Use the green channel for the image
    plt.colorbar()
    plt.title('Green Channel')
    
    # Exibir o gráfico no Streamlit
    st.pyplot()
   
    
   return {'pCRT': pycrtvalue, 'incerteza': pycrtincert}

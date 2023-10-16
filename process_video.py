# process_video.py

from pyCRT import PCRT
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def process_video(video_path,roi,xo1, yo1, xo2, yo2):
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
    
   # Gerar gráficos
   pcrt.showPCRTPlot()
    
   # Pegar a figura gerada pelo PCRT
   fig = plt.gcf()

   # Exibir o gráfico no Streamlit
   st.pyplot(fig)
    
   return {'pCRT': pycrtvalue, 'incerteza': pycrtincert}

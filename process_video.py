# process_video.py

from pyCRT import PCRT

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
    
    # Save the values to the txt file
    #result_txt_path = "runs/detect/processed_result.txt"
    #with open(result_txt_path, 'w') as file:
    #    file.write(f'pCRT: {pycrtvalue}, incerteza: {pycrtincert}')

    return {'pCRT': pycrtvalue, 'incerteza': pycrtincert}

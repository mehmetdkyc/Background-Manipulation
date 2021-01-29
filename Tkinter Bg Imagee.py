# -*- coding: utf-8 -*-  
from tkinter import *
from tkinter import filedialog
from PIL import  Image,ImageTk
from PIL import Image
import cv2
import argparse
import numpy as np
import os

#== Parameters =======================================================================
BLUR = 21
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 100
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10

class GUI(Frame):

    def __init__(self, master=None):
        
        Frame.__init__(self, master)
        w,h = 1000, 1000
        master.minsize(width=w, height=h)
        master.maxsize(width=w, height=h)
        self.pack()
    
        
        ForegroundButton= Button(self, text='Choose Foreground Image', width=20, height=2, command=self.chooseForeground)  
        ForegroundButton.pack(side=RIGHT)
        self.file = ForegroundButton
        
        BackgroundButton = Button(self, text='Choose Background Image', width=20, height=2, command=self.chooseBackground) 
        BackgroundButton.pack(side=LEFT)
        self.file = BackgroundButton
         
        ManipulateButton = Button(self, text='Manipulate', width=20, height=2, command=self.manipulate) 
        ForegroundButton.pack(side=LEFT)
        self.file = ManipulateButton
        #Replace with your image
        self.image = PhotoImage(file='background.png')
        self.label = Label(image=self.image)
    
        self.file.pack()
        self.label.pack()
    def chooseForeground(self):
        
        myForegroundFilePath = filedialog.askopenfile(parent=self,mode='rb',title='Choose a file')
        path = Image.open(myForegroundFilePath)
        print('*****************')
        print(path)
        print('*****************')
       
        
        print('====================')
        myPathName = myForegroundFilePath.name
        global myFgFileName
        myFgFileName = os.path.basename(myPathName)
        print(myFgFileName)
        print('====================') 
        return myFgFileName
        
        
    def chooseBackground(self):
        myBackgroundFilePath = filedialog.askopenfile(parent=self,mode='rb',title='Choose a file')
        path = Image.open(myBackgroundFilePath)
        print('*****************')
        print(path)
        print('*****************')
       
        
        print('====================')
        myPathName = myBackgroundFilePath.name
        global myBgFileName
        myBgFileName = os.path.basename(myPathName)
        print(myBgFileName)
        print('====================') 
        
        return myBgFileName
         
    def manipulate(self): 

        img = cv2.imread(myFgFileName) 
        
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
        edges = cv2.dilate(edges, None)
        edges = cv2.erode(edges, None)
        
        #-- Find contours in edges, sort by area ---------------------------------------------
        contour_info = []
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        for c in contours:
            contour_info.append((
                c,
                cv2.isContourConvex(c),
                cv2.contourArea(c),
            ))
        contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
        
        #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
        # Mask is black, polygon is white
        mask = np.zeros(edges.shape)
        for c in contour_info:
            cv2.fillConvexPoly(mask, c[0], (255))
        
        #-- Smooth mask, then blur it --------------------------------------------------------
        mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
        mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
        mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
        
        #-- Blend masked img into MASK_COLOR background --------------------------------------
        img= img.astype('float32') / 255.0
        
        c_red, c_green, c_blue = cv2.split(img)
        img_a = cv2.merge((c_red, c_green, c_blue, mask.astype('float32') / 255.0))
        
        cv2.imwrite("new.png", img_a*255)
        
        #-----------------------
        #combine two images into a single
        
        img = Image.open("new.png")
        background = Image.open(myBgFileName)
        
        #resize
        size=(1000,750)
        img=img.resize(size,Image.ANTIALIAS)
        background=background.resize(size,Image.ANTIALIAS)
        
        
        background.paste(img, (0, 0), img)
        background.save('tkinterfinal.png',"PNG")
        self.image = PhotoImage(file='tkinterfinal.png')
     
        
    

root = Tk()
app = GUI(master=root)
app.mainloop()
root.destroy()
# Name:            CompressImagery
#
# Version:         2.0
#
# Purpose:         Locates Tiff images in a workspace and creates an
#                  array. The rasters in the array are then compressed
#                  using JPEG compression and overviews are created using
#                  GDAL and FWTools by Frank Warmerdam.
#
# Author:          Collaborative development effort from
#                  Eric J. Rodenberg, Esri,
#                  Tom Brenneman, Esri,
#			       J.D. Overton, Esri
#
# Acknowledgments: Thanks to Peter Becker, Esri, for his input into this project.
#
# Date:            Thursday, June 25, 2009
# Updated: 		   Thursday, December 2, 2010
#
# Python Version:  Python 2.6.5 (r265:79096, Mar 19 2010, 21:48:26) [MSC v.1500 32 bit (Intel)] on win32]
#
# Copyright 2001-2010 ESRI.
# All rights reserved under the copyright laws of the United States.
# You may freely redistribute and use this sample code, with or without
# modification. The sample code is provided without any technical support or
# updates.
#
# Disclaimer OF Warranty: THE SAMPLE CODE IS PROVIDED "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY
# FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT ARE DISCLAIMED. IN NO
# EVENT SHALL ESRI OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) SUSTAINED BY YOU OR A THIRD PARTY, HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT ARISING IN ANY WAY OUT OF THE USE OF THIS SAMPLE CODE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE. THESE LIMITATIONS SHALL APPLY
# NOTWITHSTANDING ANY FAILURE OF ESSENTIAL PURPOSE OF ANY LIMITED REMEDY.
#
# For additional information contact:
#
# Environmental Systems Research Institute, Inc.
# Attn: Contracts Dept.
# 380 New York Street
# Redlands, California, U.S.A. 92373
# Email: contracts@esri.com
#***********************************************************************
import os, tkMessageBox, ConfigParser, shutil
from Tkinter import *
from tkFileDialog import *

class App:
 def __init__(self, master):
  frame = Frame(master)
  frame.grid(row=0)

  self.lblWorkspace = Label(frame, text="Imagery to be Compressed:", font=("Helvetica",10))
  self.lblWorkspace.grid(row=1, sticky=W)
  self.lstWorkspace = Entry(frame, width=35, font="Helvetica 10 bold")
  self.lstWorkspace.grid(row=1, column=1)
  self.btnWorkspace = Button(frame, text="Browse", font=("Helvetica",10), command=self.locateWorkspace)
  self.btnWorkspace.grid(row=1, column=2, padx=5, pady=5, sticky=W)

  self.lblOutdir = Label(frame, text="Output Compressed Imagery:", font=("Helvetica",10))
  self.lblOutdir.grid(row=2, sticky=W)
  self.lstOutdir = Entry(frame, width=35, font="Helvetica 10 bold")
  self.lstOutdir.grid(row=2, column=1)
  self.btnOutdir = Button(frame, text="Browse", font=("Helvetica",10), command=self.locateOutdir)
  self.btnOutdir.grid(row=2, column=2, padx=5, pady=5, sticky=W)

  self.lblFwtools = Label(frame, text="FWTools Directory:", font=("Helvetica",10))
  self.lblFwtools.grid(row=3, sticky=W)
  self.FwtoolsVar = StringVar()
  # Read Configuration File
  config = ConfigParser.ConfigParser()
  config.readfp(open('CompressImagery.cfg'))
  fwtoolsVAR = config.get('FWTools Path', 'fwTools')
  self.FwtoolsVar.set(os.path.normpath(fwtoolsVAR))
  self.lstFwtools = Entry(frame, width=35, font="Helvetica 10 bold", textvariable=self.FwtoolsVar)
  self.lstFwtools.grid(row=3, column=1)
  self.btnFwtools = Button(frame, text="Browse", font=("Helvetica",10), command=self.locateFwTools)
  self.btnFwtools.grid(row=3, column=2, padx=5, pady=5, sticky=W)

  self.photometricOverview = StringVar()
  self.lblRadPhotometric = Label(frame, text="Photometric Overview", font=("Helvetica",10))
  self.lblRadPhotometric.grid(row=4, column=0, sticky=W)
  self.radPhotometric1 = Radiobutton(frame, text="Natural Color", variable=self.photometricOverview, value="YCBCR")
  self.radPhotometric1.grid(row=5, column=0, sticky=W)
  self.radPhotometric1.select()
  self.radPhotometric2 = Radiobutton(frame, text="Non-Natural Color", variable=self.photometricOverview, value="RGB")
  self.radPhotometric2.grid(row=6, column=0, sticky=W)
  self.radPhotometric2.deselect()

  self.lblImageQuality = Label(frame, text="Image Quality", font=("Helvetica",10))
  self.lblImageQuality.grid(row=4, column=1)
  self.imageQualityVar = IntVar()
  self.imageQualityVar.set(90)
  self.imageQuality = Scale(frame, from_=0, to=100, orient=HORIZONTAL, variable=self.imageQualityVar)
  self.imageQuality.grid(row=5, column=1, rowspan=2, sticky=E+W+N+S)

  self.lblDelOrig = Label(frame, text="Delete Original Images", font=("Helvetica",10))
  self.lblDelOrig.grid(row=4, column=2, sticky=W)
  self.delOrig = StringVar()
  self.radDelOrig1 = Radiobutton(frame, text="Yes", variable=self.delOrig, value="Yes")
  self.radDelOrig1.grid(row=5, column=2, sticky=W)
  self.radDelOrig1.deselect()
  self.chkDelOrig2 = Radiobutton(frame, text="No", variable=self.delOrig, value="No")
  self.chkDelOrig2.grid(row=6, column=2, sticky=W)
  self.chkDelOrig2.select()

  self.btnHelp = Button(frame, text="Help", font=("Helvetica",10), height=3, width=10, command=self.launchHelp)
  self.btnHelp.grid(row=8, column=1, sticky=E )
  self.btnExecuteCompress = Button(frame, text="Execute", font=("Helvetica",10), height=3, width=10, command=self.onEnterValidate)
  self.btnExecuteCompress.grid(row=8, column=2, sticky=W, padx=5, pady=5 )

 def locateWorkspace(self):
  inDir = askdirectory(parent=root, title="Select a Folder", initialdir="/", mustexist=1)
  if len(self.lstWorkspace.get()) == 0 :
   self.lstWorkspace.insert(0,os.path.normpath(inDir))
   message = tkMessageBox.askyesno("Compress Imagery", "Would you like to create a new directory titled " +
                                   self.lstWorkspace.get() + "_Compressed?\n" +
                                   "Click Yes to create the directory or No to use your own.")
   if message is True:
    if not os.path.exists(os.path.normpath(inDir) + "_Compressed"):
     os.mkdir(os.path.normpath(inDir) + "_Compressed")
     self.lstOutdir.insert(0,os.path.normpath(inDir) + "_Compressed")
    else:
     self.lstOutdir.insert(0,os.path.normpath(inDir) + "_Compressed")
  else:
   self.lstWorkspace.delete(0,'end')
   self.lstWorkspace.insert(0,os.path.normpath(inDir))

 def locateOutdir(self):
  os.chdir(os.path.normpath(self.lstWorkspace.get()))
  OutDir = askdirectory(parent=root, title="Select a Folder", initialdir=os.chdir(os.pardir), mustexist=1)
  if len(self.lstOutdir.get()) == 0 :
   self.lstOutdir.insert(0,os.path.normpath(OutDir))
  else:
   self.lstOutdir.delete(0,'end')
   self.lstOutdir.insert(0,os.path.normpath(OutDir))

 def locateFwTools(self):
  fwDir = askdirectory(parent=root, title="Locate FWTools", initialdir=os.path.normpath(self.FwtoolsVar.Get()), mustexist=1)
  if len(self.lstFwtools.get()) == 0 :
   self.lstFwtools.insert(0,fwDir)
  else:
   self.lstFwtools.delete(0,'end')
   self.lstFwtools.insert(0, fwDir)

 def launchHelp(self):
  os.system("Help.pdf")

 def onEnterValidate(self):
  if len(self.lstWorkspace.get()) == 0 :
   tkMessageBox.showwarning("Compress Imagery", "Input Workspace cannot be empty!")
   if len(self.lstWorkspace.get()) == 0 :
   	return
  if len(self.lstOutdir.get()) == 0 :
   tkMessageBox.showwarning("Compress Imagery", "Output directory cannot be empty!")
   if len(self.lstOutdir.get()) == 0 :
   	return
  if os.path.exists(self.lstFwtools.get())==False:
  	message = tkMessageBox.showerror("Compress Imagery", "The FWTools Directory is invalid or does not exist!" +
							 " Check to make sure that FWTools is installed and the FWTools Path is correct.")
  	if os.path.exists(self.lstFwtools.get())==False:
  	 return
  if len(self.lstFwtools.get()) == 0 :
   tkMessageBox.showwarning("Compress Imagery", "FWTools directory cannot be empty!")
  if self.imageQualityVar.get() < 80 :
   message = tkMessageBox.askokcancel("Image Quality", "Setting the image quality below " +
  						  "80 will increase compression ratios making images " +
    					  "smaller, but this will also introduce subimage " +
      				      "artifacts. Loss of high resolution information can " +
      				      "also occur. It is recommended that you save the original images.")
   if message is False:
   	  return
  if self.photometricOverview.get() == "YCBCR":
   message = tkMessageBox.askyesno("Photometric Overview", "You choose Natural Color Photometric " +
                                   "Interpretation. If your imagery is either single band or 4 bands or more " +
                                   " the resulting imagery will not compress correctly. " +
                                   "\n" +
                                   "Examples of 4 band imagery are Color Infrared." +
                                   "\n" +
                                   "Examples of single band imagery include Black and White Aerial Photography" +
                                   "\n" +
                                   "Is your Imagery 3 Band Color Aerial Photography?")
   if message is False:
    self.photometricOverview.set("RGB")
    self.radPhotometric1.deselect()
    self.radPhotometric2.select()
  customizeCompressRoutine = self.CreateBAT()

 def CreateBAT(self):
  compress_BAT = open(os.path.normpath(self.lstOutdir.get()) + "\\compress.bat", 'w')
  lines = ["rem this batch file requires fwtools installed from: http://fwtools.maptools.org/\n",
	    "rem gdal_translate is documented here: http://www.gdal.org/gdal_translate.html\n",
        "rem %1 is the tiff image\n",
        "rem %2 is the output directory specified in the python dialog\n",
        "rem %3 is a temp file name\n",
        "\n",
	    "set fwtoolsFolder=" +'"' + os.path.normpath(self.lstFwtools.get()) + '"' + "\n",
	    "set compressionQuality=" + str(self.imageQualityVar.get()) +"\n",
	    "set photoMetric=" + self.photometricOverview.get() + "\n",
	    "\n",
	    "set tempfile=%2\\%3\n",
	    "\n",
	    "%fwtoolsFolder%\\bin\\gdal_translate -of GTiff -co COMPRESS=JPEG -co PHOTOMETRIC=%photoMetric% -co JPEG_QUALITY=%compressionQuality% -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 -co tiled=yes -co TFW=yes %1 %tempFile% \n",
	    "%fwtoolsFolder%\\bin\\gdaladdo -ro --config COMPRESS_OVERVIEW JPEG --config USE_RRD NO --config TILED Yes --config JPEG_QUALITY 80 --config PHOTOMETRIC_OVERVIEW %photoMetric% %tempFile% 2 4 8 16 32 64 128"]
  compress_BAT.writelines(lines)
  compress_BAT.close()
  CompressTiffs = self.CompressImages()

 def CompressImages(self):
  # Set the workspace. List all of the TIFF files
  workspace = os.path.normpath(self.lstWorkspace.get())
  compressBatchFile = os.path.normpath(self.lstOutdir.get()) + "\\compress.bat"
  outDIR = os.path.normpath(self.lstOutdir.get())

  # For each raster in the list of rasters
  os.chdir(workspace)
  for tiff in os.listdir("."):
    if tiff.lower().endswith(".tif"):
      cmd = compressBatchFile + " " + tiff +  " " + outDIR + " " + tiff
      os.system(cmd)
    elif tiff.lower().endswith(".tiff"):
      cmd = compressBatchFile + " " + tiff + " " + outDIR + " " + tiff
      os.system(cmd)
  appCleanup = self.CompressCleanup()

 def CompressCleanup(self):
  os.remove(os.path.normpath(self.lstOutdir.get()) + "\\compress.bat")
  if self.delOrig.get() == "Yes":
    shutil.rmtree(os.path.normpath(self.lstWorkspace.get()))
  tkMessageBox.showinfo("Compress Imagery", "Image Compression was successful!")
  root.destroy()

root = Tk()
root.geometry('640x260+300+300')
#root.iconbitmap('EsriGlobe.ico')
root.title('Compress Imagery')

app = App(root)
root.mainloop()
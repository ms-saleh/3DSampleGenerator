# -*- coding: utf-8 -*-
"""
Created on Fr Mar 12 13:36:25 2021

@author: Sadeq Saleh @ Cornell.edu

Get the design of experiment for micro channe arrays, build the geometery in 
nTopology Platform and create buildfiles in Nanoscribe
"""
import os
import subprocess
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
from getpass import getpass 

class buildSample(object):
    exePath = r"C:/Program Files/nTopology/nTopology/ntopCL.exe"
    cleanUp = True
    blockNumbers = 0
    
    def __init__(self,path):
        self.path = path
        self.setOutputPath(path)
        self.setSTLPath(self.outputPath+'\\STL')
        self.setBuildPath(self.outputPath+"\\BuildFiles")
    
    def setOutputPath(self, outputPath):
        self.outputPath=outputPath
    
    def setSTLPath(self, STLPath):


        self.STLPath=STLPath
    
    def setBuildPath(self, buildPath):
        self.buildPath=buildPath
    
    def setSampleName(self,sampleName):
        self.sampleName=sampleName
    
    def summary(self):
        print('{:>20} {}'.format('Sample Name:',self.sampleName))
        print('{:>20} {}'.format('Costum nTop Block:',self.customBlock))
        print('{:>20} {}'.format('Output Path:',self.outputPath))
        print('{:>20} {}'.format('STL Path:',self.STLPath))
        print('{:>20} {}'.format('Build Files Path:',self.buildPath))
        
    def readDOE(self):
        #look for DOE file
        for fname in os.listdir(self.path):
            if fname.endswith(".csv") and fname[:6]=="Sample":
                self.setSampleName(fname[:-4])
        #import the DOE dimensions from the Sample##.CSV
        with open(self.sampleName+'.csv',mode='r') as f:
            self.setDOE(f.readlines())
    
    def setDOE(self,DOE):
        self.DOE=DOE
    
    def readCustomBlock(self):
        for fname in os.listdir(self.path):
            if fname.endswith(".ntop") and fname[:3]=="CB_":
                self.setCustomBlock(fname)
    
    def setCustomBlock(self,nTop):
        self.customBlock=self.path+'\\'+nTop
        
    def setMeshMergeBlock(self):
        self.customBlock=self.path+'\\'+"MeshMerge.ntop"
    
    def setRecipe(self,recipe):
        self.recipe=self.path+'\\'+recipe
        
    def nTopTemplate(self):
        # Generate template for MicroChannel nTop
        Arguments = [self.exePath]                              #nTopCL path
        Arguments.append("-u")                                  #username argument
        Arguments.append(os.environ.get('nTop_user'))           #nTop username
        Arguments.append("-w")                                  #password argument
        Arguments.append(os.environ.get('nTop_pass'))           #nTop pass
        Arguments.append("-t")                                  #json template argument
        Arguments.append(self.customBlock)                      #.ntop notebook file path
        #nTopCL call with arguments
        #print(" ".join(Arguments))
        output,error = subprocess.Popen(Arguments,stdout = subprocess.PIPE, 
                   stderr= subprocess.PIPE).communicate()
        #Print the return messages
        print(output.decode("utf-8"))
    
    def nTopRun(self,jsonFile,nTopFile):
        # Generate template for MicroChannel nTop
        Arguments = [self.exePath]                              #nTopCL path
        Arguments.append("-u")                                  #username argument
        Arguments.append(os.environ.get('nTop_user'))           #nTop username
        Arguments.append("-w")                                  #password argument
        Arguments.append(os.environ.get('nTop_pass'))           #nTop pass
        Arguments.append("-j")                                  #json input argument
        Arguments.append(jsonFile)                              #input json file
        Arguments.append("-o")                                  #output argument
        Arguments.append(self.path+"\\"+"out.json")             #output json path
        Arguments.append(nTopFile)                              #.ntop notebook file path
        #nTopCL call with arguments
        # print("\n".join(Arguments))
        output,error = subprocess.Popen(Arguments,stdout = subprocess.PIPE, 
                   stderr= subprocess.PIPE).communicate()
        #Print the return messages
        print(output.decode("utf-8"))
    
    def createGyroidInputJSON(self):
        try:
            with open(self.path+"\\input_template.json") as f:
                Inputs_JSON = json.load(f)
        except:
            self.nTopTemplate()
            with open(self.path+"\\input_template.json") as f:
                Inputs_JSON = json.load(f)
        Dim = self.DOE
        self.json=[]
        Inputs_JSON['inputs'][0]['value']=self.STLPath+'\\QGyroid.stl'
        self.json.append(self.path+"\\input.json")
        for index, item in enumerate(Inputs_JSON['inputs'][1:]):
            item['value']=float(Dim[index])
        with open(self.path+"\\input.json", 'w') as outfile:
            json.dump(Inputs_JSON, outfile, indent=4)
     
    def createMeshMergeInputJSON(self):
        try:
            with open(self.path+"\\input_template.json") as f:
                Inputs_JSON = json.load(f)
        except:
            self.nTopTemplate()
            with open(self.path+"\\input_template.json") as f:
                Inputs_JSON = json.load(f)
        for index, item in enumerate(sorted(os.listdir(self.STLPath))):
            Inputs_JSON['inputs'][0]['value']=self.STLPath +"\\"+item
        fnt = ImageFont.truetype(r'/Library/Fonts/arial.ttf', 900)
        img = Image.new('RGB', (1000 , 1000), color = "black")
        d = ImageDraw.Draw(img)
        d.text((10,10), self.sampleName[-2:] , font=fnt, fill="blue")
        img.save(self.path+"\\"+self.sampleName[-2:]+".png")
        
        Inputs_JSON['inputs'][0]['value'] = self.STLPath +"\\Compartment.stl"
        Inputs_JSON['inputs'][1]['value'] = self.path +"\\"+ self.sampleName[-2:] + ".png"
        self.json=[]
        with open(self.path+"\\input.json", 'w') as outfile:
            json.dump(Inputs_JSON, outfile, indent=4)
        self.json.append(self.path+"\\input.json")
            
            
    def createTree(self):
        if os.path.isdir(self.STLPath):
            shutil.rmtree(self.STLPath)
        os.makedirs(self.STLPath)
        if os.path.isdir(self.buildPath):
            shutil.rmtree(self.buildPath)
        os.makedirs(self.buildPath)
        
    def createGyroidSTL(self):
        for JSON in self.json:
            self.nTopRun(JSON, self.customBlock)
            if self.cleanUp and os.path.isfile(JSON):
                os.remove(JSON)

    def createMeshMergeSTL(self):
        for JSON in self.json:
            self.nTopRun(JSON, self.customBlock)
            if self.cleanUp and os.path.isfile(JSON):
                os.remove(JSON)
    
    def createBottomRecipe(self,recipe):
        self.setRecipe(recipe)
        with open(self.recipe,mode='r') as f:
            Lines=f.readlines()
        f = open(self.buildPath+"\\Bottom_job.recipe",mode='w')
        f.truncate(0)
        f.close()
        f = open(self.buildPath+"\\Bottom_job.recipe",mode='a')
        for line in Lines:
            if line[:14]=="Model.FilePath":
                f.write(('Model.FilePath = '+self.STLPath +"\\Compartment.stl\n"))
            else:
                f.write(line)
        f.close()
    
    def createGyroidRecipe(self,recipe):
        self.setRecipe(recipe)
        with open(self.recipe,mode='r') as f:
            Lines=f.readlines()
        f = open(self.buildPath+"\\uChannel_job.recipe",mode='w')
        f.truncate(0)
        f.close()
        f = open(self.buildPath+"\\uChannel_job.recipe",mode='a')
        for line in Lines:
            if line[:14]=="Model.FilePath":
                f.write(('Model.FilePath = '+self.STLPath +"\\QGyroid.stl\n"))
            else:
                f.write(line)
        f.close()
    
    def sliceBottomSTL(self):
        Arguments = [self.exePath]
        Arguments.append("-p")
        Arguments.append(self.buildPath+"\\Bottom_job.recipe")
        print(" ".join(Arguments))
        subprocess.call(Arguments)
    
    def sliceGyroidSTL(self):
        Arguments = [self.exePath]
        Arguments.append("-p")
        Arguments.append(self.buildPath+"\\uChannel_job.recipe")
        print(" ".join(Arguments))
        subprocess.call(Arguments)
        
    def moveGyroidOutput(self):
        uChannel_BuildPath = self.buildPath + "\\uChannel_job_output"
        if os.path.isdir(uChannel_BuildPath):
            files = os.listdir(uChannel_BuildPath)
            for file in files:
                src = os.path.join(uChannel_BuildPath,file)
                dst = os.path.join(self.buildPath,file)
                if os.path.isfile(src):
                    shutil.copy(src,dst)
                elif os.path.isdir(src):
                    if os.path.exists(dst) and os.path.isdir(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src,dst)
            shutil.rmtree(uChannel_BuildPath)
            shutil.copy(os.path.join(self.buildPath,'QGyroid_data.gwl')
                      ,os.path.join(self.buildPath,'QGyroid_data.orig'))        
        
    def moveCompartmentOutput(self):
        Bottom_BuildPath = self.buildPath + "\\Bottom_job_output"
        if os.path.isdir(Bottom_BuildPath):
            files = os.listdir(Bottom_BuildPath)
            for file in files:
                src = os.path.join(Bottom_BuildPath,file)
                dst = os.path.join(self.buildPath,file)
                if os.path.isfile(src):
                    shutil.copy(src,dst)
                elif os.path.isdir(src):
                    if os.path.exists(dst) and os.path.isdir(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src,dst)
            shutil.rmtree(Bottom_BuildPath)
            shutil.copy(os.path.join(self.buildPath,'Compartment_data.gwl')
                      ,os.path.join(self.buildPath,'Compartment_data.orig'))
                
        
    def createCombinedJob(self):
        jobFilePath = self.path+"\\_job.gwl"
        BlockNumbers = 16*len(os.listdir(self.buildPath+"\\QGyroid_files90"))+len(os.listdir(self.buildPath+"\\Compartment_files"))
        jobFile = open(jobFilePath,mode='r')
        Lines = jobFile.readlines()
        jobFile.close()
        
        open(self.buildPath+"\\"+self.sampleName+"_job.gwl", mode='w').close()
        
        with open(self.buildPath+"\\"+self.sampleName+"_job.gwl", mode='a') as job:
            for line in Lines:
                words = line.strip().split(" ")
                if line == "%%% Last Line in Parameter Settings\n":
                    job.write(line)
                    job.write("\nvar $BlockNumbers = %s\n" %BlockNumbers)
                    job.write("var $count = 0\n")
                    job.write("var $AddZ = %.3f\n\n" %self.AddZ)
                else:
                    job.write(line)
        
    def modifyCompartmentData(self):
        dataFilePath = self.buildPath+"\\Compartment_data.orig"
        with open(dataFilePath,mode='r') as dataFile:
            Lines = dataFile.readlines()
        
        f = open(self.buildPath+"\\Compartment_data.gwl", mode='w')
        f.truncate(0)
        f.close()
        
        with open(self.buildPath+"\\Compartment_data.gwl", mode='a') as data:
            for line in Lines:
                words = line.strip().split(" ")
                if line == "FindInterfaceAt $interfacePos\n":
                    pass# do nothing
                elif len(words)>1:
                    if words[0] == '%' and words[1] == 'BLOCK':
                        data.write(line)
                        data.write("set $count = $count +1\n")
                        data.write(r'MessageOut "Print Progress = %.1f." #($count/$BlockNumbers*100)'+"\n")
                    else:
                        data.write(line)
                else:
                    data.write(line)
            
    def rotateQGyroidData(self):
        BuildFiles_path = self.buildPath
        QGyroid_files_path = self.buildPath+'\\QGyroid_files\\'
        
        if os.path.isdir(QGyroid_files_path):
            files = os.listdir(QGyroid_files_path)
            os.mkdir(BuildFiles_path+'\\QGyroid_files90\\')
            os.mkdir(BuildFiles_path+'\\QGyroid_files180\\')
            os.mkdir(BuildFiles_path+'\\QGyroid_files270\\')
            for file in files:
                f = open(QGyroid_files_path+file,mode='r')
                lines = f.readlines()
                with open(BuildFiles_path+'\\QGyroid_files90\\'+file, 'w') as f90:
                    with open(BuildFiles_path+'\\QGyroid_files180\\'+file, 'w') as f180:
                        with open(BuildFiles_path+'\\QGyroid_files270\\'+file, 'w') as f270:
                            for line in lines:
                                Dim = line.strip().split("\t")
                                if len(Dim) == 3:
                                    try:
                                        x = float(Dim[0])
                                        y = float(Dim[1])
                                        z = float(Dim[2])
                                        f90.write(' '.join([str(-x),str(y),str(z)])+'\n')
                                        f180.write(' '.join([str(-x),str(-y),str(z)])+'\n')
                                        f270.write(' '.join([str(x),str(-y),str(z)])+'\n')
                                    except:
                                        f90.write(line)
                                        f180.write(line)
                                        f270.write(line)
                                        print("Exception:" + line)
                                elif Dim[0].split(' ')[0] == 'AddXOffset':
                                    offsetX = float(Dim[0].split(' ')[1])
                                    
                                    f90.write('AddXOffset '+str(-offsetX)+'\n')
                                    f180.write('AddXOffset '+str(-offsetX)+'\n')
                                    f270.write('AddXOffset '+str(offsetX)+'\n')
                                elif Dim[0].split(' ')[0] == 'AddYOffset':
                                    offsetY = float(Dim[0].split(' ')[1])
                                    
                                    f90.write('AddYOffset '+str(offsetY)+'\n')
                                    f180.write('AddYOffset '+str(-offsetY)+'\n')
                                    f270.write('AddYOffset '+str(-offsetY)+'\n')
                                elif Dim[0].split(' ')[0] == '%' and Dim[0].split(' ')[1] == 'Slice':
                                    self.AddZ = float(Dim[-1].split(' ')[-1])
                                    #print(AddZ)
                                    f90.write(line)
                                    f180.write(line)
                                    f270.write(line)
                                else:
                                    f90.write(line)
                                    f180.write(line)
                                    f270.write(line)
                                    
    def modifyGyroidData(self):
        dataFilePath = self.buildPath+"\\QGyroid_data.orig"
        with open(dataFilePath,mode='r') as dataFile:
            Lines = dataFile.readlines()
        
        t = open(self.buildPath+"\\QGyroid_data.gwl", mode='w')
        t.truncate(0)
        t.close()
        
        t=open(self.buildPath+"\\QGyroid_data90.gwl", mode='w')
        t.truncate(0)
        t.close()
        
        t=open(self.buildPath+"\\QGyroid_data180.gwl", mode='w')
        t.truncate(0)
        t.close()
        
        t=open(self.buildPath+"\\QGyroid_data270.gwl", mode='w')
        t.truncate(0)
        t.close()
        
        with open(self.buildPath+"\\QGyroid_data.gwl", mode='a') as f:
            with open(self.buildPath+"\\QGyroid_data90.gwl", mode='a') as f90:
                with open(self.buildPath+"\\QGyroid_data180.gwl", mode='a') as f180:
                    with open(self.buildPath+"\\QGyroid_data270.gwl", mode='a') as f270:
                        for line in Lines:
                            words = line.strip().split(" ")
                            if line == "FindInterfaceAt $interfacePos\n":
                                pass# do nothing           
                            elif len(words)>1:
                                if words[0] == '%' and words[1] == 'BLOCK':
                                    M = int(words[-1][-3])
                                    L = int(words[-1][-5])
                                    
                                    f.write('StageGotoX %.3f\n' %(L*500+250))
                                    f90.write('StageGotoX %.3f\n' %-(L*500+250))
                                    f180.write('StageGotoX %.3f\n' %-(L*500+250))
                                    f270.write('StageGotoX %.3f\n' %(L*500+250))
                                    
                                    f.write('StageGotoY %.3f\n' %(M*500+250))
                                    f90.write('StageGotoY %.3f\n' %(M*500+250))
                                    f180.write('StageGotoY %.3f\n' %-(M*500+250))
                                    f270.write('StageGotoY %.3f\n' %-(M*500+250))
                                    
                                    f.write(line)
                                    f.write("set $count = $count +1\n")
                                    f.write(r'MessageOut "Print Progress = %.1f." #($count/$BlockNumbers*100)'+"\n")
                                    
                                    f90.write(line)
                                    f90.write("set $count = $count +1\n")
                                    f90.write(r'MessageOut "Print Progress = %.1f." #($count/$BlockNumbers*100)'+"\n")
                                    
                                    f180.write(line)
                                    f180.write("set $count = $count +1\n")
                                    f180.write(r'MessageOut "Print Progress = %.1f." #($count/$BlockNumbers*100)'+"\n")
                                    
                                    f270.write(line)
                                    f270.write("set $count = $count +1\n")
                                    f270.write(r'MessageOut "Print Progress = %.1f." #($count/$BlockNumbers*100)'+"\n")
                                elif words[0] == 'include' and words[1][-4:] =='.gwl':
                                    f.write(line)
                                    f90.write('include QGyroid_files90'+words[1][-18:])
                                    f180.write('include QGyroid_files180'+words[1][-18:])
                                    f270.write('include QGyroid_files270'+words[1][-18:])
                                elif words[0] == 'MoveStageX':
                                    pass
                                elif words[0] == 'MoveStageY':
                                    pass
                                elif words[0] == 'AddZDrivePosition':
                                    f.write(line)
                                    f90.write(line)
                                    f180.write(line)
                                    f270.write(line)
                                else:
                                    f.write(line)
                                    f90.write(line)
                                    f180.write(line)
                                    f270.write(line)
                            else:
                                f.write(line)
                                f90.write(line)
                                f180.write(line)
                                f270.write(line)
        
        
        


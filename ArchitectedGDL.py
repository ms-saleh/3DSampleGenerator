# -*- coding: utf-8 -*-
"""
Created on Fr Mar 12 13:36:25 2021

@author: Sadeq Saleh @ Cornell.edu

Get the design of experiment for micro channe arrays, build the geometery in 
"nTopology Platform" and create buildfiles in Nanoscribe
"""
from env_var import *
from Class_buildSample import *

def runConventionalWorkflow():
    with open('DOE.csv',mode='r') as DOE:
        Lines = DOE.readlines()
    for line in Lines:
        sample.exePath = r"C:/Program Files/nTopology/nTopology/ntopCL.exe"
        words = line.strip().split(',')
        
        sample.setSampleName(words[0])
        sample.setOutputPath(sample.path+"\\"+sample.sampleName)
        sample.setSTLPath(sample.outputPath+"\\STL")
        sample.setBuildPath(sample.outputPath+"\\BuildFiles")
        sample.setDOE(words[3:7])
        sample.createTree()
                
        sample.setCustomBlock(words[1])
        sample.summary()
        sample.nTopTemplate()
        sample.createGyroidInputJSON()
        sample.createGyroidSTL()
    
        sample.setCustomBlock(words[2])
        sample.summary()
        sample.nTopTemplate()
        sample.createMeshMergeInputJSON()
        sample.createMeshMergeSTL()
    
        sample.exePath = r"C:/Program Files/Nanoscribe/DeScribe/DeScribe.exe"
        sample.createBottomRecipe("Bottom_job.recipe")
        sample.createGyroidRecipe("uChannel_job.recipe")
        print('time to switch to Binary')
        sample.sliceBottomSTL()
        print('time to switch to ASCII')
        sample.sliceGyroidSTL()
    
        sample.blockNumbers = 0
        sample.moveCompartmentOutput()
        sample.moveGyroidOutput()
        
    
        sample.rotateQGyroidData()
        sample.modifyCompartmentData()
        sample.modifyGyroidData()
        sample.createCombinedJob()

 

if __name__ == "__main__":
    path=os.getcwd()
    setCredentials(path,'credentials.txt')
    sample = buildSample(path)
    runConventionalWorkflow()
    
     



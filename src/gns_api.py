import os
from re import findall
from shutil import copy2

def generateFileRoutingTable(projectName):
    
    routeurs = []
    path = []
    project = './'+projectName+'/project-files/dynamips/'
    
    files = [ name for name in os.listdir(project) if os.path.isdir(os.path.join(project, name)) ]
    
    for dir in files:
        
        file = os.listdir(project+dir+"/configs/")
        for name in file:
            
            if len(name.split("tartup-con")) > 1:
                f = open(project + dir + "/configs/" + name, 'r')
                for line in f.readlines():
                    f = findall("hostname [a-zA-Z0-9_\-\.]*", line)
                    if len(f) > 0:
                        routeurId = f[0][9:]
                        
                        routeurs.append(routeurId)
                        path.append(project + dir + "/configs/" + name)
                        break
                    
    f = open("fileRoutingTable.csv", 'w')
    
    for i in range(len(routeurs)):
        
        string = routeurs[i] + " " + path[i] + "\n"
        f.write(string)
        
    f.close()

def pushConfigToProject():
    
    routeurs = []
    paths = []
    
    routing = open("fileRoutingTable.csv", 'r')
    for line in  routing.readlines():
        temp = line.split(" ")
        routeurs.append(temp[0])
        paths.append(temp[1])
        
    
    path = "./verdict"
    for file in os.listdir(path):
        
        name = file[:len(file) - 4]
        ind = routeurs.index(name) 
        dest =  paths[ind]
        dest = dest.strip("\n")
        
        copy2(path+'/'+file,dest)
        
from json import *

class Parseur:
    
    counter = 0
    
    def __init__(self, file):
        
        f = open(file, 'r')
        self.data = load(f)["routers"]
        f.close()
    
    def getRouter(self):
        
        ret = self.data[Parseur.counter]
        Parseur.counter += 1
        
        if Parseur.counter >= len(self.data):
            Parseur.counter = 0
            
    def getRouterInd(self, ind):
        return self.data[ind]
    
    def getRouterNumberOfConnection(self, name):
        for router in self.data:
            if router["name"] == name:
                return len(router["links"])
    
    def getNumberOfRouter(self):
        return len(self.data)
    
    def getLinksList(self):
        links = []
        
        for elm in self.data:
            temp = elm["links"]
            
            for link in temp:
                if link[0] not in links:
                    links.append(link[0])
                    
        return links
    
    def getAssociatedRouters(self, idLink):
        
        ret = []
        for router in self.data:
            
            has = False
            interface = ""
            for link in router["links"]:
                if link[0] == idLink:
                    has = True
                    interface = link[1]
                    break
                
            if has == True:
                ret.append((router["name"], interface))
                
        return ret
    
    def getCELinks(self, name):
        
        liste = []
        print("Looking for CE on " + name)

        for router in self.data:
            
            if router["name"] == name:
                
                print(name + " dound")
                for link in router["links"]:
                    temp = self.findLinkedInterface(router["name"], link[0])
                    print("vis a vis avec" + str(temp))
                    ind = -1
                    for i in range(len(self.data)):
                        if self.data[i]["name"] == temp[0]:
                            ind = i
                            break
                    
                    print(str(temp) + " correspond au routeur " + self.data[i]["name"] + " qui est un " + self.data[i]["classe"])
                    if self.data[i]["classe"] == "CE":
                        liste.append(link)
                break
            
        return liste
            
    
    def findLinkedInterface(self, name, idLink):
        
        interfacePair = []
        for i in range(len(self.data)):
            for link in self.data[i]["links"]:
                if idLink == link[0]:
                    interfacePair.append((self.data[i]["name"], link[1]))
                    break
        
        if interfacePair[0][0] == name:
            return interfacePair[1]
        else:
            return interfacePair[0]
from src.parseur import *
from jinja2 import *
from itertools import chain

class Router:
    
    def __init__(self):
        
        self.name = ""
        self.classe = ""
        self.links = []
        self.vpns = []
        self.vrfs = []
        self.IP = []
        self.interface = []
        self.neighbors = []
        self.iBGPNeighbors = []
        self.loopback = ""
        self.as_number = -1
        
    def setName(self, name):
        self.name = name

    def setClasse(self, classe):
        self.classe = classe
    
    def setLinks(self, links):
        self.links = links
        
    def setNeighborsAS(self, ASs):
        self.neighborsAS = ASs
    
    def setVPNs(self, vpns):
        self.vpns = vpns
    
    def setVRFs(self, vrf):
        self.vrfs = vrf
    
    def setIPAdress(self, IP, interface):
        self.IP.append(IP)
        self.interface.append(interface)
        
    def setLoopback(self, IP):
        self.loopback = IP
        
    def setAS(self, val):
        self.as_number = val
        
    def setIBGP(self, addresses):
        self.iBGPNeighbors = addresses
        
    def toString(self):
        string = "Router " + self.name + " is a " + self.classe + " router. It has " + str(self.links) + " links\n"
        
        if self.classe == "PE":
            string += "It connects " + str(self.vpns) + "\n"
            
        if len(self.IP) > 0:
            string += "IP found on :\n"
            for i in range(len(self.IP)):
                string += self.interface[i] + " : " + self.IP[i] + "\n"
                
        if self.loopback != "":
            string += "Loopback adress is : " + self.loopback + "\n"
                
        return string
    
    def setNeighbors(self, neighbors):
        self.neighbors = neighbors
    
    def genConfigFile(self, path):
        
        env = Environment(loader = FileSystemLoader("src/templates/"))
        
        match self.classe:
            case "P":
                
                templateGeneral = env.get_template("router_p.txt")
                templateLoopback = env.get_template("interface_loopback.txt")
                templateInterface = env.get_template("interface_default.txt")
                templateOSPF = env.get_template("ospf.txt")
                
                interfaces = ""
                interfaces += templateLoopback.render(address = self.loopback, ospf = 42, ospfNumber = 1)
                interfaces += "\n"
                for i in range(len(self.IP)):
                    interfaces += templateInterface.render(name = self.interface[i], vrf = "", 
                                                           IP = self.IP[i], ospf = 42, ospfNumber = 1)
                    
                    if i != len(self.IP) - 1:
                        interfaces += "\n"
                    
                ospfString = templateOSPF.render(ospf = 42, loopback = self.loopback)
                
                conf = templateGeneral.render(name = self.name, interface = interfaces, ospf = ospfString)
                
                f = open(path + self.name+".cfg", 'w')
                f.write(conf)
                f.close()
                
            case "CE":
                
                templateGeneral = env.get_template("router_ce.txt")
                templateLoopback = env.get_template("interface_loopback.txt")
                templateInterface = env.get_template("interface_default.txt")
                templateBGP = env.get_template("bgp_ce.txt")
                templateNeighbor = env.get_template("bgp_neighbors.txt")
                
                interfaces = ""
                interfaces += templateLoopback.render(address = self.loopback, ospf = 42, ospfNumber = 1)
                interfaces += "\n"
                for i in range(len(self.IP)):
                    interfaces += templateInterface.render(name = self.interface[i], vrf = "", 
                                                           IP = self.IP[i], ospf = 42, ospfNumber = 1)
                    
                    if i != len(self.IP) - 1:
                        interfaces += "\n"
                        
                neighborsString = ""
                for i in range(len(self.neighbors)):
                    neighborsString += templateNeighbor.render(IP = self.neighbors[i][0], mainAS = self.neighbors[i][1])
                    if i != len(self.neighbors) - 1:
                        neighborsString += "\n "
                        
                bgpString = templateBGP.render(asNumber = self.as_number, neighbors = neighborsString)
                
                conf = templateGeneral.render(name = self.name, interface = interfaces, bgp = bgpString)
                f = open(path + self.name+".cfg", 'w')
                f.write(conf)
                f.close()
                
            case "PE":
                
                templateGeneral = env.get_template("router_pe.txt")
                templateLoopback = env.get_template("interface_loopback.txt")
                templateInterface = env.get_template("interface_default.txt")
                templateInterfaceVRF = env.get_template("interface_noospf.txt")
                templateAdresseFamily = env.get_template("adresseFamily.txt")
                templateVRF = env.get_template("vrf.txt")
                templateOSPF = env.get_template("ospf.txt")
                
                vrfString = ""
                for i in range(len(self.vrfs[0])):
                    rts_both = ''
                    for j in range(len(self.vrfs[1][i])):
                        rts_both += "route-target both "+str(self.vrfs[1][i][j])+":"+str(self.vrfs[1][i][j])
                        if j < len(self.vrfs[1][i])-1:
                            rts_both += "\n "
                    
                
                    number = self.vrfs[0][i][1]
                    vrfString += templateVRF.render(name = "VRF"+number,
                        RD = number + ":" + number, RTs = rts_both) + "\n"
                
                interfaces = ""
                interfaces += templateLoopback.render(address = self.loopback, ospf = 42, ospfNumber = 1)
                interfaces += "\n"
                for i in range(len(self.IP)):
                    if self.interface[i] not in self.vrfs[0]:
                        interfaces += templateInterface.render(name = self.interface[i], vrf = "", 
                                                            IP = self.IP[i], ospf = 42, ospfNumber = 1)
                    else:
                        interfaces += templateInterfaceVRF.render(name = self.interface[i],
                        vrf = "vrf forwarding VRF"+self.interface[i][1], IP = self.IP[i])
                    
                    if i != len(self.IP) - 1:
                        interfaces += "\n"
                        
                ospfString = templateOSPF.render(ospf = 42, loopback = self.loopback)
                
                iBGPString = "router bgp 1\n"
                half1 = ""
                half2 = ""
                for i in range(len(self.iBGPNeighbors)):
                    
                    if self.iBGPNeighbors[i] != self.loopback:
                        half1 += " neighbor " + self.iBGPNeighbors[i] + " remote-as 1\n"
                        half1 += " neighbor " + self.iBGPNeighbors[i] + " update-source Loopback0\n"
                        half2 += "  neighbor " + self.iBGPNeighbors[i] + " activate\n"
                        
                iBGPString += half1 + " no auto-summary\n !\n address-family vpnv4\n" + half2 + "!\n"
                
                adressFamilyString = ""
                for i in range(len(self.vrfs[0])):
                    IPFront = ""
                    temp = self.vrfs[0][i]
                    temp = self.IP[self.interface.index(temp)]
                    
                    temp1 = temp.split(".")
                    if temp1[3] == "1":
                        IPFront = temp1[0]+"."+temp1[1]+"."+temp1[2]+".2"
                    else:
                        IPFront = temp1[0]+"."+temp1[1]+"."+temp1[2]+".1"
                    
                    neigh = "neighbor " + IPFront + " remote-as " + str(self.neighborsAS[i])+ "\n"
                    neigh += " neighbor " + IPFront + " activate"
                    
                    adressFamilyString += templateAdresseFamily.render(name = "VRF"+self.vrfs[0][i][1], neighbors = neigh)
                    if i != len(self.vrfs[0]) - 1:
                        adressFamilyString += "\n"
                
                conf = templateGeneral.render(VRFs = vrfString, name = self.name, interface = interfaces,
                                              iBGP = iBGPString, ospf = ospfString, adressFamily = adressFamilyString)
                
                f = open(path + self.name+".cfg", 'w')
                f.write(conf)
                f.close()
                

                
    
class Network:
    
    def __init__(self, parseur : Parseur):
        
        self.PE = []
        self.CE = []
        self.P = []
        
        self.hasGeneratedIP = False
        
        self.parseur = parseur
        
        numberOfRouter = parseur.getNumberOfRouter()
        
        for i in range(numberOfRouter):
            
            temp = parseur.getRouterInd(i)
            
            newRouter = Router()
            newRouter.setName(temp["name"])
            newRouter.setClasse(temp["classe"])
            
            if "links" not in temp:
                print("WARNING - There is a non-connected router named :" + temp["names"])
            else:
                newRouter.setLinks(temp["links"])
                
            if "VPN" in temp:
                newRouter.setVPNs(temp["VPN"])
            
            if len(temp["links"]) > 3:
                print("ERROR - Cannot create a router with more than 3 links")
                exit(-1)
                
            if "AS_BGP" in temp:
                newRouter.setAS(temp["AS_BGP"])
            
            match temp["classe"]:
                case "PE":
                    self.PE.append(newRouter)
                case "CE":
                    self.CE.append(newRouter)
                case "P":
                    self.P.append(newRouter)
                case _:
                    print("ERROR - Router "+temp["name"]+" class is not recognized, please check it")
    
            
    def generateIPAdresses(self):
        
        for link in self.parseur.getLinksList():
            
            involved = self.parseur.getAssociatedRouters(link)
            
            if len(involved) != 2:
                print("ERROR - There are not 2 routers on link " + str(link))
                exit(-1)
            
            counter = 1
            
            for router in self.PE:
                
                if router.name == involved[0][0] or router.name == involved[1][0]:
                    if involved[0][0] == router.name:
                        router.setIPAdress("192.168."+str(link)+"."+str(counter), involved[0][1])
                    else:
                        router.setIPAdress("192.168."+str(link)+"."+str(counter), involved[1][1])
                    
                    counter += 1
                
                if counter == 3:
                    break
                
            for router in self.CE:
                if router.name == involved[0][0] or router.name == involved[1][0]:
                    if involved[0][0] == router.name:
                        router.setIPAdress("192.168."+str(link)+"."+str(counter), involved[0][1])
                    else:
                        router.setIPAdress("192.168."+str(link)+"."+str(counter), involved[1][1])
                    counter += 1
                
                if counter == 3:
                    break
                
            for router in self.P:
                if router.name == involved[0][0] or router.name == involved[1][0]:
                    if involved[0][0] == router.name:
                        router.setIPAdress("192.168."+str(link)+"."+str(counter), involved[0][1])
                    else:
                        router.setIPAdress("192.168."+str(link)+"."+str(counter), involved[1][1])
                    counter += 1
                
                if counter == 3:
                    break
                
        for router in self.PE:
            router.setLoopback("192.168.255." + str(router.name[1:]))
        for router in self.CE:
            router.setLoopback("192.168.255." + str(router.name[1:]))
        for router in self.P:
            router.setLoopback("192.168.255." + str(router.name[1:]))
            
    def giveNeighborsToRouters(self):
        
        for router in self.CE:
            neighborList = []
            for i in range(len(router.links)):
                visavis = self.parseur.findLinkedInterface(router.name, router.links[i][0])
                for routerBis in chain(self.CE, self.PE, self.P):
                    if routerBis.name == visavis[0]:
                        toAdd = (routerBis.IP[routerBis.interface.index(visavis[1])],1)
                        neighborList.append(toAdd)
                
                
            router.setNeighbors(neighborList)
        
        loopbacks = []    
        for router in self.PE:
            loopbacks.append(router.loopback)
            
        for router in self.PE:
            router.setIBGP(loopbacks)
            
    def setupVrfOfPe(self):
        
        for router in self.PE:
            
            usedInterface = []
            RTs = []
            ASs = []
            
            for vpn in router.vpns:
                if vpn[1] not in usedInterface:
                    usedInterface.append(vpn[1])
                    RTs.append([])
                    
                    idLink = vpn[1]
                    for i in range(len(router.links)):
                        if router.links[i][1] == idLink: 
                            idLink = router.links[i][0]
                            break
                    
                    eBGP = self.parseur.findLinkedInterface(router.name, idLink)
                    eBGP = eBGP[0]
                
                    
                    AS = -1
                    for router1 in self.CE:
                        if router1.name == eBGP: 
                            
                            AS = router1.as_number
                            break
                    
                    ASs.append(AS)
                    
            for vpn in router.vpns:
                RTs[usedInterface.index(vpn[1])].append(vpn[0])
                
                
                
            
            router.setNeighborsAS(ASs)
            router.setVRFs((usedInterface, RTs))
            
    def genAllConfigFiles(self, path):
        
        for router in chain(self.CE, self.PE, self.P):
            router.genConfigFile(path)
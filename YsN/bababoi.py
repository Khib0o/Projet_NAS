#!/usr/bin/python3
import os, json, glob, platform, re



router_path={}
hosts=[]

f=open('testfeild.gns3')
raw=json.load(f)
# raw=f.read()
# print(raw.keys())
for node in raw['topology']['nodes']:
    path=r'project-files/dynamips/'+node['node_id']+r'/configs/'
    conf_file=glob.glob(path+'/*startup*',recursive=True)[0]
    if platform.uname().system=='Windows':
        conf_file=conf_file.split('\\')
    else:
        conf_file=conf_file.split('/')
    conf_file=conf_file[-1]
    # print(conf_file)
    hosts.append(node['name'])
    router_path[node['name']]= path+conf_file
f.close()
# print(router_path)

# print(mask(28))



class Router:
    def __init__(self, name, path="", hostname=''):
        self.name       = name
        self.path       = path
        if self.name in router_path.keys():
            self.path   = router_path[self.name]
        self.conf_file  = open(self.path,'r')
        self.run_conf   = self.conf_file.read()
        self.hostname   = hostname


    def get_ints(self):
        # print(self.run_conf.find("interface"))
        l=[m.group(0) for m in re.finditer('(?<=interface )\w+',self.run_conf)]
        k=[m.group(0) for m in re.finditer('(?<=interface )*/\w+',self.run_conf)]
        return [l[i]+k[i] for i in range(len(k))]



# P1=Router("R4")
# print(P1.get_ints(),'\n',P1.path)
l={ "R1":{
        "interface":{
            "name":"f0/0",
            "IP":'10.10.10.10'
        },
        "interface":{
            "name":"f2/0",
            "IP":'10.10.10.10'
        }
        }
    }


s="\n".join([f'interface f{i}\nLolipop' for i in l["R1"]])
print(s)

# s=open(router_path["R1"],"r").read()
# s,end=s[:-6],s[-6:]
# print(s,'\n##################\n',end)

"""
Title: OrangeApi
Desc: A python module to gather and manage the devices connected to your router.
Author: FuriousBird
Version: 1.1.5
"""

from types import MethodDescriptorType
import requests, json

class OrangeClient:
    addr = "192.168.1.1"
    user = "admin"
    psw = False
    contextId = False
    emulate_network = False
    emulate_src = "./emulate.json"
    def handle_dict(self, d) -> None:
        for k in d.keys():
            v = d[k]
            if k == "addr":
                self.addr = v
            if k == "user":
                self.user = v
            if k == "psw":
                self.psw = v
            if k == "emul":
                self.emulate_network = v
            if k=="emul_src":
                self.emulate_src = v
    def __init__(self, d={}, **kwargs) -> None:
        if d:
            self.handle_dict(d)
        if kwargs:
            self.handle_dict(kwargs)
        self.session = False
    def post(self, service, method, params={}, headers={}, retries=3, additional={}) -> dict:
        #default headers for login and after login
        if not self.contextId:
            postheaders = {"Content-Type":"application/x-sah-ws-4-call+json; charset=UTF-8", "Authorization": "X-Sah-Login"}
        else:
            postheaders = {"Content-Type":"application/x-sah-ws-4-call+json; charset=UTF-8", "Authorization":"X-Sah "+self.contextId}
        
        #overwrite if precised
        for k in headers.keys():
            postheaders[k] = headers[k]
        
        d = {
            "service":service,
            "method":method,
            "parameters":params
        }

        for k in additional.keys():
            if k not in ["service", "method", "parameters"]:
                d[k] = additional[k]

        try:
            r = self.session.post('http://192.168.1.1/ws', data=json.dumps(d), headers=postheaders)
        except requests.exceptions.RequestException:
            if not retries is False:
                if retries != 0:
                    print("Error: Retrying Post")
                    return self.post(service=service, method=method, params=params, retries=retries-1)
            return {}
        
        return r.json()

    def start(self, psw_in=False) -> str:
        if psw_in:
            psw_send = psw_in
        else:
            if self.psw:
                psw_send = self.psw
            else:
                return ""
        self.session = requests.Session()
        rdat = self.post(service="sah.Device.Information", method="createContext", params={
              "applicationName":"webui",
              "username":self.user,
              "password":psw_send
        }, headers={"Content-Type":"application/x-sah-ws-4-call+json; charset=UTF-8", "Authorization": "X-Sah-Login"})

        if rdat:
            contextId = rdat.get("data", {}).get("contextID", False)
            self.contextId = contextId
            return contextId
        else:
            return ""
    def get_devices(self) -> list:
        output = self.post(service="TopologyDiagnostics", method="buildTopology", params={"SendXmlFile":False})
        devices = []
        if output:
            if self.emulate_network:
                with open(self.emulate_src, "r") as file:
                    output = json.loads(file.read())
            
            toporoot = output.get("status", [])
            if len(toporoot)>0:
                toporoot = toporoot[0]

            child_types = toporoot.get("Children", {})
            lan = list(filter(lambda x: x.get("Key", False) == "lan", child_types))[0]

            methods = lan.get("Children", [])
            for meth in methods:
                #print(json.dumps(meth,indent=4))
                meth_children = meth.get("Children", [])
                #i am spiraling into insanity
                for child_of_meth in meth_children:
                    devices.append(child_of_meth)
        return devices
    def get_connected_devices(self) -> list:
        d = self.get_devices()
        d = list(filter(lambda x:x.get("Active", False), d))
        return d
    def overrideschedule(self, devicemac, override=True):
        if type(override)==bool:
            override = "Disable"*int(not(override))+"Enable"*int(override)
        else:
            assert type(override)==str, "overrideschedule: Schedule must be str or bool"
            assert (override=="Enable" or override=="Disable"), "If schedule is str, must be 'Enable' or 'Disable'."
        assert (override=="Enable" or override=="Disable")
        p = {   
                "info": {
                    "base": "Weekly",    
                    "def": "Enable",
                    "enable": True,
                    "ID": devicemac,
                    "override": override,
                    "schedule": []
                    },  
                "type": "ToD"  
            }
        r = self.post(method="addSchedule", params=p, service="Scheduler" )
        return r
    def close(self) -> None:
        self.session.close()
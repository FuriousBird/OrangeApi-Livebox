from src.orangeapi import OrangeClient
import json

import dotenv
dotenv.load_dotenv()
import os
password = os.getenv("password")

if __name__=="__main__":
    c = OrangeClient({
        "user":"admin",
        "psw":password,
        "emul":False,
        "emul_src":"emulate.json"
    })
    c.start()
    d = c.get_connected_devices()
    with open("j.json", 'w') as file:
        file.write(json.dumps(d))
    for i in d:
        devId=i.get("Key", False)
        if devId:
            r = c.overrideschedule(devId, override=True)
            if r:
                status = r.get("status", False)
                col_code = "38;5;85"*int(status)+"38;5;167"*int(not(status))
            else:
                col_code = "38;5;167"
        else:
            col_code = "38;5;167"
            
        print("\033[{}m".format(col_code)+i.get("Name", "--- Unnamed Device ---")+"\033[0m", end="    ")
        if devId:
            print("\033[93m"+devId+"\033[0m")
        else:
            print("\033[93m"+"--- ID not found ---"+"\033[0m")
        
    r = c.overrideschedule("8E:BD:88:5A:84:F2", override=True)
    print(r)
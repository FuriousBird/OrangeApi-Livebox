from orangeapi import OrangeClient

c = OrangeClient({
        "user":"admin",
        "psw":"motdepasse"
    })
c.start()
d = c.get_connected_devices()
if d:
    for i in d:
        print(i.get("Name", "--- Unamed ---"))
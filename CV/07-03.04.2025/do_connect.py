import network as net


def do_connect():
    sta_if = net.WLAN(net.WLAN.IF_STA)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect("13373-IoT-Lab", "FetMc5Un>2dYzEM")
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ipconfig("addr4"))

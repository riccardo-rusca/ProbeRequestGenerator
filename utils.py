import random

oui = {}

def get_oui(vendor_name: str) -> [str, str]:
    if len(oui) == 0:
        with open('utility/oui_hex.txt', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                mac = line.strip().split("\t")[0]
                vendor = line.strip().split("\t")[1]
                if oui.get(vendor):
                    oui[vendor].append(mac)
                else:
                    oui[vendor] = []
                    oui[vendor].append(mac)

    res = ""
    res_name = ""
    for key in oui:
        if key.lower().startswith(vendor_name.lower()):
            res = oui[key][0]  # take the first one
            res_name = key

    return [res.replace("-", ":"), res_name]


def get_frequency(channel: int) -> int:
    if channel == 14:
        freq = 2484
    else:
        freq = 2407 + (channel * 5)

    return freq


def produce_sequenceNumber(frag: int, seq: int) -> int:
    return (seq << 4) + frag


def random_MAC() -> str:
    # output format: 62:AA:BB:C1:45:12
    first_byte = int('%d%d%d%d%d%d10' % (random.randint(0, 1), random.randint(0, 1), random.randint(0, 1), random.randint(0, 1), random.randint(0, 1), random.randint(0, 1)), 2)
    mac_address = ("%02x:%02x:%02x:%02x:%02x:%02x" % (
        first_byte, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))).lower()
    return mac_address

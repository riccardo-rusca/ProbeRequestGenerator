from datetime import datetime
from scapy.layers.dot11 import Dot11, RadioTap, Dot11ProbeReq, Dot11Elt, Dot11EltRates, Dot11EltDSSSet, \
    Dot11EltVendorSpecific
from utils import *
from numpy import random

def create_probe(vendor: str,
                 randomization: int,
                 ssid: list,
                 burst_length: int,
                 mac_address: str,
                 inter_pkt_time: float,
                 VHT_capabilities: bytes,
                 extended_capabilities: bytes,
                 HT_capabilities: bytes,
                 wps: bytes,
                 uuide: bytes,
                 time: datetime) -> tuple[str, list]:
    """Create a probe request packet, putting together all the layers, and save it in a pcap file"""

    packets = list()

    num_pkt_sent = 0
    radio = create_radio()
    dot11, seq_number, mac_address = create_80211(vendor, randomization, seq_number=0, mac_address=mac_address, burst_lenght=burst_length)

    # handle of packets burst
    dot11Array = []
    for i in range(1, int(burst_length)):
        dot11burst, seq_number, mac_address = create_80211(vendor, randomization, seq_number=seq_number+1, mac_address=mac_address, burst_lenght=burst_length)
        dot11Array.append(dot11burst)

    probeReq = Dot11ProbeReq()
    if len(ssid) != 0:
        dot11elt = create_informationElement(ssid=random.choice(ssid))
    else:
        dot11elt = create_informationElement(ssid="")
    dot11eltrates = create_supportedRates([2, 4, 11, 22])
    dot11eltratesext = create_extendedSupportedRates([12, 18, 22, 36, 48, 72, 96, 108])
    dot11eltdssset = create_DSSSparameterSet(1)
    dot11elthtcap = create_HTcapabilities(HT_capabilities)
    dot11eltven = create_vendorSpecific(vendor)
    if wps and uuide:
        dot11wps, dot11uuide = create_wps_uuide(wps, uuide)

    if VHT_capabilities is not None:
        dot11eltVHTcap = create_VHTcapabilities(VHT_capabilities)

    dot11eltEXTcap = create_Extendendcapabilities(extended_capabilities)

    if VHT_capabilities is not None:
        if wps and uuide:
            frame = radio / dot11 / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltVHTcap / dot11eltEXTcap / dot11eltven / dot11wps / dot11uuide
        else:
            frame = radio / dot11 / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltVHTcap / dot11eltEXTcap / dot11eltven
    else:
        if wps and uuide:
            frame = radio / dot11 / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltEXTcap / dot11eltven / dot11wps / dot11uuide
        else:
            frame = radio / dot11 / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltEXTcap / dot11eltven

    packets.append(frame)

    t_ref = time.timestamp()
    frame.time = t_ref
    num_pkt_sent += 1

    # handle of packets burst
    for i in range(1, int(burst_length)):
        if VHT_capabilities is not None:
            if wps and uuide:
                frame = radio / dot11Array.pop(0) / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltVHTcap / dot11eltEXTcap / dot11eltven / dot11wps / dot11uuide
            else:
                frame = radio / dot11Array.pop(0) / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltVHTcap / dot11eltEXTcap / dot11eltven
        else:
            if wps and uuide:
                frame = radio / dot11Array.pop(0) / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltEXTcap / dot11eltven / dot11wps / dot11uuide
            else:
                frame = radio / dot11Array.pop(0) / probeReq / dot11elt / dot11eltrates / dot11eltratesext / dot11eltdssset / dot11elthtcap / dot11eltEXTcap / dot11eltven

        t_ref = t_ref + inter_pkt_time
        frame.time = t_ref
        packets.append(frame)

    return mac_address, packets


def create_radio():
    return RadioTap(present='TSFT+Flags+Rate+Channel+dBm_AntSignal+Antenna', Flags='', Rate=1.0,
                    ChannelFrequency=get_frequency(channel=1), ChannelFlags='CCK+2GHz', dBm_AntSignal=-random.randint(30, 70), Antenna=0)


def create_80211(vendor, randomization, seq_number, mac_address, burst_lenght):
    if mac_address == "":
        # create a randomized mac address by default
        mac_address = (random_MAC()).lower()
        if randomization == 0:
            # search if the MAC address vendor exist in the vendor list and take the OUI
            MAC_vend = (get_oui(vendor)[0]).lower()
            if MAC_vend != 0:
                mac_address = MAC_vend + (":%02x:%02x:%02x" % (
                    random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))).lower()

    if seq_number == 0:
        seq_number = random.randint(0, 4096 - burst_lenght)

    return [Dot11(addr1='ff:ff:ff:ff:ff:ff', addr2=mac_address, addr3='ff:ff:ff:ff:ff:ff', SC=produce_sequenceNumber(0, seq_number)), seq_number, mac_address]


def create_informationElement(ssid):
    if ssid != "":
        return Dot11Elt(ID=0, info=ssid)
    else:
        return Dot11Elt(ID=0)


def create_supportedRates(rates):
    return Dot11EltRates(ID=1, rates=rates)


def create_extendedSupportedRates(rates):
    return Dot11EltRates(ID=50, rates=rates)


def create_DSSSparameterSet(channel):
    return Dot11EltDSSSet(channel=channel)


def create_HTcapabilities(HT_info):
    return Dot11Elt(ID=45, info=HT_info)


def create_vendorSpecific(vendor):
    mac, name = get_oui(vendor)
    return Dot11EltVendorSpecific(ID=221, oui=int(mac.replace(":", ""), 16), info='\x00\x00\x00\x00')


def create_VHTcapabilities(VHT_capabilities: bytes):
    return Dot11Elt(ID=191, info=VHT_capabilities)


def create_Extendendcapabilities(extended_capabilities: bytes):
    return Dot11Elt(ID=127, info=extended_capabilities)


def create_wps_uuide(wps: bytes, uuide: bytes):
    return Dot11EltVendorSpecific(ID=221, info=wps), Dot11EltVendorSpecific(ID=221, info=uuide)

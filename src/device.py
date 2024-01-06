from packet import *
from utility.utils import *
import numpy as np

HEXADECIMAL = [
    "a", "b", "c", "d", "e", "f",
    "1", "2", "3", "4", "5", "6", "7", "8", "9"
]

def random_hex(number_of_elements: int):
    """Create a random hex string of length number_of_elements"""
    hex_chars = np.array(HEXADECIMAL)
    info = "".join(np.random.choice(hex_chars, size=number_of_elements))
    return info


def create_ssid():
    """Create a random set of SSIDs"""
    num_ssids = np.random.randint(1, 11)  # Random number of SSIDs between 1 and 10
    ssid_chars = np.array(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
    ssids = set()

    for _ in range(num_ssids):
        ssid = "".join(np.random.choice(ssid_chars, size=32))
        ssids.add(ssid)

    return list(ssids)


class Device:
    """Stores device information"""

    def __init__(self, id: int, time: datetime, phase: int, vendor: str, model: str, randomization: int):
        self.id = id
        self.time_phase_changed = time
        self.phase = phase  # 0: locked, 1: awake, 2: active
        self.vendor = vendor
        self.model = model.replace(" ", "").lower()
        self.randomization = randomization  # 0: no randomization, 1: randomization
        self.SSID = []  # can be a list of SSID "ssid1, ssid2, ssid3"
        self.mac_address = []
        self.number_packets_sent = 0
        self.number_bursts_sent = 0
        self.wps = None
        self.uuide = None

        if self.randomization == 0:
            # if randomization is disabled, create a MAC address based on the vendor name
            self.mac_address.append(self.create_mac_address())

        # Paper: "Exploration of User Privacy in 802.11 Probe Requests with MAC Address Randomization Using Temporal Pattern Analysis"
        has_wps = np.random.choice([True, False], p=[0.11, 0.89])
        if has_wps:
            self.wps = bytes.fromhex(random_hex(number_of_elements=8))
            self.uuide = bytes.fromhex(random_hex(number_of_elements=8))
            # print(binascii.hexlify(self.wps).decode(), binascii.hexlify(self.uuide).decode())

        ssid = np.random.choice([True, False], p=[0.2, 0.8])
        if ssid:
            self.SSID = create_ssid()


    def create_mac_address(self) -> str:
        """Create a MAC address based on the vendor name of the device and return it"""
        mac_address = random_MAC()
        MAC_vend = (get_oui(self.vendor)[0]).lower()
        if MAC_vend != 0:
            mac_address = MAC_vend + (":%02x:%02x:%02x" % (
                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))).lower()

        return mac_address

    def send_probe(self,
                   inter_pkt_time: float,
                   VHT_capabilities: bytes,
                   extended_capabilities: bytes,
                   HT_capabilities: bytes,
                   num_pkt_burst: int,
                   time: datetime) -> list:
        """Function that create a probe packet"""
        # vendor_name model randomization SSID num_pkt_burst outfilename
        if self.randomization == 0:
            mac_address, packets = create_probe(self.vendor,
                                                self.randomization,
                                                self.SSID,
                                                num_pkt_burst,
                                                self.mac_address[0],
                                                inter_pkt_time,
                                                VHT_capabilities,
                                                extended_capabilities,
                                                HT_capabilities,
                                                self.wps,
                                                self.uuide,
                                                time)
        else:
            # if randomization is enabled, use Broadcom as vendor name
            mac_address, packets = create_probe("Broadcom",
                                                self.randomization,
                                                self.SSID,
                                                num_pkt_burst,
                                                "",
                                                inter_pkt_time,
                                                VHT_capabilities,
                                                extended_capabilities,
                                                HT_capabilities,
                                                self.wps,
                                                self.uuide,
                                                time)
        if self.randomization == 0:
            if self.mac_address[0] != mac_address:
                raise Exception("SOMETHING WENT WRONG!")
        else:
            self.mac_address.append(mac_address)
        return packets

    def change_phase(self, phase: int, time: datetime) -> None:
        """Function to change the phase of the device"""
        self.phase = phase
        self.time_phase_changed = time

    def print_information(self, file_name: str) -> None:
        """Function to print device information"""
        with open(file_name + '.txt', 'a') as f:
            f.write("\n")
            f.write("Device {} information:\n".format(self.id))
            f.write("Vendor: {}\n".format(self.vendor))
            f.write("Model: {}\n".format(self.model))
            f.write("Use randomization: {}\n".format(self.randomization))
            f.write("MAC address: {}\n".format(self.mac_address))
            f.write("SSID: {}\n".format(self.SSID))

    def print_statistics(self, file_name: str) -> None:
        """Function to print device statistics of probe packets sent"""
        with open(file_name + '.txt', 'a') as f:
            f.write("Number of different MAC address: {}\n".format(len(self.mac_address)))
            f.write("Number of packets sent: {}\n".format(self.number_packets_sent))
            f.write("Number of different bursts sent: {}\n".format(self.number_bursts_sent))

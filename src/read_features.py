import numpy as np
from json import load
import os


class DeviceRates:
    """Device constant information"""

    def __init__(self):
        self._database = dict()
        # Populate the database with first information
        # This latter are about vendor, model, burst length, use of randomization and 802.11 capabilities
        current_directory = os.getcwd()
        with open("./database/general_features.json", "r") as file_read:
            features = load(file_read)
            for f in features:
                self._database[f["device_name"]] = {
                    "vendor": f["vendor"],
                    "burst_length": {float(it.split(":")[0]): float(it.split(":")[1]) for it in f["burst_length"].split("/")},
                    "randomization": int(f["use_randomization"]),
                    "VHT_capabilities": None if f["VHT_capabilities"] == "?" else bytes.fromhex(str(f["VHT_capabilities"].replace("x", ""))),
                    "extended_capabilities": None if f["extended_capabilities"] == "?" else bytes.fromhex(str(f["extended_capabilities"].rstrip().replace("x", ""))),
                    "HT_capabilities": None if f["HT_capabilities"] == "?" else bytes.fromhex(str(f["HT_capabilities"].rstrip().replace("x", "") + "ffff000000000000000000000000000000000000000000"))
                }
        # Populate the database with second information
        # This latter are about time between different bursts and time between packets in the same burst
        # Each value is associated with a probability
        with open("./database/time_features.json", "r") as file_read:
            features = load(file_read)
            for f in features:
                self._database[f["device_name"]]["prob_int_burst"] = list()
                self._database[f["device_name"]]["prob_between_bursts"] = list()
                self._database[f["device_name"]]["prob_int_burst"].append(
                    (
                        f["phase"],
                        {float(value): float(prob) for value,prob in f["time_between_packets_in_burst"].items()}
                     )
                )
                self._database[f["device_name"]]["prob_between_bursts"].append(
                    (
                        f["phase"],
                        {float(value): float(prob) for value,prob in f["time_between_different_bursts"].items()}
                     )
                )

    def get_element(self, model: str) -> dict:
        """Returns an element from the dictionary with all information, given its model"""
        try:
            return self._database[model.replace(" ", "").lower()]
        except KeyError as e:
            print(f"An error occurred: {e}")
            exit(-1)

    def get_randomization(self, model: str) -> int:
        """Returns the randomization key (0 no, 1 yes) for a specific device model"""
        return self.get_element(model)["randomization"]

    def get_burst_lengths(self, model: str) -> dict:
        """Returns the probabilities of burst lengths associated with a certain model"""
        return self.get_element(model)["burst_length"]

    def get_prob_between_bursts(self, model: str, phase: int) -> dict:
        """Returns the probabilities of times between different bursts associated with a certain model"""
        probs = self.get_element(model)["prob_between_bursts"]
        prob_phase = list(filter(lambda x: x[0] == phase, probs))[0]
        return prob_phase[1]

    def get_prob_int_burst(self, model: str, phase: int) -> dict:
        """Returns the probabilities of times between packets inside the same burst associated with a certain model"""
        probs = self.get_element(model)["prob_int_burst"]
        prob_phase = list(filter(lambda x: x[0] == phase, probs))[0]
        return prob_phase[1]

    def get_VHT_capabilities(self, model: str) -> bytes:
        """Returns the VHT capabilities associated with a device model"""
        return self.get_element(model)["VHT_capabilities"]

    def get_extended_capabilities(self, model: str) -> bytes:
        """Returns the extended capabilities associated with a device model"""
        return self.get_element(model)["extended_capabilities"]

    def get_HT_capabilities(self, model: str) -> bytes:
        """Returns the VHT capabilities associated with a device model"""
        return self.get_element(model)["HT_capabilities"]

    # vendor, model, burst, randomization = simulator.database.get_random_device()  # get random device
    def get_random_device(self) -> [str, str, int]:
        """Returns a random device model from the database"""
        # percentage of market share in Europe 2020-2023 mobile devices https://gs.statcounter.com/vendor-market-share/mobile/europe/#yearly-2020-2023-bar
        # Apple 28.5%, Samsung 20.5%, Huawei 14.5%, Xiaomi 7.5%, OnePlus 3.5%, Lenovo 2.5%
        index = np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8], size=1,
                              p=[0.200, 0.030, 0.050, 0.090, 0.045, 0.266, 0.097, 0.188, 0.034])[0]
        model = list(self._database)[index]
        device = self._database.get(model)
        return device['vendor'], model, int(device['randomization'])

    def is_sending_probe(self, model: str, phase: int) -> bool:
        """Returns true if the device is sending probe requests in a certain phase, false otherwise"""
        # If in the database there isn't a rate associated with the given phase, return False
        rates = self.get_element(model)["prob_between_bursts"]
        rates = list(filter(lambda x: x[0] == phase, rates))
        return False if len(rates) == 0 else True

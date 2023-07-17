import numpy as np
from typing import List, Tuple

class DeviceRates:
    """Device constant information"""

    def __init__(self):
        self._database = dict()
        # Populate the database with first information
        # This latter are about vendor, model, burst length, use of randomization and 802.11 capabilities
        with open("./information1.txt", "r") as file_read:
            line = file_read.readline().replace("\\n", "")
            while line:
                if line.startswith("#"):
                    line = file_read.readline().replace("\\n", "")
                    continue
                elements = line.split(",")
                vendor = elements[0]
                model = elements[1]
                burst_probs = elements[2]
                burst_length = {float(it.split(":")[0]): float(it.split(":")[1]) for it in burst_probs.split("/")}
                randomization = int(elements[3])
                VHT_capabilities = elements[4]
                if VHT_capabilities == "?":
                    VHT_capabilities = None
                else:
                    VHT_capabilities = bytes.fromhex(str(VHT_capabilities.replace("x", "")))
                extended_capabilities = bytes.fromhex(str(elements[5].rstrip().replace("x", "")))
                HT_capabilities = bytes.fromhex(str(elements[6].rstrip().replace("x", "") + "ffff000000000000000000000000000000000000000000"))
                # Store the new collected information
                self.set_first_information(
                    vendor,
                    model,
                    burst_length,
                    randomization,
                    VHT_capabilities,
                    extended_capabilities,
                    HT_capabilities
                )
                line = file_read.readline().replace("\\n", "")

        # Populate the database with second information
        # This latter are about time between different bursts and time between packets in the same burst
        # Each value is associated with a probability
        with open("./information2.txt", "r") as file_read:
            line = file_read.readline().replace("\\n", "")
            while line:
                if line.startswith("#"):
                    line = file_read.readline().replace("\\n", "")
                    continue
                # Take all the device phases
                prob_int_burst = list()
                prob_between_bursts = list()
                elements = line.split(",")
                for i in range(3):
                    model = elements[0]
                    phase = int(elements[1])
                    prob_int_burst.append((
                        phase,
                        [(float(prob.split(":")[0]), float(prob.split(":")[1])) for prob in elements[2].split("/")]
                    ))
                    prob_between_bursts.append((
                        phase,
                        [(float(prob.split(":")[0]), float(prob.split(":")[1])) for prob in elements[3].split("/")]
                    ))
                    # check_probs(elements[2], elements[3], phase, model)
                    line = file_read.readline().replace("\\n", "")
                    elements = line.split(",")
                    if model != elements[0]:
                        break
                # Store the new collected information
                # The Data Structures for the probabilities send are in form: list[tuple[int, list[tuple[float, float]]]]
                # Where each tuple inside the external list contains an integer that represents the phase
                # and a list of float tuples that represent the value and the probability associated
                self.set_second_information(
                    model,
                    prob_int_burst,
                    prob_between_bursts
                )
                # line = file_read.readline().replace("\\n", "")

    def set_first_information(self,
                              vendor: str,
                              model: str,
                              burst_length: dict,
                              randomization: int,
                              VHT_capabilities: bytes,
                              extended_capabilities: bytes,
                              HT_capabilities: bytes) -> None:
        """Sets a new element in model database"""
        self._database[model] = {
            "vendor": vendor,
            "model": model,
            "burst_lengths": burst_length,
            "randomization": randomization,
            "VHT_capabilities": VHT_capabilities,
            "extended_capabilities": extended_capabilities,
            "HT_capabilities": HT_capabilities
        }

    def set_second_information(self,
                               model: str,
                               prob_int_burst: List[Tuple[int, List[Tuple[float, float]]]],
                               prob_between_bursts: List[Tuple[int, List[Tuple[float, float]]]]) -> None:
        """Update the model element in the database"""
        self._database[model]["prob_int_burst"] = list()
        self._database[model]["prob_between_bursts"] = list()

        # Put in the database the inter packet times and the burst rates with the associated phase
        for phase, prob in prob_int_burst:
            self._database[model]["prob_int_burst"].append((phase, {v: p for v, p in prob}))
        for phase, prob in prob_between_bursts:
            self._database[model]["prob_between_bursts"].append((phase, {v: p for v, p in prob}))

    def get_element(self, model: str) -> dict:
        """Returns an element from the dictionary with all information, given its model"""
        return self._database[model.replace(" ", "").lower()]

    def get_randomization(self, model: str) -> int:
        """Returns the randomization key (0 no, 1 yes) for a specific device model"""
        return self.get_element(model)["randomization"]

    def get_burst_lengths(self, model: str) -> dict:
        """Returns the probabilities of burst lengths associated with a certain model"""
        return self.get_element(model)["burst_lengths"]

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
        device = self._database.get(list(self._database)[index])
        return device['vendor'], device['model'], int(device['randomization'])

    def is_sending_probe(self, model: str, phase: int) -> bool:
        """Returns true if the device is sending probe requests in a certain phase, false otherwise"""
        # If in the database there isn't a rate associated with the given phase, return False
        rates = self.get_element(model)["prob_between_bursts"]
        rates = list(filter(lambda x: x[0] == phase, rates))
        return False if len(rates) == 0 else True

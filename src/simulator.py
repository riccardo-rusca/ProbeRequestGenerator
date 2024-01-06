from src.device import *
from src.read_features import *


class Simulator:
    """Device's model and vendor behaviour simulator"""

    def __init__(self, out_file: str, avg_number_of_devices: int, avg_permanence_time: int, closed_environment: bool):
        self.database = DeviceRates()
        self.out_file = out_file
        open(out_file + '.txt', 'w')
        open(out_file + '.pcap', 'w')
        open(out_file + '_probe_ids.txt', 'w')
        self.next_id_device = 0
        self.events_list = []
        self.devices_list = []
        self.number_of_devices_available = 0
        self.average_number_of_devices_available = avg_number_of_devices
        self.average_permanence_time = avg_permanence_time
        self.closed_environment = closed_environment

    def new_burst(self, time: datetime, device: Device) -> tuple[float, float, int, list]:
        """Manage device probe request creation and return the deltatime to add for the next probe request"""
        # Inter packet time probabilities (need to be normalized)
        int_pkt_time = self.database.get_prob_int_burst(device.model, device.phase)
        int_keys = list(int_pkt_time.keys())
        int_probs = np.asarray(list(int_pkt_time.values())).astype("float64")
        int_probs = int_probs / np.sum(int_probs)
        # Burst rate probabilities (need to be normalized)
        burst_rates = self.database.get_prob_between_bursts(device.model, device.phase)
        rates_keys = list(burst_rates.keys())
        rate_probs = np.asarray(list(burst_rates.values())).astype("float64")
        rate_probs = rate_probs / np.sum(rate_probs)
        # Burst length probabilities (no need to be normalized)
        burst_length = self.database.get_burst_lengths(device.model)

        int_pkt_time_chosen = np.random.choice(int_keys, size=1, p=int_probs)[0]
        burst_rate_chosen = np.random.choice(rates_keys, size=1, p=rate_probs)[0]
        burst_length_chosen = np.random.choice(list(burst_length.keys()), size=1, p=list(burst_length.values()))[0]

        packets = device.send_probe(int_pkt_time_chosen,
                                    self.database.get_VHT_capabilities(device.model),
                                    self.database.get_extended_capabilities(device.model),
                                    self.database.get_HT_capabilities(device.model),
                                    burst_length_chosen,
                                    time)

        return int_pkt_time_chosen, burst_rate_chosen, burst_length_chosen, packets

    def add_device(self, device: Device) -> None:
        """Add a device to the list of devices"""
        self.devices_list.append(device)
        self.next_id_device += 1
        self.number_of_devices_available += 1

import datetime
from scapy.utils import wrpcap
from simulator import *
from datetime import timedelta

TIME_OFFSET = timedelta(seconds=0.001)


class Event:
    """Simulator event"""

    def __init__(self,
                 start_time: datetime,
                 job_type: str,
                 device: Device = None,
                 phase: int = None,
                 vendor: str = None,
                 model: str = None,
                 packet=None,
                 burst_end: bool = None):
        self.start_time = start_time
        self.device = device
        self.job_type = job_type
        self.phase = phase
        self.vendor = vendor
        self.model = model
        self.packet = packet
        self.burst_end = burst_end


def handle_event(event: Event, simulator: Simulator):
    """Handle event based on job_type (can be "change_phase", "create_device", "delete_device", "send_packet", "create_burst")"""

    if event.job_type == "change_phase":
        change_phase(simulator, event.device, event.phase, event.start_time)
        phase, seconds_before_change = generate_phase(event.phase)
        _ = add_new_event(simulator, (Event(
            start_time=event.start_time + timedelta(seconds=seconds_before_change),
            job_type="change_phase",
            device=event.device,
            phase=phase
        )))

        clean_events_after_change_phase(simulator, event.device)
        if simulator.database.is_sending_probe(event.device.model, event.device.phase):
            _ = add_new_event(simulator, (Event(
                start_time=event.start_time,
                job_type="create_burst",
                device=event.device
            )))  # schedule probe request now to start new phase behaviour

    elif event.job_type == "create_burst":
        if simulator.database.is_sending_probe(event.device.model, event.device.phase):
            int_pkt_time, burst_rate, burst_length, packets = simulator.new_burst(event.start_time, event.device)
            counter_sum = timedelta(seconds=0.0)
            for i in range(int(burst_length)):
                counter = add_new_event(simulator, (Event(
                    start_time=event.start_time + i * timedelta(seconds=int_pkt_time) + counter_sum,
                    job_type="send_packet",
                    device=event.device,
                    packet=packets[i],
                    burst_end=True if i == burst_length - 1 else False
                )))
                counter_sum += counter
                # Packets have to be updated with the temporal shift like the event
                # The inter packet time addition is already inside the packets when they are created
                packets[i].time = (datetime.fromtimestamp(packets[i].time) + counter_sum).timestamp()

            _ = add_new_event(simulator, (Event(
                start_time=event.start_time + (burst_length - 1) * timedelta(
                    seconds=int_pkt_time) + counter_sum + timedelta(seconds=burst_rate),
                job_type="create_burst",
                device=event.device
            )))

    elif event.job_type == "send_packet":
        if event.burst_end:
            event.device.number_bursts_sent += 1
        with open(simulator.out_file + '_probe_ids.txt', 'a') as f:
            f.write("{}\n".format(event.device.id))
        wrpcap(simulator.out_file + ".pcap", event.packet, append=True)
        event.device.number_packets_sent += 1

    elif event.job_type == "create_device":
        phase = np.random.choice([0, 1, 2], size=1, p=[0.35, 0.15, 0.50])[
            0]  # probability of starting in locked phase is 35%, in awake phase is 15% and in active phase is 50%
        device = create_device(simulator, event.start_time, phase, event.vendor, event.model)
        new_phase, seconds_before_change = generate_phase(event.phase)

        _ = add_new_event(simulator, (Event(
            start_time=event.start_time + timedelta(seconds=seconds_before_change),
            job_type="change_phase",
            device=device,
            phase=new_phase
        )))  # schedule phase change

        if simulator.database.is_sending_probe(device.model, device.phase):
            _ = add_new_event(simulator, (Event(
                start_time=event.start_time,
                job_type="create_burst",
                device=device
            )))  # schedule first probe request

        if not simulator.closed_environment:
            _ = add_new_event(simulator, (Event(
                start_time=event.start_time + timedelta(seconds=simulator.average_permanence_time),
                job_type="delete_device",
                device=device
            )))  # schedule device death
            next_device_creation = simulator.average_permanence_time / simulator.average_number_of_devices_available  # calculate next device creation time with little law
            vendor, model, randomization = simulator.database.get_random_device()  # get random device
            _ = add_new_event(simulator, (Event(
                start_time=event.start_time + timedelta(seconds=next_device_creation),
                job_type="create_device",
                vendor=vendor,
                model=model
            )))

    elif event.job_type == "delete_device":
        delete_device(simulator, event.device, event.start_time)
        clean_events_after_delete_device(simulator, event.device.id)


def generate_phase(phase: int) -> [int, int]:
    """Generate phase based on the given phase"""
    new_phase = 0
    seconds_before_change = 0
    if phase == 0:
        new_phase = np.random.choice([1, 2], size=1, p=[0.2, 0.8])[
            0]  # probability of going to awake phase is 20% and to active phase is 80%
        seconds_before_change = random.expovariate(1 / (60 * 5))  # next change phase after mean 5 minutes
    elif phase == 1:
        new_phase = np.random.choice([0, 2], size=1, p=[0.9, 0.1])[
            0]  # probability of going back to locked phase is 90% and to active phase is 10%
        seconds_before_change = random.expovariate(1 / 30)  # next change phase after mean 30 seconds
    elif phase == 2:
        new_phase = 0  # probability of going back to locked phase is 100%
        seconds_before_change = random.expovariate(1 / (60 * 3))  # next change phase after mean 3 minutes
    return new_phase, seconds_before_change


def change_phase(simulator: Simulator, device: Device, phase: int, time: datetime) -> None:
    """Change phase of the given device"""
    device.change_phase(phase, time)
    with open(simulator.out_file + '.txt', 'a') as f:
        f.write("Device number {} ({}) changed phase to {} at time: {}\n".format(device.id,
                                                                                 device.vendor + ' ' + device.model,
                                                                                 phase, time))


def delete_device(simulator: Simulator, device: Device, time: datetime) -> None:
    """Delete device"""
    device.time_phase_changed = time
    simulator.number_of_devices_available -= 1
    with open(simulator.out_file + '.txt', 'a') as f:
        f.write(
            "Device number {} ({}) deleted at time: {}\n".format(device.id, device.vendor + ' ' + device.model, time)
        )


def create_device(simulator: Simulator, time: datetime, phase: int, vendor: str, model: str) -> Device:
    """Create a new device and return it"""
    randomization = simulator.database.get_randomization(model)
    device = Device(simulator.next_id_device, time, phase, vendor, model, randomization)
    simulator.add_device(device)
    with open(simulator.out_file + '.txt', 'a') as f:
        f.write(
            "Device number {} ({}) created at time: {}\n".format(device.id, device.vendor + ' ' + device.model, time))
    return device


def add_new_event(simulator: Simulator, event: Event) -> timedelta:
    """Add a new event to the list of events"""
    # If some send_packet events overlap, we must move forward the new added and all the packets in the same burst sent after
    # This is why we introduced the variable counter that its incremented at each shift in the event queue
    # The variable is returned for the correct managing of the following packets inside the burst and for the following burst
    counter = timedelta(seconds=0.0)
    if event.job_type == "send_packet":
        for e in simulator.events_list:
            if e.job_type == "send_packet" and e.start_time == event.start_time:
                counter += TIME_OFFSET
                event.start_time += TIME_OFFSET
    simulator.events_list.append(event)
    # If two events of type respectively send_packet and create_burst are time overlapped, it's more convenient to have the send_packet put after
    # In that way the create_burst will create a new packet that will be time overlapped with the one mentioned before
    # But with the logic written for managing this case, everything will be managed with the time shift done above
    simulator.events_list.sort(key=lambda x: (x.start_time, 1 if x.job_type == "send_packet" else 0))

    return counter


def clean_events_after_change_phase(simulator, device):
    """Remove all sending events related to the given device when they are scheduled but it changed its phase"""
    simulator.events_list = [x for x in simulator.events_list if
                             x.job_type == "create_device" or
                             (x.device.id != device.id or (
                                         x.device.id == device.id and x.job_type != "create_burst" and x.job_type != "send_packet"))]


def clean_events_after_delete_device(simulator, device_id):
    simulator.events_list = list(
        filter(lambda x: x.device is not None and x.device.id != device_id, simulator.events_list))

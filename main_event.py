from event import *

# DEVICES = [
#     "Apple iPhone6",
#     "Huawei P9Lite",
#     "Xiaomi Note8T",
#     "Oneplus Nord5G",
#     "Xiaomi Mi9Lite",
#     "Apple iPhone13Pro",
#     "Apple iPhone14Pro",
#     "Apple iPhone11",
#     "Apple iPad8",
#     "Apple MacM1",
#     "Apple iPhone7",
#     "Apple MacAir",
#     "Samsung Note20Ultra",
#     "Lenovo Thinkpadx13Gen1",
# ]

DEVICE_CHOSEN = {
    "Apple iPhone11": 1,
}

AVG_NUMBER_OF_DEVICES = 15
AVG_PERMANENCE_TIME = 15*60
REAL_MINUTES = 1

out_file = 'out_file'
simulator = Simulator(out_file, avg_number_of_devices=AVG_NUMBER_OF_DEVICES, avg_permanence_time=AVG_PERMANENCE_TIME)
open(simulator.out_file + '.txt', 'w')
open(simulator.out_file + '.pcap', 'w')
open(simulator.out_file + '_probe_ids.txt', 'w')
start_time = datetime.now()
print(start_time)

print('+++++++++++\nStart simulation\n+++++++++++')

for k in DEVICE_CHOSEN.keys():
    for _ in range(DEVICE_CHOSEN[k]):
        add_new_event(simulator, Event(start_time, "create_device", vendor=k.split(" ")[0], model=k.split(" ")[1]))

with open(simulator.out_file + '.txt', 'a') as f:
    f.write('+++++++++++Simulation start+++++++++++\n')
    f.write('Initial time (real and simulated): {}\n'.format(start_time))


while datetime.now() < start_time + timedelta(seconds=REAL_MINUTES*60) and len(simulator.events_list) > 0:
    event = simulator.events_list.pop(0)  # take the first event from the list
    last_time = event.start_time
    handle_event(event, simulator)  # handle the event

end_time = datetime.now()
alive_devices = [ev.device.id for ev in simulator.events_list if ev.device is not None]
for device in simulator.devices_list:
    if device.id in alive_devices:
        delete_device(simulator, device, last_time)

print("\n+++++++++++\nSimulation end\n+++++++++++")
print(end_time)

different_MACs = 0
num_pkts = 0
for device in simulator.devices_list:
    device.print_information(simulator.out_file)
    device.print_statistics(simulator.out_file)
    num_pkts += device.number_packets_sent
    different_MACs += len(device.mac_address)

with open(simulator.out_file + '.txt', 'a') as f:
    f.write('\n+++++++++++Simulation end+++++++++++\n')
    f.write('End time (real): {}\n'.format(end_time))
    f.write('End time (simulated): {}\n'.format(last_time))
    f.write('Time ratio (simulated/real): {}\n'.format(round((last_time - start_time) / (end_time - start_time), 2)))
    f.write('List of devices and statistics\n')
    f.write('\nTotal number of different MAC addresses: ' + str(different_MACs) + '\n')
    f.write('Total number of packets sent: ' + str(num_pkts) + '\n')
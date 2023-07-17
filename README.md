# WiFi Probe Request Generator

If you use the content of this repository, please reference the following paper: 
> soon available


### Overview
| Specification |            |  
|----------|-------------|
| Subject |  Engineering | 
| Specific subject area |  Generator that is able to produce WiFi packets of probe requests type, simulating the real behaviour of the considered devices |
| Type of scripts  | Python |    
| Rights reserved  | Institution: Politecnico di Torino <br> City/Town/Region: Torino, TO <br> Country: Italy  |   


### List of devices ued in the generator
| Type   |  Vendor | Model | OS | Year | 
|----------|-------------|-------------|:-------------:|:-------------:|
| SmartPhone |  Apple | iPhone 14 Pro | iOS 16.4  | 2022 |
| SmartPhone |  OnePlus | Nord 5G | Android 11.0 | 2021 |
| SmartPhone |  Apple | iPhone 13 Pro | iOS 16.3 | 2021 |
| SmartPhone |  Samsung | Note 20 Ultra | Android 12.0 | 2020 |
| SmartPhone |  Xiaomi | Mi9 Lite | Android 10.0  | 2020 |
| SmartPhone |  Apple | iPhone 11 | iOS  15.0.1 | 2019 |
| SmartPhone |  Xiaomi | Redmi Note 8T | Android   10.0  | 2019 |
| SmartPhone |  Huawei | P9 Lite | Android   7.0  | 2016 |
| SmartPhone |  Apple | iPhone 7 | iOS 15.2 | 2016 |
| SmartPhone |  Apple  | iPhone 6 | iOS   12.5.5  | 2014 |
| Tablet |  Apple  | iPad 8 | iPadOS  14.8.1  | 2020 |
| Laptop | Lenovo | ThinkPad X13 Gen1 | Windows   11 | 2021 |
| Laptop | Apple  | MacBookAir M1 | macOS   12.1 | 2020 |
| Laptop | Apple  | MacBookPro | macOS 11.6.2 | 2015 |

### Files description
* [*device.py*](device.py) &rarr; contains all the informations and functions related to the device class.
* [*device_information.py*](device_information.py) &rarr; contains all the functions that read the device information in [*information1.txt*](information1.txt) and [*information2.txt*](information2.txt).
* [*event.py*](event.py) &rarr; contains all the informations and functions related to the event class.
* [*main_event.py*](main_event.py) &rarr; contains the main code, where all the input parameters are set.
* [*packet.py*](packet.py) &rarr; contains the code for the creation of a Probe Request packet, using scapy library.
* [*simulator.py*](simulator.py) &rarr; contains all the informations and functions related to the simulator class.
* [*utility.py*](utility.py) &rarr; contains some utility functions.

### Contacts
* Riccardo Rusca [riccardo.rusca@polito.it]
* Diego Gasco [diego.gasco@studenti.polito.it]
* Claudio Casetti [claudio.casetti@polito.it]
* Paolo Giaccone [paolo.giaccone@polito.it]

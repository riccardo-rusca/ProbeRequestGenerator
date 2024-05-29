# WiFi Probe Request Generator

If you use the content of this repository, please reference the following paper: 
> R. Rusca, A. Carluccio, D. Gasco and P. Giaccone, "Privacy-Aware Crowd Monitoring and WiFi Traffic Emulation for Effective Crisis Management," 2023 International Conference on Information and Communication Technologies for Disaster Management (ICT-DM), Cosenza, Italy, 2023, pp. 1-6, doi: 10.1109/ICT-DM58371.2023.10286944. [URL](https://ieeexplore.ieee.org/document/10286944) [BibTeX](/cite.bib)


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
* [*/src/device.py*](src/device.py) &rarr; contains all the informations and functions related to the device class.
* [*/src/read_features.py*](src/read_features.py) &rarr; contains all the functions that read the device information in [*/database/general_features.json*](database/general_features.json) and [*/database/time_features.json*](/database/time_features.json).
* [*/src/event.py*](src/event.py) &rarr; contains all the informations and functions related to the event class.
* [*/src/main_event.py*](src/main_event.py) &rarr; contains the main code, where all the input parameters are set.
* [*/src/packet.py*](src/packet.py) &rarr; contains the code for the creation of a Probe Request packet, using scapy library.
* [*/src/simulator.py*](src/simulator.py) &rarr; contains all the informations and functions related to the simulator class.
* [*/utility/utils.py*](utility/utils.py) &rarr; contains some utility functions.
* [*/utility/oui_formatter.py*](utility/oui_formatter.py) &rarr; contains functions for OUI management.

### Contacts
* Riccardo Rusca [riccardo.rusca@polito.it]
* Diego Gasco [diego.gasco@polito.it]
* Claudio Casetti [claudio.casetti@polito.it]
* Paolo Giaccone [paolo.giaccone@polito.it]

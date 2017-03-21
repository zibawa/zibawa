# zibawa 

Open source IoT from device to dashboard

## Description

Zibawa integrates other open source software to form a complete software stack for IoT.

Using Zibawa along with Grafana, rabbitMQ, InfluxDB and OpenLDAP you can run a secure end to end IoT management system.

Zibawa is built in Django framework using Python 3

## Features

### Device management

Devices and their related channels are created, and information about what the channel is measuring is added.

### MQTT message testing

Different message formats can be tested on web interface to ensure they can be interpreted and visualized in the dashboards correctly.

### MQTT message interpreting and enrichment

Timestamps are parsed from messages or added.
Channel data is added to the message values as indexable tag
Hooks enable further data to be added to the stored message, for example, a mqtt message containing an RFID tag would be stored along with information about (for example) the production batch, part number relating to the tag.


### MQTT message storage

Messages are stored on the configured database backend. Currently comptible with InfluxDB and elasticsearch


### Kura CloudService interpreter

Kura is an [[open source gateway project]](http://eclipse.github.io/kura/) . Kura by default sends messages using google protocol buffers. Zibawa includes a decoder to enable you to use Kura cloud service "out of the box".

### Device authorization and security

All devices are authorized using encrypted passwords stored on openLDAP.
All communications are encrypted using TLS.

### Stack management
Web tools enable you to monitor the different parts of the stack to ensure they are running and configured to work together.


## Aplications

*Industrie 4.0
*Industrial machinery monitoring
*RFID traceability

## Documentation and Installation

[Full documentation for Zibawa Open source IoT](https://docs.zibawa.com/)

## Contribution and Participation

Contributions and participation in the project are welcome! 

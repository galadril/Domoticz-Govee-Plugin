
# Govee Local Api Control plugin for Domoticz
This plugin allows you to discover Govee devices on your local network and create/update devices in Domoticz.


## Compatibility

This plugin requires Govee devices that support local API. A list of compatible devices can be found on Govee's documentation:
https://app-h5.govee.com/user-manual/wlan-guide


## Installation

Python version 3.4 or higher required & Domoticz version 3.87xx or greater.

To install:
* Go in your Domoticz directory using a command line and open the plugins directory.
* Run: ```git clone https://github.com/galadril/Domoticz-Govee-Plugin.git```
* Restart Domoticz.


## Configuration

* Open the Domoticz web interface.
* Go to Setup > Hardware.
* Add a new hardware with type Govee Discovery.
* Set the Scan interval (in seconds) for how often the plugin should scan for Govee devices.
* Save and close the dialog.


## Updating

To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-Yi-Hack-Plugin directory.
* Run: ```git pull```
* Restart Domoticz.


## Usage

The plugin will automatically discover compatible Govee devices on your local network and create/update devices in Domoticz. You can turn on/off the devices and set their brightness level from the Domoticz web interface.


## Debugging

You can enable debugging by setting the Debug parameter to a value between 1 and 6 in the Setup > Hardware dialog. More information about the debugging levels can be found in the Domoticz documentation.


## Change log

| Version | Information |
| ----- | ---------- |
| 0.0.1 | Initial version |


# Donation

If you like to say thanks, you could always buy me a cup of coffee (/beer)!   
(Thanks!)  
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)

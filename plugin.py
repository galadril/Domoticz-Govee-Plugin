"""
<plugin key="GoveeDiscovery" name="Govee Discovery" author="Mark Heinis" version="0.0.1"  wikilink="https://github.com/galadril/Domoticz-Govee-Plugin" externallink="">
    <description>
        Plugin to discover Govee devices on the local network and create/update devices in Domoticz.
    </description>
    <params>
        <param field="Mode1" label="Scan interval (sec)" width="200px" required="true" default="10" />
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import socket
import json
import time
import uuid

class GoveeDiscovery:
    def __init__(self):
        self.last_scan_time = 0
        
    def onStart(self):
        Domoticz.Log("onStart called")
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
        Domoticz.Heartbeat(int(Parameters["Mode1"]))
        return True

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, connection, status, description):
        Domoticz.Log("onConnect called")

    def onMessage(self, connection, data):
        Domoticz.Log("onMessage called")

    def onCommand(self, unit, command, level, hue):
        Domoticz.Log("onCommand called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        self.scan_devices()

    def scan_devices(self):
        Domoticz.Log("Scanning devices...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(5)
            sock.bind(('', 4002))
			
            message = b'{  \"msg\":{    \"cmd\":\"scan\",    \"data\":{      \"account_topic\":\"reserve\"    }  }}'
            Domoticz.Log("Sending discovery message")
            sock.sendto(message, ('239.255.255.250', 4001))
            
            receivedDevices = []
            while True:
                data, addr = sock.recvfrom(1024)
                ip_address = addr[0]
                
                if not data:
                    break
                
                try:
                    strData = data.decode("utf-8", "ignore")
                    
                    try:
                        device = self.parse_device(strData)
                        if device is not None:
                            receivedDevices.append(device)
                            Domoticz.Log("Found device: {}".format(device))

                            existingDevice = 0
                            for dev in Devices:
                                if (Devices[dev].DeviceID == device['ip']):
                                    existingDevice = dev
                                    
                            if (existingDevice == 0):
                                Domoticz.Device(Name=device['ip'], Unit=len(Devices)+1, Type=241, Subtype=2, Used=0, DeviceID=device['ip']).Create()
                                Domoticz.Log("Created device: "+device['id'])
                                
                            self.get_device_status(device)
                    except Exception as inst:
                        status = self.parse_status(strData)
                        status['id'] = ip_address
                        
                        if status is not None:
                            try:
                                Domoticz.Log("Found status: {}".format(status))
                                for dev in Devices:
                                    if (Devices[dev].DeviceID == status['id']):
                                        Devices[dev].Update(nValue=status['status'], sValue=status['color'], TimedOut=0)
                            except Exception as inst:
                                Domoticz.Log("Error: '"+str(inst)+"'")

                except Exception as inst:
                    Domoticz.Log("Skipping message with data: '"+str(strData)+"'")
                    
            sock.close()
        except Exception as e:
            Domoticz.Log("Not receiving new messages")
            
    def get_device_status(self, device):
        Domoticz.Log("Fetching status for device with ID {}".format(device['id']))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(30)
            message = b'{  \"msg\":{    \"cmd\":\"devStatus\",    \"data\":{      }  }}'
            sock.sendto(message, (device['ip'], 4003))
            data, addr = sock.recvfrom(1024)
            status = json.loads(data.decode())
            Domoticz.Log("Received status: {}".format(status))
            sock.close()
        except Exception as e:
            Domoticz.Log("Error while fetching status for device with ID {}: {}".format(device['id'], str(e)))
            
    def parse_device(self, data):
        device = json.loads(data)['msg']['data']
        device_id = device['device']
        device_name = device['sku']
        device_type = device['sku']
        device_ip = device['ip']
        return {'id': device_id, 'name': device_name, 'type': device_type, 'ip': device_ip}

    def parse_status(self, data):
        status = json.loads(data)['msg']['data']
        onOff = status['onOff']
        brightness = status['brightness']
        color = status['color']
        svalue = "{},{},{}".format(color['r'], color['g'], color['b'])
        self.statusDeviceId = ""
        return {'id': self.statusDeviceId, 'status': onOff, 'brightness': brightness, 'color': svalue}
            
global _plugin
_plugin = GoveeDiscovery()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

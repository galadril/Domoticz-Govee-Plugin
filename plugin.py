#           Govee Plugin
#
#           Author:     galadril, 2023
#
"""
<plugin key="Govee" name="Govee" author="galadril" version="0.0.1" wikilink="https://github.com/galadril/Domoticz-Govee-Plugin" externallink="">
    <description>
        <h2>Govee Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Lists Govee devices via local api.</li>
        </ul>
    </description>
    <params>
        <param field="APIKey" label="API Key" width="200px" required="true" default=""/>
        <param field="Mode6" label="Debug" width="200px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic + Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections + Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import sys
import json
import base64

class BasePlugin:
    GoveeConn = None
    nextConnect = 1
    apiKey = Parameters["APIKey"]
    oustandingPings = 0
    
    getDevices = { 'Verb' : 'GET', 'URL'  : '/v1/devices', 'Headers' : {'Govee-API-Key': apiKey}}
        
    def onStart(self):
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
            
        sendAfterConnect = getDevices
        
        self.GoveeConn = Domoticz.Connection(Name="GoveeConn", Transport="TCP/IP", Protocol="HTTP", Address=developer-api.govee.com)
        self.GoveeConn.Connect()
        
        for Device in Devices:
            UpdateDevice(Device, Devices[Device].nValue, Devices[Device].sValue, 1)
            
        Domoticz.Heartbeat(10)
        return True
        
    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            Domoticz.Log("Connected successfully to: "+Connection.Address)
            self.GoveeConn.Send(self.sendAfterConnect)
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Connection.Address+":"+Connection.Port)
            Domoticz.Debug("Failed to connect ("+str(Status)+") to: "+Connection.Address+":"+Connection.Port+" with error: "+Description)
            for Key in Devices:
                UpdateDevice(Key, 0, Devices[Key].sValue, 1)
        return True

    def onMessage(self, Connection, Data):
        try:
            Response = json.loads(Data["data"])
            DumpJSONResponseToLog(Response)
            
            counter = 0
            for device in Response['devices']:
                counter = counter + 1
                
                if (counter not in Devices):
                    Domoticz.Device(Name=device['deviceName'], Unit=1, Type=241, Subtype=6,  Switchtype=7).Create()
                
        except: 
            Domoticz.Log("No json payload received.")
            
        return True

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level) + ", Connected: " + str(self.GoveeConn.Connected()))
       
        if (self.GoveeConn.Connected() == False):
            self.GoveeConn.Connect()
        else:
            self.GoveeConn.Send(self.sendAfterConnect)
        
        return True

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)
        return

    def onHeartbeat(self):
        try:
            if (self.GoveeConn.Connected()):
                if (self.oustandingPings > 3):
                    self.GoveeConn.Disconnect()
                    self.nextConnect = 0
                else:
                    self.GoveeConn.Send(self.getDevices)
                    self.oustandingPings = self.oustandingPings + 1
            else:
                # if not connected try and reconnected every 3 heartbeats
                self.oustandingPings = 0
                self.nextConnect = self.nextConnect - 1
                self.sendAfterConnect = self.getDevices
                if (self.nextConnect <= 0):
                    self.nextConnect = 1
                    self.GoveeConn.Connect()
            return True
        except:
            Domoticz.Log("Unhandled exception in onHeartbeat, forcing disconnect.")
            self.onDisconnect(self.GoveeConn)
            self.GoveeConn = None
        
    def onDisconnect(self, Connection):
        Domoticz.Log("Device has disconnected")
        return

    def onStop(self):
        Domoticz.Log("onStop called")
        return True

    def TurnOn(self):
        self.GoveeConn.Send(self.sendOnAction)
        return

    def TurnOff(self):
        self.GoveeConn.Send(self.sendOffAction)
        return

    def ClearDevices(self):
        # Stop everything and make sure things are synced
        self.cameraState = 0
        self.SyncDevices(0)
        return
        
global _plugin
_plugin = BasePlugin()

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

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Settings count: " + str(len(Settings)))
    for x in Settings:
        Domoticz.Debug( "'" + x + "':'" + str(Settings[x]) + "'")
    for x in Images:
        Domoticz.Debug( "'" + x + "':'" + str(Images[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def debugDevices(self, Devices, Unit):
    Domoticz.Log("Device Name: %s" % Devices[Unit].Name)
    Domoticz.Log("       DeviceId: %s" % Devices[Unit].DeviceID)
    Domoticz.Log("       Type: %s" % Devices[Unit].Type)
    Domoticz.Log("       Subtype: %s" % Devices[Unit].SubType)
    Domoticz.Log("       SwitchType: %s" % Devices[Unit].SwitchType)
    Domoticz.Log("       Options: %s" % Devices[Unit].Options)
    Domoticz.Log("       LastLevel: %s" % Devices[Unit].LastLevel)
    Domoticz.Log("       LastUpdate: %s" % Devices[Unit].LastUpdate)

def DumpJSONResponseToLog(jsonDict):
    if isinstance(jsonDict, dict):
        Domoticz.Log("JSON Response Details ("+str(len(jsonDict))+"):")
        for x in jsonDict:
            if isinstance(jsonDict[x], dict):
                Domoticz.Log("--->'"+x+" ("+str(len(jsonDict[x]))+"):")
                for y in jsonDict[x]:
                    Domoticz.Log("------->'" + y + "':'" + str(jsonDict[x][y]) + "'")
            else:
                Domoticz.Log("--->'" + x + "':'" + str(jsonDict[x]) + "'")

def UpdateDevice(Unit, nValue, sValue, TimedOut):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (Devices[Unit].TimedOut != TimedOut):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

# Synchronise images to match parameter in hardware page
def UpdateImage(Unit):
    if (Unit in Devices) and (Parameters["Mode1"] in Images):
        Domoticz.Debug("Device Image update: '" + Parameters["Mode1"] + "', Currently "+str(Devices[Unit].Image)+", should be "+str( Images[Parameters["Mode1"]].ID))
        if (Devices[Unit].Image != Images[Parameters["Mode1"]].ID):
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=str(Devices[Unit].sValue), Image=Images[Parameters["Mode1"]].ID)
    return
import re
import serial
import time
import urllib
import urllib2
import xml.etree.ElementTree as ET
from awake import wol
import socket
from time import gmtime, strftime
import json
import sys
#import pdb 

class commandprocessor(object):

   def handle_command(self,command):

      if command == "":
         return "processing"
      commands = self.get_commands()
      results = "processing"
      try:
         tempActions = (item["actions"] for item in commands if item["name"] == command).next()
         for action in tempActions:
            if (action.get('type') == 'serial'):
               #pdb.set_trace()
               if (action.get('chassis') == '1'): 
                   sp = serial.Serial("/dev/ttyUSB0",19200, timeout=0)
               else:
                   sp = serial.Serial("/dev/ttyUSB1",19200, timeout=0)
               sp.write(action.get('data') + '\r')
               time.sleep(float(action.get('delay')))
               time.sleep(.1)
               sp.close()
            if (action.get('type') == 'wake'):
               wol.send_magic_packet(action.get('data'))
            if (action.get('type') == 'ir'):
			   pass
            if (action.get('type') == 'key press'):
               params = urllib.urlencode({'keypresses': action.get('data')})
               keyrequest = urllib2.Request("http://192.168.10.30:8001/command", params)
               response = urllib2.urlopen(keyrequest,timeout=2)
               tempData = response.read()
               response.close()   
               time.sleep(float(action.get('delay')))
            if (action.get('type') == 'command'):
               results = self.handle_command(action.get('data'))
      except:
         raise
         pass
      return results
     
   def get_commands(self):
      XMLtree = ET.parse("commands.xml")
      doc = XMLtree.getroot()
      commands = []
      for elem in doc.findall('command'):
         actions = []
         for action in elem.findall('action'):
            if (action.get('type') == 'serial'):
                tempAction = {'type' : action.get('type'), 'data': action.get('data'), 'delay' : action.get('delay'), 'chassis' : action.get('chassis') }
            else:
                tempAction = {'type' : action.get('type'), 'data': action.get('data'), 'delay' : action.get('delay') }            
            actions.append(tempAction)
         commands.append({ 'name' : elem.get('name'), 'actions' : actions })
      return commands

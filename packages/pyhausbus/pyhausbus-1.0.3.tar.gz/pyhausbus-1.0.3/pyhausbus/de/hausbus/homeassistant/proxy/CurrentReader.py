import logging
from pyhausbus.HausBusCommand import HausBusCommand
from pyhausbus.ABusFeature import *
from pyhausbus.ResultWorker import ResultWorker
import pyhausbus.HausBusUtils as HausBusUtils
from pyhausbus.de.hausbus.homeassistant.proxy.currentReader.params.MConfig import MConfig
from pyhausbus.de.hausbus.homeassistant.proxy.currentReader.data.Configuration import Configuration
from pyhausbus.de.hausbus.homeassistant.proxy.currentReader.data.Current import Current
from pyhausbus.de.hausbus.homeassistant.proxy.currentReader.data.SignalCount import SignalCount
from pyhausbus.de.hausbus.homeassistant.proxy.currentReader.data.Power import Power
from pyhausbus.de.hausbus.homeassistant.proxy.currentReader.params.EErrorCode import EErrorCode

class CurrentReader(ABusFeature):
  CLASS_ID:int = 90

  def __init__ (self,objectId:int):
    super().__init__(objectId)

  @staticmethod
  def create(deviceId:int, instanceId:int):
    return CurrentReader(HausBusUtils.getObjectId(deviceId, 90, instanceId))

  """
  @param config .
  @param impPerKwh Anzahl Signale pro kWh.
  @param startCurrent Startwert Stromverbrauch in Wattstunden.
  @param currentReportInterval Interval in Sekunden nach dem immer der aktuelle Gesamtstromverbrauch gemeldet wird.
  """
  def setConfiguration(self, config:MConfig, impPerKwh:int, startCurrent:int, currentReportInterval:int):
    logging.info("setConfiguration"+" config = "+str(config)+" impPerKwh = "+str(impPerKwh)+" startCurrent = "+str(startCurrent)+" currentReportInterval = "+str(currentReportInterval))
    hbCommand = HausBusCommand(self.objectId, 3, "setConfiguration")
    hbCommand.addByte(config.getValue())
    hbCommand.addWord(impPerKwh)
    hbCommand.addDWord(startCurrent)
    hbCommand.addWord(currentReportInterval)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def getConfiguration(self):
    logging.info("getConfiguration")
    hbCommand = HausBusCommand(self.objectId, 4, "getConfiguration")
    ResultWorker()._setResultInfo(Configuration,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param config .
  @param impPerKwh Anzahl Signale pro kWh.
  @param startCurrent Startwert Stromverbrauch in Wattstunden.
  @param currentReportInterval Interval in Sekunden nach dem immer der aktuelle Gesamtstromverbrauch gemeldet wird.
  """
  def Configuration(self, config:MConfig, impPerKwh:int, startCurrent:int, currentReportInterval:int):
    logging.info("Configuration"+" config = "+str(config)+" impPerKwh = "+str(impPerKwh)+" startCurrent = "+str(startCurrent)+" currentReportInterval = "+str(currentReportInterval))
    hbCommand = HausBusCommand(self.objectId, 129, "Configuration")
    hbCommand.addByte(config.getValue())
    hbCommand.addWord(impPerKwh)
    hbCommand.addDWord(startCurrent)
    hbCommand.addWord(currentReportInterval)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param time Systemzeit des ESP zu Debugzwecken.
  @param signalCount Anzahl gez?hlter S0 Signale seit dem letzten Zur?cksetzen.
  @param power Aktuelle Leistung in Watt.
  @param signalDuration Dauer des gemessenen S0 Signals in ms.
  """
  def evSignal(self, time:int, signalCount:int, power:int, signalDuration:int):
    logging.info("evSignal"+" time = "+str(time)+" signalCount = "+str(signalCount)+" power = "+str(power)+" signalDuration = "+str(signalDuration))
    hbCommand = HausBusCommand(self.objectId, 200, "evSignal")
    hbCommand.addDWord(time)
    hbCommand.addDWord(signalCount)
    hbCommand.addWord(power)
    hbCommand.addDWord(signalDuration)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def getCurrent(self):
    logging.info("getCurrent")
    hbCommand = HausBusCommand(self.objectId, 1, "getCurrent")
    ResultWorker()._setResultInfo(Current,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param current Verbrauchter Strom in Wattstunden.
  """
  def evCurrent(self, current:int):
    logging.info("evCurrent"+" current = "+str(current))
    hbCommand = HausBusCommand(self.objectId, 201, "evCurrent")
    hbCommand.addDWord(current)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param power Aktuelle Leistung in Watt.
  """
  def Power(self, power:int):
    logging.info("Power"+" power = "+str(power))
    hbCommand = HausBusCommand(self.objectId, 130, "Power")
    hbCommand.addWord(power)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param current verbrauchter Strom in Wattstunden.
  """
  def Current(self, current:int):
    logging.info("Current"+" current = "+str(current))
    hbCommand = HausBusCommand(self.objectId, 128, "Current")
    hbCommand.addDWord(current)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def getSignalCount(self):
    logging.info("getSignalCount")
    hbCommand = HausBusCommand(self.objectId, 6, "getSignalCount")
    ResultWorker()._setResultInfo(SignalCount,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param signalCount Anzahl gez?hlter S0 Signale seit dem letzten Zur?cksetzen.
  """
  def SignalCount(self, signalCount:int):
    logging.info("SignalCount"+" signalCount = "+str(signalCount))
    hbCommand = HausBusCommand(self.objectId, 131, "SignalCount")
    hbCommand.addDWord(signalCount)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def clearSignalCount(self):
    logging.info("clearSignalCount")
    hbCommand = HausBusCommand(self.objectId, 7, "clearSignalCount")
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param signalCount .
  """
  def setSignalCount(self, signalCount:int):
    logging.info("setSignalCount"+" signalCount = "+str(signalCount))
    hbCommand = HausBusCommand(self.objectId, 2, "setSignalCount")
    hbCommand.addDWord(signalCount)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def getPower(self):
    logging.info("getPower")
    hbCommand = HausBusCommand(self.objectId, 5, "getPower")
    ResultWorker()._setResultInfo(Power,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def incSignalCount(self):
    logging.info("incSignalCount")
    hbCommand = HausBusCommand(self.objectId, 9, "incSignalCount")
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def decSignalCount(self):
    logging.info("decSignalCount")
    hbCommand = HausBusCommand(self.objectId, 10, "decSignalCount")
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param data .
  @param type .
  """
  def evDebug(self, data:int, type:MConfig):
    logging.info("evDebug"+" data = "+str(data)+" type = "+str(type))
    hbCommand = HausBusCommand(self.objectId, 210, "evDebug")
    hbCommand.addDWord(data)
    hbCommand.addByte(type.getValue())
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param value .
  @param stamp .
  """
  def evInterrupt(self, value:int, stamp:int):
    logging.info("evInterrupt"+" value = "+str(value)+" stamp = "+str(stamp))
    hbCommand = HausBusCommand(self.objectId, 211, "evInterrupt")
    hbCommand.addByte(value)
    hbCommand.addDWord(stamp)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param errorCode .
  """
  def evError(self, errorCode:EErrorCode):
    logging.info("evError"+" errorCode = "+str(errorCode))
    hbCommand = HausBusCommand(self.objectId, 255, "evError")
    hbCommand.addByte(errorCode.value)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")



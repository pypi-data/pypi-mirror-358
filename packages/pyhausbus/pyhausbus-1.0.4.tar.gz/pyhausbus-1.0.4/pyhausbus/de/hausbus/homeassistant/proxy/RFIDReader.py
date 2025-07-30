import logging
from pyhausbus.HausBusCommand import HausBusCommand
from pyhausbus.ABusFeature import *
from pyhausbus.ResultWorker import ResultWorker
import pyhausbus.HausBusUtils as HausBusUtils
from pyhausbus.de.hausbus.homeassistant.proxy.rFIDReader.params.EErrorCode import EErrorCode
from pyhausbus.de.hausbus.homeassistant.proxy.rFIDReader.data.Configuration import Configuration
from pyhausbus.de.hausbus.homeassistant.proxy.rFIDReader.params.EState import EState
from pyhausbus.de.hausbus.homeassistant.proxy.rFIDReader.data.LastData import LastData
from pyhausbus.de.hausbus.homeassistant.proxy.rFIDReader.data.State import State

class RFIDReader(ABusFeature):
  CLASS_ID:int = 43

  def __init__ (self,objectId:int):
    super().__init__(objectId)

  @staticmethod
  def create(deviceId:int, instanceId:int):
    return RFIDReader(HausBusUtils.getObjectId(deviceId, 43, instanceId))

  """
  """
  def evConnected(self):
    logging.info("evConnected")
    hbCommand = HausBusCommand(self.objectId, 200, "evConnected")
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

  """
  """
  def getConfiguration(self):
    logging.info("getConfiguration")
    hbCommand = HausBusCommand(self.objectId, 0, "getConfiguration")
    ResultWorker()._setResultInfo(Configuration,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def setConfiguration(self):
    logging.info("setConfiguration")
    hbCommand = HausBusCommand(self.objectId, 1, "setConfiguration")
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param state State of the RFID-Reader hardware.
  """
  def State(self, state:EState):
    logging.info("State"+" state = "+str(state))
    hbCommand = HausBusCommand(self.objectId, 129, "State")
    hbCommand.addByte(state.value)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param tagID ID of the detected RFID tag.
  """
  def evData(self, tagID:int):
    logging.info("evData"+" tagID = "+str(tagID))
    hbCommand = HausBusCommand(self.objectId, 201, "evData")
    hbCommand.addDWord(tagID)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def getLastData(self):
    logging.info("getLastData")
    hbCommand = HausBusCommand(self.objectId, 3, "getLastData")
    ResultWorker()._setResultInfo(LastData,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param tagID last tagID read successfully.
  """
  def LastData(self, tagID:int):
    logging.info("LastData"+" tagID = "+str(tagID))
    hbCommand = HausBusCommand(self.objectId, 130, "LastData")
    hbCommand.addDWord(tagID)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def Configuration(self):
    logging.info("Configuration")
    hbCommand = HausBusCommand(self.objectId, 128, "Configuration")
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def getState(self):
    logging.info("getState")
    hbCommand = HausBusCommand(self.objectId, 2, "getState")
    ResultWorker()._setResultInfo(State,self.getObjectId())
    hbCommand.send()
    logging.info("returns")



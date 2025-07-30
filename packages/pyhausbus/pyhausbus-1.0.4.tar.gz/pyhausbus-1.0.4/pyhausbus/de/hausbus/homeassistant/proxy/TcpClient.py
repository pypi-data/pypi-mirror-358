import logging
from pyhausbus.HausBusCommand import HausBusCommand
from pyhausbus.ABusFeature import *
from pyhausbus.ResultWorker import ResultWorker
import pyhausbus.HausBusUtils as HausBusUtils
from pyhausbus.de.hausbus.homeassistant.proxy.tcpClient.data.CurrentIp import CurrentIp

class TcpClient(ABusFeature):
  CLASS_ID:int = 91

  def __init__ (self,objectId:int):
    super().__init__(objectId)

  @staticmethod
  def create(deviceId:int, instanceId:int):
    return TcpClient(HausBusUtils.getObjectId(deviceId, 91, instanceId))

  """
  @param IP0 .
  @param IP1 .
  @param IP2 .
  @param IP3 .
  @param port .
  """
  def announceServer(self, IP0:int, IP1:int, IP2:int, IP3:int, port:int):
    logging.info("announceServer"+" IP0 = "+str(IP0)+" IP1 = "+str(IP1)+" IP2 = "+str(IP2)+" IP3 = "+str(IP3)+" port = "+str(port))
    hbCommand = HausBusCommand(self.objectId, 1, "announceServer")
    hbCommand.addByte(IP0)
    hbCommand.addByte(IP1)
    hbCommand.addByte(IP2)
    hbCommand.addByte(IP3)
    hbCommand.addWord(port)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def getCurrentIp(self):
    logging.info("getCurrentIp")
    hbCommand = HausBusCommand(self.objectId, 2, "getCurrentIp")
    ResultWorker()._setResultInfo(CurrentIp,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  @param IP0 .
  @param IP1 .
  @param IP2 .
  @param IP3 .
  """
  def CurrentIp(self, IP0:int, IP1:int, IP2:int, IP3:int):
    logging.info("CurrentIp"+" IP0 = "+str(IP0)+" IP1 = "+str(IP1)+" IP2 = "+str(IP2)+" IP3 = "+str(IP3))
    hbCommand = HausBusCommand(self.objectId, 128, "CurrentIp")
    hbCommand.addByte(IP0)
    hbCommand.addByte(IP1)
    hbCommand.addByte(IP2)
    hbCommand.addByte(IP3)
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")

  """
  """
  def evWhoIsServer(self):
    logging.info("evWhoIsServer")
    hbCommand = HausBusCommand(self.objectId, 200, "evWhoIsServer")
    ResultWorker()._setResultInfo(None,self.getObjectId())
    hbCommand.send()
    logging.info("returns")



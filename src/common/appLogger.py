
import logging
from http.client import HTTPConnection

class appLogger:
  def getLogger(name):

    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(module)s;%(message)s")

    handler = logging.FileHandler(f'/data/logs/{name}.log')        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = True
    
    return logger

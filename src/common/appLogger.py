
import logging

class appLogger:
  def getLogger(name):

    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    logging.basicConfig(filename=f'logs/loger_user_actions{name}.log')

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

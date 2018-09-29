import logging
import _thread

class ConnectionCounter(object):
    connections = 0

    def connectionDied():
        ConnectionCounter.connections -= 1
        logging.info("Connection died, new count: %d" %ConnectionCounter.connections)
        if ConnectionCounter.connections == 0:
            logging.info("No connections left, shutting down.")
            _thread.interrupt_main()
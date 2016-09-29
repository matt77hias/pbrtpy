from logging import basicConfig, getLogger

FORMAT = '%(asctime)-15s  %(message)s'
logger = None

def init_logger():
    global logger
    # Setting the format    
    basicConfig(format=FORMAT)
    # Constructs the logger
    logger = getLogger('rlib')

init_logger()
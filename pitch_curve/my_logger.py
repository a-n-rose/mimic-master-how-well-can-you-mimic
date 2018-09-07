import datetime
import logging.handlers


def get_date():
    time = datetime.datetime.now()
    time_str = "{}y{}m{}d{}h{}m{}s".format(time.year,time.month,time.day,time.hour,time.minute,time.second)
    return(time_str)

def start_logging(log_name):
    #default format: severity:logger name:message
    #documentation: https://docs.python.org/3.6/library/logging.html#logrecord-attributes 
    log_formatterstr='%(levelname)s , %(asctime)s, "%(message)s", %(name)s , %(threadName)s'
    log_formatter = logging.Formatter(log_formatterstr)
    logging.root.setLevel(logging.DEBUG)
    #logging.basicConfig(format=log_formatterstr,
    #                    filename='/tmp/tradinglog.csv',
    #                    level=logging.INFO)
    #for logging infos:
    file_handler_info = logging.handlers.RotatingFileHandler('{}_loginfo.csv'.format(log_name),
                                                                mode='a',
                                                                maxBytes=1.0 * 1e6,
                                                                backupCount=200)
    #file_handler_debug = logging.FileHandler('/tmp/tradinglogdbugger.csv', mode='w')
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.INFO)
    logging.root.addHandler(file_handler_info)
    
    
    #https://docs.python.org/3/library/logging.handlers.html
    #for logging errors:
    file_handler_error = logging.handlers.RotatingFileHandler('{}_logerror.csv'.format(log_name), mode='a',
                                                                maxBytes=1.0 * 1e6,
                                                                backupCount=200)
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.ERROR)
    logging.root.addHandler(file_handler_error)
    
    #for logging infos:
    file_handler_debug = logging.handlers.RotatingFileHandler('{}_logdbugger.csv'.format(log_name),
                                                                mode='a',
                                                                maxBytes=2.0 * 1e6,
                                                                backupCount=200)
    #file_handler_debug = logging.FileHandler('/tmp/tradinglogdbugger.csv', mode='w')
    file_handler_debug.setFormatter(log_formatter)
    file_handler_debug.setLevel(logging.DEBUG)
    logging.root.addHandler(file_handler_debug)
    print("Logging initialized")
    return None

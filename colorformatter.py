import logging

class ColorFormatter(logging.Formatter):
    """ Customizable colors for logging. Uses ANSI escape codes.
    
    Note:   Don't use color logging for files, 
            pass "use_color=True" only for console logs.
        
    Both foreground and background colors can be set at
    the class-level, format_string-level and/or the individual message level.
    
    Won't work on Windows yet, but this is possible with ANSI API usage (ToDo).
    
    Ideas and code gratefully taken from: 
    http://stackoverflow.com/questions/384076/how-can-i-make-the-python-logging-output-to-be-colored
    """
        
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    
    COLORS = {
        'DEBUG'    : BLUE,
        'INFO'     : WHITE,
        'WARNING'  : YELLOW,
        'ERROR'    : RED,
        'CRITICAL' : WHITE,
        
        'RED'      : RED,
        'GREEN'    : GREEN,
        'YELLOW'   : YELLOW,
        'BLUE'     : BLUE,
        'MAGENTA'  : MAGENTA,
        'CYAN'     : CYAN,
        'WHITE'    : WHITE,
        'BLACK'    : BLACK,
    }
    
    RESET_SEQ = "\033[0m"
    BOLD_SEQ  = "\033[1m"
    COLOR_SEQ = "\033[1;%dm"



    def __init__(self, use_color=True, format_string=None):
        if format_string in ['', None]:  
            self.FORMAT = ("[%(asctime)s] [%(levelname)-8s] "
                           "$BOLD[%(message)s]$RESET "
                           "(%(funcname)s:%(lineno)d)")
        else:
            self.FORMAT = format_string
            
        if use_color:
            self.use_color = True
            self.FORMAT = self.FORMAT.replace("$RESET", self.RESET_SEQ).replace("$BOLD", self.BOLD_SEQ)
        else:
            self.use_color = False
            self.FORMAT = self.FORMAT.replace("$RESET", "").replace("$BOLD", "")

        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, self.FORMAT)
        

    def format(self, record):
        levelname = record.levelname
        message   = logging.Formatter.format(self, record)
        
        if self.use_color and levelname in self.COLORS:
            
            color = self.COLOR_SEQ % (30 + self.COLORS[levelname])
            if levelname == "CRITICAL": # set red background for critical messages
                color = color + self.COLOR_SEQ % (40 + self.COLORS['RED'])
            
            message = message.replace("$RESET", self.RESET_SEQ)\
                               .replace("$BOLD",  self.BOLD_SEQ)\
                               .replace("$COLOR", color)
            for k,v in self.COLORS.items():
                message = message.replace("$" + k,    self.COLOR_SEQ % (v+30))\
                                 .replace("$BG" + k,  self.COLOR_SEQ % (v+40))\
                                 .replace("$BG-" + k, self.COLOR_SEQ % (v+40))
                
            
        return message + self.RESET_SEQ # append a sanity RESET_SEQ to every msg 





def main():
    """ Sample consumption of the ColorFormatter class to produce colored logging.
    
    import logging
    from colorformatter import ColorFormatter as ColorFormatter
    
    """
    myformat1 = ('%(asctime)s - %(levelname)-8s - ' 
                 '%(module)s:%(funcName)s:%(lineno)d - %(message)s')
    
    myformat2 = ('$COLOR%(levelname)s -$RESET %(asctime)s - ' 
                 '$BOLD$COLOR%(name)s$RESET - %(message)s')
    
    myformat3 = ('$COLOR%(asctime)s - %(levelname)-8s - ' 
                 '%(module)s:%(funcName)s:%(lineno)d - %(message)s$RESET')
    
    myformat4 = ('$BG-GREEN$COLOR%(asctime)s - %(levelname)-8s - ' 
                 '%(module)s:%(funcName)s:%(lineno)d - %(message)s$RESET')

    logging.basicConfig(
        level = logging.DEBUG,
        format = myformat1,
        filename = 'colorlog.test.log',
        filemode = 'w' 
    )   
    
    console = logging.StreamHandler()
    console.setFormatter(ColorFormatter(use_color=True, format_string=myformat3))
    console.setLevel(logging.DEBUG)    
    logging.getLogger().addHandler(console)

    mylog = logging.getLogger('TESTLOGGER')
    mylog.debug("This is a test debug message")
    mylog.info("This is a test info message")
    mylog.warn("This is a test warn message")
    mylog.error("This is a plain vanilla error message")
    mylog.error("$BG-WHITEThis is a test error message - with white background forced in the message")
    mylog.critical("$BG-GREENThis is a test critical message with green background forced in the message")
    mylog.critical("This is a test critical message with a default red background set in the class")







if __name__ == "__main__":
    main()


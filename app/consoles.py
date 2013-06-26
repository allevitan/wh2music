#For shits and giggles, for those times I type console.log

from __future__ import print_function
import sys
import inspect

class Console(object):
    
    def __init__(self, log=None):
        __old_excepthook = sys.excepthook
        self.__log__ = []
        def console_excepthook(*args):
            if log:
                log.write(self.format(self.__log__))
            __old_excepthook(*args)
        sys.excepthook = console_excepthook
    
    def log(self, *args):
        filename = inspect.getframeinfo(inspect.stack()[1][0]).filename
        line = inspect.stack()[1][2]
        self.__log__.append((filename, line, args))
        print(self.format_line(self.__log__[-1]))
        return '' #So templates don't print it
    
    def format(self, log):
        string = ''
        for line in log:
            string.append(format_line(line) + '\n')
        return string

    def format_line(self, logdata):
        prefix = '%s (%d):' %(logdata[0],logdata[1])
        return prefix + ' ' + ' '.join(logdata[2])

    def __str__(self):
        return '<Console object with %d logs>' %len(self.__log__)

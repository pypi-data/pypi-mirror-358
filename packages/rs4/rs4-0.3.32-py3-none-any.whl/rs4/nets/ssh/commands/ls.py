from . import default
import re
import time
from datetime import datetime

class Result (default.Result):
    def parse_output (self, output):
        lines = output.split ("\n")
        try:
            self.meta ['total'] = int (lines [0].split ()[-1])
        except ValueError:
            pass

        now = time.localtime (time.time ())
        for line in lines [self.meta and 1 or 0:-1]:
            compos = line.split ()
            d = {}
            d ['permission'], _, d ['ouser'], d ['ogroup'], d ['size'], month, day, time_or_year, *name = compos
            d ['name'] = ' '.join (name)
            if time_or_year.find (":") != -1:
                year = now.tm_year
                time_ = time_or_year
                hour, minuates = [ int (e) for e in time_or_year.split (':') ]
            else:
                year = time_or_year
                time_ = "00:00"
                hour, minuates = 0, 0

            mformat = '%m'
            if month.find ('월') != -1:
                month = month [:-1]
            else:
                month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index (month) + 1

            curtime = time.localtime (time.time ())
            if curtime [1:5] < (int (month), int (day), hour, minuates):
                year = curtime.tm_year - 1

            d ['mtime'] = datetime.strptime ('{}/{}/{} {}'.format (month, day, year, time_), '{}/%d/%Y %H:%M'.format (mformat))
            d ['size'] = int (d ['size'])
            self.data.append (d)

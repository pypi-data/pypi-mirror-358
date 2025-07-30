from . import default
import re

RX_spt = re.compile ("^GPU ", re.M)

class Result (default.Result):
    def parse_output (self, outputs):
        for output in RX_spt.split (outputs) [1:]:
            lines = output.split ("\n")
            self.header = lines [0]
            d = {}
            p = ''
            for line in lines[1:-1]:
                try:
                    k, v = line.split (":", 1)
                except ValueError:
                    p = line.strip ()
                    continue
                # print (p + ':' + k.strip (), v.strip ())
                d [p + ':' + k.strip ()] = v.strip ()

            r = {
                'Product Name': d [':Product Name'],
                'GPU': d ['FB Memory Usage:Total'],
                'GPU Util%': d ['Utilization:Gpu'],
                'Temperature': d ['Temperature:GPU Current Temp'],
            }
            try:
                r ['Power'] = d ['Power Readings:Power Draw']
                r ['Power Limit'] =  d ['Power Readings:Power Limit']
            except KeyError:
                r ['Power'] = d ['GPU Power Readings:Power Draw']
                r ['Power Limit'] =  d ['GPU Power Readings:Current Power Limit']

            self.data.append (r)

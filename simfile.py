import re

class SimFile:
    def __init__(self, filename):
        self._kvStore = dict()
        
        lc = 0
        for line in open(filename):
            lc += 1
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue

            fields = line.split('=')
            if len(fields) < 2:
                print 'Error on line %d of input file: key missing assignment.' % lc
                continue

            if len(fields) > 2:
                fields[1] = '='.join(fields[1:])

            key = fields[0].strip()
            value = fields[1].strip()

            if len(value) == 0:
                print 'Error on line %d of input file: assignment missing argument.' % lc
                continue

            if value == 'True':
                self._kvStore[key] = True
                continue

            if value == 'False':
                self._kvStore[key] = False
                continue
            
            try:
                self._kvStore[key] = float(value)
                continue
            except:
                pass

            if re.match('^"[^"]*"$', value):
                self._kvStore[key] = value.strip('"')
                continue

            if value[0] == '[' and value[-1] == ']':
                array1 = [ s.strip() for s in value[1:-1].split(',') ]
                array2 = []
                for v in array1:
                    if v == 'True':
                        array2.append(True)
                    elif v == 'False':
                        array2.append(False)
                    elif re.match('^"[^"]*"$', v):
                        array2.append(v.strip('"'))
                    else:
                        try:
                            array2.append(float(v))
                        except:
                            array2 = None
                            break

                if not array2 is None:
                    self._kvStore[key] = array2
                    continue

            print 'Error on line %d of input file: invalid value (\'%s\')' % (lc, value)

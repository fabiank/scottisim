import re
import numbers

class SimFile:
    def __init__(self, filename):
        _converter = dict()
        
        self.duration = None
        _converter['duration'] = self._set_duration

        self.bins = None
        _converter['bins'] = self._set_bins

        self.spectrum = None
        _converter['spectrum'] = self._set_spectrum

        self.lines = []
        _converter['line'] = self._add_line
        
        self._lc = 0
        for line in open(filename):
            self._lc += 1
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue

            fields = line.split('=')
            if len(fields) < 2:
                print 'Error on line %d of input file: key missing assignment.' % self._lc
                continue

            if len(fields) > 2:
                fields[1] = '='.join(fields[1:])

            key = fields[0].strip()

            if key not in _converter:
                print 'Error on line %d of input file: invalid key "%s"' % (self._lc, key)
                continue

            value = fields[1].strip()

            if len(value) == 0:
                print 'Error on line %d of input file: assignment missing argument.' % self._lc
                continue

            _converter[key](value)

    def _set_duration(self, value):
        self.duration = self._convert_float(value)
        
        if self.duration is None:
            print 'On line %d of input file: invalid duration ("%s")' % (self._lc, value)
            return False

        return True

    def _set_bins(self, value):
        bins = self._convert_array(value)
        if bins is None:
            print 'On line %d of input file: invalid bins definition ("%s")' % (self._lc, value)
            return False

        if len(bins) != 3 or not isinstance(bins[0], int) or not isinstance(bins[1], numbers.Number) or not isinstance(bins[2], numbers.Number):
            print 'On line %d of input file: bins expects the syntax [int, float, float]' % self._lc
            return False

        self.bins = bins
        return True

    def _set_spectrum(self, value):
        self.spectrum = self._convert_string(value)

        if self.spectrum is None:
            print 'On line %d of input file: invalid spectrum file name ("%s")' % (self._lc, value)
            return False

        return True

    def _add_line(self, value):
        line = self._convert_array(value)
        if line is None:
            print 'On line %d of input file: invalid line definition ("%s")' % (self._lc, value)
            return False

        if len(line) != 2 or not isinstance(line[0], numbers.Number) or not isinstance(line[1], numbers.Number):
            print 'On line %d of input file: "line" requires an array of 2 numbers' % self._lc
            return False

        self.lines.append(line)
        return True

    def _convert_int(self, value):
        try:
            return int(value)
        except:
            return None

    def _convert_float(self, value):
        try:
            return float(value)
        except:
            return None

    def _convert_bool(self, value):
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None

    def _convert_string(self, value):
        if re.match('^"[^"]*"$', value):
            return value.strip('"')
        if re.match("^'[^']*'$", value):
            return value.strip("'")
        return None

    def _convert_array(self, value):
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
                        array2.append(int(v))
                        continue
                    except:
                        pass
                    
                    try:
                        array2.append(float(v))
                        continue
                    except:
                        pass
                    
                return None

            return array2

        return None

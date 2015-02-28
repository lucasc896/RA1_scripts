class event_cat(object):
    """data container for event yields"""
    def __init__(self, data = [], pred = [], pred_err = []):
        self._catstring = ''
        self._data = data
        self._pred = pred
        self._pred_err = pred_err
        self.check_list_consistency()
        self._nbins = len(self._data)
        self.check_val_types()

        self._excess = []
        self._excess_err = []
        self.calculate_excess()

    def __str__(self):
        out_str = ">> event_cat object (%s):\n" % self._catstring
        
        out_str += "\t> Data:\n\t\t"
        for n in range(self._nbins):
            out_str += "%s, " % self._data[n]
        
        out_str += "\n\t> Preds:\n\t\t"
        for n in range(self._nbins):
            out_str += "%s+/-%s, " % (self._pred[n], self._pred_err[n])

        return out_str

    def check_list_consistency(self):
        if len(self._data) != len(self._pred):
            print "data and preds arrays different lengths"
            print self._data
            print self._pred
        if len(self._pred) != len(self._pred_err):
            print "preds and pred_errs arrays different lengths"
            print self._pred
            print self._pred_err

    def check_val_types(self):
        """check all val types are consistently floats"""
        
        def convert_val(val = ''):
            if val == "-":
                return 0.
            return float(val)

        for n in range(self._nbins):
            self._data[n] = convert_val(self._data[n])
            self._pred[n] = convert_val(self._pred[n])
            self._pred_err[n] = convert_val(self._pred_err[n])

    def calculate_excess(self):
        for d, p, perr in zip(self._data, self._pred, self._pred_err):
            self._excess.append(d-p)
            self._excess_err.append(perr)

    def get_excess(self):
        return self._excess, self._excess_err
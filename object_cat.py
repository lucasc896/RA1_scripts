class event_cat(object):
    """data container for event yields"""
    def __init__(self, data = [], pred = [], pred_err = [], ht_bins = []):
        self._catstring = ''
        self._data = data
        self._pred = pred
        self._pred_err = pred_err
        self._htbins = ht_bins
        if self._data:
            self._hasData = True
        else:
            self._hasData = False
        self.check_list_consistency()
        self._nbins = len(self._pred)
        self.check_val_types()

        if self._hasData:
            self._excess = []
            self._excess_err = []
            self.calculate_excess()

    def __str__(self):
        out_str = ">> event_cat object (%s):\n" % self._catstring
        
        if self._hasData:
            out_str += "\t> Data:\n\t\t"
            for n in range(len(self._data)):
                out_str += "%s, " % self._data[n]
            
        out_str += "\n\t> Preds:\n\t\t"
        for n in range(self._nbins):
            out_str += "%s+/-%s, " % (self._pred[n], self._pred_err[n])

        return out_str

    def check_list_consistency(self):
        if self._hasData:
            if len(self._data) != len(self._pred):
                print "data and preds arrays different lengths"
                print self._data
                print self._pred
        if len(self._pred) != len(self._pred_err):
            print "preds and pred_errs arrays different lengths"
            print self._pred
            print self._pred_err
        if len(self._htbins) != len(self._pred):
            print "htbins and preds arrays different lengths"
            print self._htbins
            print self._pred

    def pick_htbins(self, htbins_wlist = []):
        pop_list = []
        for n, ht in enumerate(self._htbins):
            if ht not in htbins_wlist:
                pop_list.append(n)

        for p in reversed(pop_list):
            for list in [self._data, self._pred, self._pred_err, self._excess, self._excess_err, self._htbins]:
                if list:
                    list.pop(p)

        self._nbins -= len(pop_list)

    def check_val_types(self):
        """check all val types are consistently floats"""
        
        def convert_val(val = ''):
            if val == "-":
                return 0.
            return float(val)

        for n in range(self._nbins):
            if self._hasData:
                self._data[n] = convert_val(self._data[n])
            self._pred[n] = convert_val(self._pred[n])
            self._pred_err[n] = convert_val(self._pred_err[n])

    def calculate_excess(self):
        for d, p, perr in zip(self._data, self._pred, self._pred_err):
            self._excess.append(d-p)
            self._excess_err.append(perr)

    def the_data(self):
        return self._data

    def the_excess(self):
        return self._excess, self._excess_err

    def the_preds(self):
        return self._pred, self._pred_err

    def the_htbins(self):
        return self._htbins
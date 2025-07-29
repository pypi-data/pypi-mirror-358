

class RollingSeries:
    def __init__(self, data, window, name=None):
        self.data = data
        self.window = window
        self.name = name if name else "rolling_series"

    def mean(self):
        results = []
        for i in range(len(self.data)):
            if i + 1 < self.window:
                results.append(None)
            else:
                window_vals = self.data[i + 1 - self.window: i + 1]
                avg = sum(window_vals) / len(window_vals)
                results.append(avg)
        from .series import Series
        return Series(results, name=f"{self.name}_rolling_mean")
    
    def sum(self):
        results = []
        for i in range(len(self.data)):
            if i + 1 < self.window:
                results.append(None)
            else:
                window_vals = self.data[i + 1 - self.window: i+ 1]
                total = sum(window_vals)
                results.append(total)
        from .series import Series
        return Series(results, name=f"{self.name}_rolling_sum")
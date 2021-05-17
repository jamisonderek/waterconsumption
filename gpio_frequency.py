from gpiozero.input_devices import SmoothedInputDevice
from threading import Event
from statistics import median

class FrequencySignal(SmoothedInputDevice):
    """ This is good for measuring signals in the 1-100Hz range. """
    def __init__(self, pin=None, *, queue_len=9, partial=False, pin_factory=None):
        super().__init__(
            pin, pull_up=False, queue_len=queue_len, 
            sample_wait=0.0, partial=partial, 
            ignore=frozenset({None}), pin_factory=pin_factory
        )
        try:
            self._signal = Event()
            self._signal_rise = None
            self._signal_fall = None
            self.pin.edges = 'both'
            self.pin.bounce = None
            self.pin.when_changed = self._signal_changed
            self._queue.start()
        except:
            self.close()
            raise        

    def _signal_changed(self, ticks, level):
        if not self._signal.is_set():
            if level:
                self._signal_rise = ticks
            else:
                self._signal_fall = ticks

        if self._signal_fall is not None and self._signal_rise is not None and self.pin_factory.ticks_diff(self._signal_fall, self._signal_rise) != 0: 
            self._signal.set()

    def _measure_pulse_duration(self):
        self._signal.clear()
        self._signal_fall = None
        self._signal_rise = None
        if self._signal.wait(0.3):
            if self._signal_fall is not None and self._signal_rise is not None:
                duration = 2 * self.pin_factory.ticks_diff(self._signal_fall, self._signal_rise)
                duration = abs(duration)
                if (duration == 0.0):
                    print ("The durations: {0},{1} = {2}".format(self._signal_fall, self._signal_rise, duration))
                return duration
        return 0.0

    def measure_frequency(self):
        samples=[]
        for sample in range(5):
            samples.append(self._measure_pulse_duration())
        duration = median(samples)
        if (duration == 0.0):
            return 0
        else:
            return 1.0/duration
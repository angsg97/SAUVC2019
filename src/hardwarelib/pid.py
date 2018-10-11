import threading
import time


class PIDController(threading.Thread):

    def __init__(self,
                 input_func, output_func,
                 const_p, const_i, const_d,
                 input_attach=None, output_attach=None,
                 minimal_delay_ms=100,
                 simulated=False):
        threading.Thread.__init__(self)
        self.input_func = input_func
        self.output_func = output_func
        self.input_attach = input_attach
        self.output_attach = output_attach
        self.setPID(const_p, const_i, const_d)
        self.stopped = False
        self.minimal_delay_ms = minimal_delay_ms
        self.simulated = simulated

    def setPID(self, const_p, const_i, const_d):
        self.const_p = const_p
        self.const_i = const_i
        self.const_d = const_d

    def stop(self):
        self.stopped = True

    def get_error(self):
        return self.input_func() if self.input_attach is None \
            else self.input_func(self.input_attach)

    def output(self, value):
        return self.output_func(value) if self.output_attach is None \
            else self.output_func(self.output_attach, value)

    def run(self):
        self.stopped = False
        error_i = 0
        error_d = 0
        error_last = self.get_error()
        last_time = time.time()
        while not self.stopped:
            if not self.simulated:
                time.sleep(self.minimal_delay_ms/1000)
                time_interval = time.time() - last_time
            else:
                time_interval = self.minimal_delay_ms/1000
            last_time = time.time()

            error_now = self.get_error()
            error_i += error_now * time_interval
            error_d = (error_now - error_last) / time_interval
            error_last = error_now

            self.output(error_now * self.const_p + error_i * self.const_i + error_d * self.const_d)

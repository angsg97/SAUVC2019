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
        self.enabled = False
        self.just_resumed = True

    def setPID(self, const_p, const_i, const_d):
        self.const_p = const_p
        self.const_i = const_i
        self.const_d = const_d

    def stop(self):
        self.stopped = True

    def resume(self):
        if not self.enabled:
            self.enabled = True
            self.just_resumed = True

    def pause(self):
        self.enabled = False

    def __get_error(self):
        return self.input_func() if self.input_attach is None \
            else self.input_func(self.input_attach)

    def __output(self, value):
        return self.output_func(value) if self.output_attach is None \
            else self.output_func(self.output_attach, value)

    def run(self):
        self.enabled = True
        self.stopped = False
        error_i = 0
        error_d = 0
        error_last = self.__get_error()
        last_time = 0
        while not self.stopped:
            if self.enabled:
                error_now = self.__get_error()

                time_interval = self.minimal_delay_ms/1000 if self.simulated else time.time() - \
                    last_time
                last_time = time.time()

                if self.just_resumed:
                    error_i = 0
                    error_d = 0
                    self.just_resumed = False

                else:
                    error_i += error_now * time_interval
                    error_d = (error_now - error_last) / time_interval
                error_last = error_now

                self.__output(error_now * self.const_p + error_i *
                              self.const_i + error_d * self.const_d)

                if not self.simulated:
                    time.sleep(self.minimal_delay_ms/1000)

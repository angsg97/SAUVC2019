""" Contains implements of pid algorithm """
import threading
import time


class PIDController(threading.Thread):
    """ a standard pid controller """
    def __init__(self,
                 input_func, output_func,
                 const_p, const_i, const_d, const_max_i=None,
                 reset_i_when_crossing=False,
                 input_attach=None, output_attach=None,
                 minimal_delay_ms=100,
                 simulated=False):
        """ Inits the PID controller
        Args:
            input_func: a method in the form of f() -> float
                that returns the current error of the system
            output_func: a method in the form of f(float)
                that take a value in [-1, 1] and outputs to the system
            const_p: Kp
            const_i: Ki
            const_d: Kd
            const_max_i: maximum value for integral term(optional, set to None to disable it)
            input_attach: attachment for input_func, if the value is set,
                it will be the first argument for input_func,
                input_func should be f(attach) -> float
            output_attach: attachment for output_func, if the value is set,
                it will be the first argument for output_func,
                output_func should be f(attach, output_value)
            minimal_delay_ms: expected delay for the pid loop,
                the actual delay depends on input_func() and output_func()
            simulated: if set to True, there will be no actual delay
        """
        threading.Thread.__init__(self)
        self.input_func = input_func
        self.output_func = output_func
        self.input_attach = input_attach
        self.output_attach = output_attach
        self.setPID(const_p, const_i, const_d, const_max_i)
        self.reset_i_when_crossing = reset_i_when_crossing
        self.stopped = False
        self.minimal_delay_ms = minimal_delay_ms
        self.simulated = simulated
        self.enabled = False
        self.just_resumed = True

    def setPID(self, const_p, const_i, const_d, const_max_i=None):
        """ Set PID parameters to new one """
        self.const_p = const_p
        self.const_i = const_i
        self.const_d = const_d
        self.const_max_i = const_max_i

    def stop(self):
        """ Stop the controller """
        self.stopped = True

    def resume(self):
        """ Resume the controller """
        if not self.enabled:
            self.enabled = True
            self.just_resumed = True

    def pause(self):
        """ Pause the controller """
        self.enabled = False

    def __get_error(self):
        """ get current error from input_func() """
        return self.input_func() if self.input_attach is None \
            else self.input_func(self.input_attach)

    def __output(self, value):
        """ output the result of PID to the system """
        return self.output_func(value) if self.output_attach is None \
            else self.output_func(self.output_attach, value)

    def run(self):
        """ main body of the controller (use start() to launch it in a new thread) """
        self.enabled = True
        self.stopped = False
        error_i = 0
        error_d = 0
        error_last = self.__get_error()
        last_time = 0
        while not self.stopped:
            if self.enabled:
                error_now = self.__get_error()
                if error_now is None:
                    continue

                time_interval = self.minimal_delay_ms/1000 if self.simulated else time.time() - \
                    last_time
                last_time = time.time()

                # in case pid is disabled in get_error method
                if not self.enabled:
                    continue

                # set integral term and derivative term when the controller just begin of resume
                if self.just_resumed:
                    error_i = 0
                    error_d = 0
                    self.just_resumed = False

                else:
                    # calculate integral term
                    error_i += error_now * time_interval
                    # when error changes its sign
                    # reset integral term if reset_i_when_crossing is set
                    if self.reset_i_when_crossing and error_now * error_last < 0:
                        error_i = 0
                    # Apply windup limit to limit the size of the integral term
                    if not self.const_max_i is None:
                        error_i = min(max(error_i, 0 - self.const_max_i), self.const_max_i)

                    # calculate derivative term
                    error_d = (error_now - error_last) / time_interval
                
                error_last = error_now # save current error for derivative term next time

                self.__output(error_now * self.const_p + error_i *
                              self.const_i + error_d * self.const_d)

                if not self.simulated:
                    time.sleep(self.minimal_delay_ms/1000)
            else:
                time.sleep(self.minimal_delay_ms/1000)

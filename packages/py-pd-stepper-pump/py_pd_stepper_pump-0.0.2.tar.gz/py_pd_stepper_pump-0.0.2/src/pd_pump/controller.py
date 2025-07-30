from pd_stepper.controller_serial import ControllerSerial
from pd_stepper.serial_port import SerialPort
from .parameters import Parameters

class ControllerPump(ControllerSerial):
    def __init__(self, port: SerialPort):
        super().__init__(port)
        self.__serial_port = port
        self.params = Parameters()

    def pump_ml(self, ml):
        self.__serial_port.communicate(f'setTarget:{self.params.steps_per_ml_pump * ml}')

    def suck_ml(self, ml):
        self.__serial_port.communicate(f'setTarget:{self.params.steps_per_ml_suck * ml}')

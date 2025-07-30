from pd_stepper.pd_stepper import PDStepper
from pd_stepper.serial_port import SerialPort
from .controller import ControllerPump

class Pump(PDStepper):
    def __init__(self, port: str):
        super().__init__(port)
        self.__serial_port = SerialPort(port)
        self.controller = ControllerPump(self.__serial_port)
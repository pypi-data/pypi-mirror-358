from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage


@dataclass
class AnalogDataPayload:
        # The voltage at the output of the ADC channel 0.
    AnalogInput0: int
        # The quadrature counter value on Port 2
    Encoder: int
        # The voltage at the output of the ADC channel 1.
    AnalogInput1: int

@dataclass
class RgbAllPayload:
        # The intensity of the green channel in the RGB0 LED.
    Green0: int
        # The intensity of the red channel in the RGB0 LED.
    Red0: int
        # The intensity of the blue channel in the RGB0 LED.
    Blue0: int
        # The intensity of the green channel in the RGB1 LED.
    Green1: int
        # The intensity of the red channel in the RGB1 LED.
    Red1: int
        # The intensity of the blue channel in the RGB1 LED.
    Blue1: int

@dataclass
class RgbPayload:
        # The intensity of the green channel in the RGB LED.
    Green: int
        # The intensity of the red channel in the RGB LED.
    Red: int
        # The intensity of the blue channel in the RGB LED.
    Blue: int


class DigitalInputs(IntFlag):
    """
    Specifies the state of port digital input lines.

    Attributes
    ----------
    DI_PORT0 : int
        TODO
    DI_PORT1 : int
        TODO
    DI_PORT2 : int
        TODO
    DI3 : int
        TODO
    """

    NONE = 0x0
    DI_PORT0 = 0x1
    DI_PORT1 = 0x2
    DI_PORT2 = 0x4
    DI3 = 0x8


class DigitalOutputs(IntFlag):
    """
    Specifies the state of port digital output lines.

    Attributes
    ----------
    DO_PORT0 : int
        TODO
    DO_PORT1 : int
        TODO
    DO_PORT2 : int
        TODO
    SUPPLY_PORT0 : int
        TODO
    SUPPLY_PORT1 : int
        TODO
    SUPPLY_PORT2 : int
        TODO
    LED0 : int
        TODO
    LED1 : int
        TODO
    RGB0 : int
        TODO
    RGB1 : int
        TODO
    DO0 : int
        TODO
    DO1 : int
        TODO
    DO2 : int
        TODO
    DO3 : int
        TODO
    """

    NONE = 0x0
    DO_PORT0 = 0x1
    DO_PORT1 = 0x2
    DO_PORT2 = 0x4
    SUPPLY_PORT0 = 0x8
    SUPPLY_PORT1 = 0x10
    SUPPLY_PORT2 = 0x20
    LED0 = 0x40
    LED1 = 0x80
    RGB0 = 0x100
    RGB1 = 0x200
    DO0 = 0x400
    DO1 = 0x800
    DO2 = 0x1000
    DO3 = 0x2000


class PortDigitalIOS(IntFlag):
    """
    Specifies the state of the port DIO lines.

    Attributes
    ----------
    DIO0 : int
        TODO
    DIO1 : int
        TODO
    DIO2 : int
        TODO
    """

    NONE = 0x0
    DIO0 = 0x1
    DIO1 = 0x2
    DIO2 = 0x4


class PwmOutputs(IntFlag):
    """
    Specifies the state of PWM output lines.

    Attributes
    ----------
    PWM_DO0 : int
        TODO
    PWM_DO1 : int
        TODO
    PWM_DO2 : int
        TODO
    PWM_DO3 : int
        TODO
    """

    NONE = 0x0
    PWM_DO0 = 0x1
    PWM_DO1 = 0x2
    PWM_DO2 = 0x4
    PWM_DO3 = 0x8


class Events(IntFlag):
    """
    Specifies the active events in the device.

    Attributes
    ----------
    PORT_DI : int
        TODO
    PORT_DIO : int
        TODO
    ANALOG_DATA : int
        TODO
    CAMERA0 : int
        TODO
    CAMERA1 : int
        TODO
    """

    NONE = 0x0
    PORT_DI = 0x1
    PORT_DIO = 0x2
    ANALOG_DATA = 0x4
    CAMERA0 = 0x8
    CAMERA1 = 0x10


class CameraOutputs(IntFlag):
    """
    Specifies camera output enable bits.

    Attributes
    ----------
    CAMERA_OUTPUT0 : int
        TODO
    CAMERA_OUTPUT1 : int
        TODO
    """

    NONE = 0x0
    CAMERA_OUTPUT0 = 0x1
    CAMERA_OUTPUT1 = 0x2


class ServoOutputs(IntFlag):
    """
    Specifies servo output enable bits.

    Attributes
    ----------
    SERVO_OUTPUT2 : int
        TODO
    SERVO_OUTPUT3 : int
        TODO
    """

    NONE = 0x0
    SERVO_OUTPUT2 = 0x4
    SERVO_OUTPUT3 = 0x8


class EncoderInputs(IntFlag):
    """
    Specifies quadrature counter enable bits.

    Attributes
    ----------
    ENCODER_PORT2 : int
        TODO
    """

    NONE = 0x0
    ENCODER_PORT2 = 0x4


class FrameAcquired(IntFlag):
    """
    Specifies that camera frame was acquired.

    Attributes
    ----------
    FRAME_ACQUIRED : int
        TODO
    """

    NONE = 0x0
    FRAME_ACQUIRED = 0x1


class MimicOutput(Enum):
    """
    Specifies the target IO on which to mimic the specified register.

    Attributes
    ----------
    NONE : int
        TODO
    DIO0 : int
        TODO
    DIO1 : int
        TODO
    DIO2 : int
        TODO
    DO0 : int
        TODO
    DO1 : int
        TODO
    DO2 : int
        TODO
    DO3 : int
        TODO
    """

    NONE = 0
    DIO0 = 1
    DIO1 = 2
    DIO2 = 3
    DO0 = 4
    DO1 = 5
    DO2 = 6
    DO3 = 7


class EncoderModeConfig(Enum):
    """
    Specifies the type of reading made from the quadrature encoder.

    Attributes
    ----------
    POSITION : int
        TODO
    DISPLACEMENT : int
        TODO
    """

    POSITION = 0
    DISPLACEMENT = 1


# All available registers for the device as a Enum
class BehaviorRegisters(Enum):
    """Enum for all available registers in the Behavior device.

    Attributes
    ----------
    DIGITAL_INPUT_STATE : int
        Reflects the state of DI digital lines of each Port
    RESERVED0 : int
        Reserved for future use
    OUTPUT_SET : int
        Set the specified digital output lines.
    OUTPUT_CLEAR : int
        Clear the specified digital output lines
    OUTPUT_TOGGLE : int
        Toggle the specified digital output lines
    OUTPUT_STATE : int
        Write the state of all digital output lines
    PORT_DIO_SET : int
        Set the specified port DIO lines
    PORT_DIO_CLEAR : int
        Clear the specified port DIO lines
    PORT_DIO_TOGGLE : int
        Toggle the specified port DIO lines
    PORT_DIO_STATE : int
        Write the state of all port DIO lines
    PORT_DIO_DIRECTION : int
        Specifies which of the port DIO lines are outputs
    PORT_DIO_STATE_EVENT : int
        Specifies the state of the port DIO lines on a line change
    ANALOG_DATA : int
        Voltage at the ADC input and encoder value on Port 2
    OUTPUT_PULSE_ENABLE : int
        Enables the pulse function for the specified output lines
    PULSE_DO_PORT0 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_DO_PORT1 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_DO_PORT2 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_SUPPLY_PORT0 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_SUPPLY_PORT1 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_SUPPLY_PORT2 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_LED0 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_LED1 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_RGB0 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_RGB1 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_DO0 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_DO1 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_DO2 : int
        Specifies the duration of the output pulse in milliseconds.
    PULSE_DO3 : int
        Specifies the duration of the output pulse in milliseconds.
    PWM_FREQUENCY_DO0 : int
        Specifies the frequency of the PWM at DO0.
    PWM_FREQUENCY_DO1 : int
        Specifies the frequency of the PWM at DO1.
    PWM_FREQUENCY_DO2 : int
        Specifies the frequency of the PWM at DO2.
    PWM_FREQUENCY_DO3 : int
        Specifies the frequency of the PWM at DO3.
    PWM_DUTY_CYCLE_DO0 : int
        Specifies the duty cycle of the PWM at DO0.
    PWM_DUTY_CYCLE_DO1 : int
        Specifies the duty cycle of the PWM at DO1.
    PWM_DUTY_CYCLE_DO2 : int
        Specifies the duty cycle of the PWM at DO2.
    PWM_DUTY_CYCLE_DO3 : int
        Specifies the duty cycle of the PWM at DO3.
    PWM_START : int
        Starts the PWM on the selected output lines.
    PWM_STOP : int
        Stops the PWM on the selected output lines.
    RGB_ALL : int
        Specifies the state of all RGB LED channels.
    RGB0 : int
        Specifies the state of the RGB0 LED channels.
    RGB1 : int
        Specifies the state of the RGB1 LED channels.
    LED0_CURRENT : int
        Specifies the configuration of current to drive LED 0.
    LED1_CURRENT : int
        Specifies the configuration of current to drive LED 1.
    LED0_MAX_CURRENT : int
        Specifies the configuration of current to drive LED 0.
    LED1_MAX_CURRENT : int
        Specifies the configuration of current to drive LED 1.
    EVENT_ENABLE : int
        Specifies the active events in the device.
    START_CAMERAS : int
        Specifies the camera outputs to enable in the device.
    STOP_CAMERAS : int
        Specifies the camera outputs to disable in the device. An event will be issued when the trigger signal is actually stopped being generated.
    ENABLE_SERVOS : int
        Specifies the servo outputs to enable in the device.
    DISABLE_SERVOS : int
        Specifies the servo outputs to disable in the device.
    ENABLE_ENCODERS : int
        Specifies the port quadrature counters to enable in the device.
    ENCODER_MODE : int
        Configures the operation mode of the quadrature encoders.
    RESERVED2 : int
        Reserved for future use
    RESERVED3 : int
        Reserved for future use
    RESERVED4 : int
        Reserved for future use
    RESERVED5 : int
        Reserved for future use
    RESERVED6 : int
        Reserved for future use
    RESERVED7 : int
        Reserved for future use
    RESERVED8 : int
        Reserved for future use
    RESERVED9 : int
        Reserved for future use
    CAMERA0_FRAME : int
        Specifies that a frame was acquired on camera 0.
    CAMERA0_FREQUENCY : int
        Specifies the trigger frequency for camera 0.
    CAMERA1_FRAME : int
        Specifies that a frame was acquired on camera 1.
    CAMERA1_FREQUENCY : int
        Specifies the trigger frequency for camera 1.
    RESERVED10 : int
        Reserved for future use
    RESERVED11 : int
        Reserved for future use
    RESERVED12 : int
        Reserved for future use
    RESERVED13 : int
        Reserved for future use
    SERVO_MOTOR2_PERIOD : int
        Specifies the period of the servo motor in DO2, in microseconds.
    SERVO_MOTOR2_PULSE : int
        Specifies the pulse of the servo motor in DO2, in microseconds.
    SERVO_MOTOR3_PERIOD : int
        Specifies the period of the servo motor in DO3, in microseconds.
    SERVO_MOTOR3_PULSE : int
        Specifies the pulse of the servo motor in DO3, in microseconds.
    RESERVED14 : int
        Reserved for future use
    RESERVED15 : int
        Reserved for future use
    RESERVED16 : int
        Reserved for future use
    RESERVED17 : int
        Reserved for future use
    ENCODER_RESET : int
        Reset the counter of the specified encoders to zero.
    RESERVED18 : int
        Reserved for future use
    ENABLE_SERIAL_TIMESTAMP : int
        Enables the timestamp for serial TX.
    MIMIC_PORT0_IR : int
        Specifies the digital output to mimic the Port 0 IR state.
    MIMIC_PORT1_IR : int
        Specifies the digital output to mimic the Port 1 IR state.
    MIMIC_PORT2_IR : int
        Specifies the digital output to mimic the Port 2 IR state.
    RESERVED20 : int
        Reserved for future use
    RESERVED21 : int
        Reserved for future use
    RESERVED22 : int
        Reserved for future use
    MIMIC_PORT0_VALVE : int
        Specifies the digital output to mimic the Port 0 valve state.
    MIMIC_PORT1_VALVE : int
        Specifies the digital output to mimic the Port 1 valve state.
    MIMIC_PORT2_VALVE : int
        Specifies the digital output to mimic the Port 2 valve state.
    RESERVED23 : int
        Reserved for future use
    RESERVED24 : int
        Reserved for future use
    POKE_INPUT_FILTER : int
        Specifies the low pass filter time value for poke inputs, in ms.
    """
    DIGITAL_INPUT_STATE = 32
    RESERVED0 = 33
    OUTPUT_SET = 34
    OUTPUT_CLEAR = 35
    OUTPUT_TOGGLE = 36
    OUTPUT_STATE = 37
    PORT_DIO_SET = 38
    PORT_DIO_CLEAR = 39
    PORT_DIO_TOGGLE = 40
    PORT_DIO_STATE = 41
    PORT_DIO_DIRECTION = 42
    PORT_DIO_STATE_EVENT = 43
    ANALOG_DATA = 44
    OUTPUT_PULSE_ENABLE = 45
    PULSE_DO_PORT0 = 46
    PULSE_DO_PORT1 = 47
    PULSE_DO_PORT2 = 48
    PULSE_SUPPLY_PORT0 = 49
    PULSE_SUPPLY_PORT1 = 50
    PULSE_SUPPLY_PORT2 = 51
    PULSE_LED0 = 52
    PULSE_LED1 = 53
    PULSE_RGB0 = 54
    PULSE_RGB1 = 55
    PULSE_DO0 = 56
    PULSE_DO1 = 57
    PULSE_DO2 = 58
    PULSE_DO3 = 59
    PWM_FREQUENCY_DO0 = 60
    PWM_FREQUENCY_DO1 = 61
    PWM_FREQUENCY_DO2 = 62
    PWM_FREQUENCY_DO3 = 63
    PWM_DUTY_CYCLE_DO0 = 64
    PWM_DUTY_CYCLE_DO1 = 65
    PWM_DUTY_CYCLE_DO2 = 66
    PWM_DUTY_CYCLE_DO3 = 67
    PWM_START = 68
    PWM_STOP = 69
    RGB_ALL = 70
    RGB0 = 71
    RGB1 = 72
    LED0_CURRENT = 73
    LED1_CURRENT = 74
    LED0_MAX_CURRENT = 75
    LED1_MAX_CURRENT = 76
    EVENT_ENABLE = 77
    START_CAMERAS = 78
    STOP_CAMERAS = 79
    ENABLE_SERVOS = 80
    DISABLE_SERVOS = 81
    ENABLE_ENCODERS = 82
    ENCODER_MODE = 83
    RESERVED2 = 84
    RESERVED3 = 85
    RESERVED4 = 86
    RESERVED5 = 87
    RESERVED6 = 88
    RESERVED7 = 89
    RESERVED8 = 90
    RESERVED9 = 91
    CAMERA0_FRAME = 92
    CAMERA0_FREQUENCY = 93
    CAMERA1_FRAME = 94
    CAMERA1_FREQUENCY = 95
    RESERVED10 = 96
    RESERVED11 = 97
    RESERVED12 = 98
    RESERVED13 = 99
    SERVO_MOTOR2_PERIOD = 100
    SERVO_MOTOR2_PULSE = 101
    SERVO_MOTOR3_PERIOD = 102
    SERVO_MOTOR3_PULSE = 103
    RESERVED14 = 104
    RESERVED15 = 105
    RESERVED16 = 106
    RESERVED17 = 107
    ENCODER_RESET = 108
    RESERVED18 = 109
    ENABLE_SERIAL_TIMESTAMP = 110
    MIMIC_PORT0_IR = 111
    MIMIC_PORT1_IR = 112
    MIMIC_PORT2_IR = 113
    RESERVED20 = 114
    RESERVED21 = 115
    RESERVED22 = 116
    MIMIC_PORT0_VALVE = 117
    MIMIC_PORT1_VALVE = 118
    MIMIC_PORT2_VALVE = 119
    RESERVED23 = 120
    RESERVED24 = 121
    POKE_INPUT_FILTER = 122


class Behavior(Device):
    """
    Behavior class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1216:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1216}, got {self.WHO_AM_I}")

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputSet register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputSet", reply.error_message)

        return reply.payload

    def write_output_set(self, value: DigitalOutputs):
        """
        Writes a value to the OutputSet register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputSet register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputSet", reply.error_message)
    def read_output_clear(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputClear register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputClear register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputClear", reply.error_message)

        return reply.payload

    def write_output_clear(self, value: DigitalOutputs):
        """
        Writes a value to the OutputClear register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputClear register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputClear", reply.error_message)
    def read_output_toggle(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputToggle register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputToggle register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputToggle", reply.error_message)

        return reply.payload

    def write_output_toggle(self, value: DigitalOutputs):
        """
        Writes a value to the OutputToggle register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputToggle register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputToggle", reply.error_message)
    def read_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputState register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputState", reply.error_message)

        return reply.payload

    def write_output_state(self, value: DigitalOutputs):
        """
        Writes a value to the OutputState register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputState register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputState", reply.error_message)
    def read_port_dio_set(self) -> PortDigitalIOS:
        """
        Reads the contents of the PortDIOSet register.

        Returns
        -------
        PortDigitalIOS
            Value read from the PortDIOSet register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PortDIOSet", reply.error_message)

        return reply.payload

    def write_port_dio_set(self, value: PortDigitalIOS):
        """
        Writes a value to the PortDIOSet register.

        Parameters
        ----------
        value : PortDigitalIOS
            Value to write to the PortDIOSet register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PortDIOSet", reply.error_message)
    def read_port_dio_clear(self) -> PortDigitalIOS:
        """
        Reads the contents of the PortDIOClear register.

        Returns
        -------
        PortDigitalIOS
            Value read from the PortDIOClear register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PortDIOClear", reply.error_message)

        return reply.payload

    def write_port_dio_clear(self, value: PortDigitalIOS):
        """
        Writes a value to the PortDIOClear register.

        Parameters
        ----------
        value : PortDigitalIOS
            Value to write to the PortDIOClear register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PortDIOClear", reply.error_message)
    def read_port_dio_toggle(self) -> PortDigitalIOS:
        """
        Reads the contents of the PortDIOToggle register.

        Returns
        -------
        PortDigitalIOS
            Value read from the PortDIOToggle register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PortDIOToggle", reply.error_message)

        return reply.payload

    def write_port_dio_toggle(self, value: PortDigitalIOS):
        """
        Writes a value to the PortDIOToggle register.

        Parameters
        ----------
        value : PortDigitalIOS
            Value to write to the PortDIOToggle register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PortDIOToggle", reply.error_message)
    def read_port_dio_state(self) -> PortDigitalIOS:
        """
        Reads the contents of the PortDIOState register.

        Returns
        -------
        PortDigitalIOS
            Value read from the PortDIOState register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PortDIOState", reply.error_message)

        return reply.payload

    def write_port_dio_state(self, value: PortDigitalIOS):
        """
        Writes a value to the PortDIOState register.

        Parameters
        ----------
        value : PortDigitalIOS
            Value to write to the PortDIOState register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PortDIOState", reply.error_message)
    def read_port_dio_direction(self) -> PortDigitalIOS:
        """
        Reads the contents of the PortDIODirection register.

        Returns
        -------
        PortDigitalIOS
            Value read from the PortDIODirection register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PortDIODirection", reply.error_message)

        return reply.payload

    def write_port_dio_direction(self, value: PortDigitalIOS):
        """
        Writes a value to the PortDIODirection register.

        Parameters
        ----------
        value : PortDigitalIOS
            Value to write to the PortDIODirection register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PortDIODirection", reply.error_message)
    def read_port_dio_state_event(self) -> PortDigitalIOS:
        """
        Reads the contents of the PortDIOStateEvent register.

        Returns
        -------
        PortDigitalIOS
            Value read from the PortDIOStateEvent register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PortDIOStateEvent", reply.error_message)

        return reply.payload

    def read_analog_data(self) -> AnalogDataPayload:
        """
        Reads the contents of the AnalogData register.

        Returns
        -------
        AnalogDataPayload
            Value read from the AnalogData register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply.is_error:
            raise HarpReadException("AnalogData", reply.error_message)

        return reply.payload

    def read_output_pulse_enable(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputPulseEnable register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputPulseEnable register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("OutputPulseEnable", reply.error_message)

        return reply.payload

    def write_output_pulse_enable(self, value: DigitalOutputs):
        """
        Writes a value to the OutputPulseEnable register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputPulseEnable register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("OutputPulseEnable", reply.error_message)
    def read_pulse_do_port0(self) -> int:
        """
        Reads the contents of the PulseDOPort0 register.

        Returns
        -------
        int
            Value read from the PulseDOPort0 register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseDOPort0", reply.error_message)

        return reply.payload

    def write_pulse_do_port0(self, value: int):
        """
        Writes a value to the PulseDOPort0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDOPort0 register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseDOPort0", reply.error_message)
    def read_pulse_do_port1(self) -> int:
        """
        Reads the contents of the PulseDOPort1 register.

        Returns
        -------
        int
            Value read from the PulseDOPort1 register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseDOPort1", reply.error_message)

        return reply.payload

    def write_pulse_do_port1(self, value: int):
        """
        Writes a value to the PulseDOPort1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDOPort1 register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseDOPort1", reply.error_message)
    def read_pulse_do_port2(self) -> int:
        """
        Reads the contents of the PulseDOPort2 register.

        Returns
        -------
        int
            Value read from the PulseDOPort2 register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseDOPort2", reply.error_message)

        return reply.payload

    def write_pulse_do_port2(self, value: int):
        """
        Writes a value to the PulseDOPort2 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDOPort2 register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseDOPort2", reply.error_message)
    def read_pulse_supply_port0(self) -> int:
        """
        Reads the contents of the PulseSupplyPort0 register.

        Returns
        -------
        int
            Value read from the PulseSupplyPort0 register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseSupplyPort0", reply.error_message)

        return reply.payload

    def write_pulse_supply_port0(self, value: int):
        """
        Writes a value to the PulseSupplyPort0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseSupplyPort0 register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseSupplyPort0", reply.error_message)
    def read_pulse_supply_port1(self) -> int:
        """
        Reads the contents of the PulseSupplyPort1 register.

        Returns
        -------
        int
            Value read from the PulseSupplyPort1 register.
        """
        address = 50
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseSupplyPort1", reply.error_message)

        return reply.payload

    def write_pulse_supply_port1(self, value: int):
        """
        Writes a value to the PulseSupplyPort1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseSupplyPort1 register.
        """
        address = 50
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseSupplyPort1", reply.error_message)
    def read_pulse_supply_port2(self) -> int:
        """
        Reads the contents of the PulseSupplyPort2 register.

        Returns
        -------
        int
            Value read from the PulseSupplyPort2 register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseSupplyPort2", reply.error_message)

        return reply.payload

    def write_pulse_supply_port2(self, value: int):
        """
        Writes a value to the PulseSupplyPort2 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseSupplyPort2 register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseSupplyPort2", reply.error_message)
    def read_pulse_led0(self) -> int:
        """
        Reads the contents of the PulseLed0 register.

        Returns
        -------
        int
            Value read from the PulseLed0 register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseLed0", reply.error_message)

        return reply.payload

    def write_pulse_led0(self, value: int):
        """
        Writes a value to the PulseLed0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseLed0 register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseLed0", reply.error_message)
    def read_pulse_led1(self) -> int:
        """
        Reads the contents of the PulseLed1 register.

        Returns
        -------
        int
            Value read from the PulseLed1 register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseLed1", reply.error_message)

        return reply.payload

    def write_pulse_led1(self, value: int):
        """
        Writes a value to the PulseLed1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseLed1 register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseLed1", reply.error_message)
    def read_pulse_rgb0(self) -> int:
        """
        Reads the contents of the PulseRgb0 register.

        Returns
        -------
        int
            Value read from the PulseRgb0 register.
        """
        address = 54
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseRgb0", reply.error_message)

        return reply.payload

    def write_pulse_rgb0(self, value: int):
        """
        Writes a value to the PulseRgb0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseRgb0 register.
        """
        address = 54
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseRgb0", reply.error_message)
    def read_pulse_rgb1(self) -> int:
        """
        Reads the contents of the PulseRgb1 register.

        Returns
        -------
        int
            Value read from the PulseRgb1 register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseRgb1", reply.error_message)

        return reply.payload

    def write_pulse_rgb1(self, value: int):
        """
        Writes a value to the PulseRgb1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseRgb1 register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseRgb1", reply.error_message)
    def read_pulse_do0(self) -> int:
        """
        Reads the contents of the PulseDO0 register.

        Returns
        -------
        int
            Value read from the PulseDO0 register.
        """
        address = 56
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseDO0", reply.error_message)

        return reply.payload

    def write_pulse_do0(self, value: int):
        """
        Writes a value to the PulseDO0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDO0 register.
        """
        address = 56
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseDO0", reply.error_message)
    def read_pulse_do1(self) -> int:
        """
        Reads the contents of the PulseDO1 register.

        Returns
        -------
        int
            Value read from the PulseDO1 register.
        """
        address = 57
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseDO1", reply.error_message)

        return reply.payload

    def write_pulse_do1(self, value: int):
        """
        Writes a value to the PulseDO1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDO1 register.
        """
        address = 57
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseDO1", reply.error_message)
    def read_pulse_do2(self) -> int:
        """
        Reads the contents of the PulseDO2 register.

        Returns
        -------
        int
            Value read from the PulseDO2 register.
        """
        address = 58
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseDO2", reply.error_message)

        return reply.payload

    def write_pulse_do2(self, value: int):
        """
        Writes a value to the PulseDO2 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDO2 register.
        """
        address = 58
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseDO2", reply.error_message)
    def read_pulse_do3(self) -> int:
        """
        Reads the contents of the PulseDO3 register.

        Returns
        -------
        int
            Value read from the PulseDO3 register.
        """
        address = 59
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PulseDO3", reply.error_message)

        return reply.payload

    def write_pulse_do3(self, value: int):
        """
        Writes a value to the PulseDO3 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDO3 register.
        """
        address = 59
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PulseDO3", reply.error_message)
    def read_pwm_frequency_do0(self) -> int:
        """
        Reads the contents of the PwmFrequencyDO0 register.

        Returns
        -------
        int
            Value read from the PwmFrequencyDO0 register.
        """
        address = 60
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PwmFrequencyDO0", reply.error_message)

        return reply.payload

    def write_pwm_frequency_do0(self, value: int):
        """
        Writes a value to the PwmFrequencyDO0 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmFrequencyDO0 register.
        """
        address = 60
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PwmFrequencyDO0", reply.error_message)
    def read_pwm_frequency_do1(self) -> int:
        """
        Reads the contents of the PwmFrequencyDO1 register.

        Returns
        -------
        int
            Value read from the PwmFrequencyDO1 register.
        """
        address = 61
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PwmFrequencyDO1", reply.error_message)

        return reply.payload

    def write_pwm_frequency_do1(self, value: int):
        """
        Writes a value to the PwmFrequencyDO1 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmFrequencyDO1 register.
        """
        address = 61
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PwmFrequencyDO1", reply.error_message)
    def read_pwm_frequency_do2(self) -> int:
        """
        Reads the contents of the PwmFrequencyDO2 register.

        Returns
        -------
        int
            Value read from the PwmFrequencyDO2 register.
        """
        address = 62
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PwmFrequencyDO2", reply.error_message)

        return reply.payload

    def write_pwm_frequency_do2(self, value: int):
        """
        Writes a value to the PwmFrequencyDO2 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmFrequencyDO2 register.
        """
        address = 62
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PwmFrequencyDO2", reply.error_message)
    def read_pwm_frequency_do3(self) -> int:
        """
        Reads the contents of the PwmFrequencyDO3 register.

        Returns
        -------
        int
            Value read from the PwmFrequencyDO3 register.
        """
        address = 63
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("PwmFrequencyDO3", reply.error_message)

        return reply.payload

    def write_pwm_frequency_do3(self, value: int):
        """
        Writes a value to the PwmFrequencyDO3 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmFrequencyDO3 register.
        """
        address = 63
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("PwmFrequencyDO3", reply.error_message)
    def read_pwm_duty_cycle_do0(self) -> int:
        """
        Reads the contents of the PwmDutyCycleDO0 register.

        Returns
        -------
        int
            Value read from the PwmDutyCycleDO0 register.
        """
        address = 64
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PwmDutyCycleDO0", reply.error_message)

        return reply.payload

    def write_pwm_duty_cycle_do0(self, value: int):
        """
        Writes a value to the PwmDutyCycleDO0 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmDutyCycleDO0 register.
        """
        address = 64
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PwmDutyCycleDO0", reply.error_message)
    def read_pwm_duty_cycle_do1(self) -> int:
        """
        Reads the contents of the PwmDutyCycleDO1 register.

        Returns
        -------
        int
            Value read from the PwmDutyCycleDO1 register.
        """
        address = 65
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PwmDutyCycleDO1", reply.error_message)

        return reply.payload

    def write_pwm_duty_cycle_do1(self, value: int):
        """
        Writes a value to the PwmDutyCycleDO1 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmDutyCycleDO1 register.
        """
        address = 65
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PwmDutyCycleDO1", reply.error_message)
    def read_pwm_duty_cycle_do2(self) -> int:
        """
        Reads the contents of the PwmDutyCycleDO2 register.

        Returns
        -------
        int
            Value read from the PwmDutyCycleDO2 register.
        """
        address = 66
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PwmDutyCycleDO2", reply.error_message)

        return reply.payload

    def write_pwm_duty_cycle_do2(self, value: int):
        """
        Writes a value to the PwmDutyCycleDO2 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmDutyCycleDO2 register.
        """
        address = 66
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PwmDutyCycleDO2", reply.error_message)
    def read_pwm_duty_cycle_do3(self) -> int:
        """
        Reads the contents of the PwmDutyCycleDO3 register.

        Returns
        -------
        int
            Value read from the PwmDutyCycleDO3 register.
        """
        address = 67
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PwmDutyCycleDO3", reply.error_message)

        return reply.payload

    def write_pwm_duty_cycle_do3(self, value: int):
        """
        Writes a value to the PwmDutyCycleDO3 register.

        Parameters
        ----------
        value : int
            Value to write to the PwmDutyCycleDO3 register.
        """
        address = 67
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PwmDutyCycleDO3", reply.error_message)
    def read_pwm_start(self) -> PwmOutputs:
        """
        Reads the contents of the PwmStart register.

        Returns
        -------
        PwmOutputs
            Value read from the PwmStart register.
        """
        address = 68
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PwmStart", reply.error_message)

        return reply.payload

    def write_pwm_start(self, value: PwmOutputs):
        """
        Writes a value to the PwmStart register.

        Parameters
        ----------
        value : PwmOutputs
            Value to write to the PwmStart register.
        """
        address = 68
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PwmStart", reply.error_message)
    def read_pwm_stop(self) -> PwmOutputs:
        """
        Reads the contents of the PwmStop register.

        Returns
        -------
        PwmOutputs
            Value read from the PwmStop register.
        """
        address = 69
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PwmStop", reply.error_message)

        return reply.payload

    def write_pwm_stop(self, value: PwmOutputs):
        """
        Writes a value to the PwmStop register.

        Parameters
        ----------
        value : PwmOutputs
            Value to write to the PwmStop register.
        """
        address = 69
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PwmStop", reply.error_message)
    def read_rgb_all(self) -> RgbAllPayload:
        """
        Reads the contents of the RgbAll register.

        Returns
        -------
        RgbAllPayload
            Value read from the RgbAll register.
        """
        address = 70
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("RgbAll", reply.error_message)

        return reply.payload

    def write_rgb_all(self, value: RgbAllPayload):
        """
        Writes a value to the RgbAll register.

        Parameters
        ----------
        value : RgbAllPayload
            Value to write to the RgbAll register.
        """
        address = 70
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("RgbAll", reply.error_message)
    def read_rgb0(self) -> RgbPayload:
        """
        Reads the contents of the Rgb0 register.

        Returns
        -------
        RgbPayload
            Value read from the Rgb0 register.
        """
        address = 71
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Rgb0", reply.error_message)

        return reply.payload

    def write_rgb0(self, value: RgbPayload):
        """
        Writes a value to the Rgb0 register.

        Parameters
        ----------
        value : RgbPayload
            Value to write to the Rgb0 register.
        """
        address = 71
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Rgb0", reply.error_message)
    def read_rgb1(self) -> RgbPayload:
        """
        Reads the contents of the Rgb1 register.

        Returns
        -------
        RgbPayload
            Value read from the Rgb1 register.
        """
        address = 72
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Rgb1", reply.error_message)

        return reply.payload

    def write_rgb1(self, value: RgbPayload):
        """
        Writes a value to the Rgb1 register.

        Parameters
        ----------
        value : RgbPayload
            Value to write to the Rgb1 register.
        """
        address = 72
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Rgb1", reply.error_message)
    def read_led0_current(self) -> int:
        """
        Reads the contents of the Led0Current register.

        Returns
        -------
        int
            Value read from the Led0Current register.
        """
        address = 73
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Led0Current", reply.error_message)

        return reply.payload

    def write_led0_current(self, value: int):
        """
        Writes a value to the Led0Current register.

        Parameters
        ----------
        value : int
            Value to write to the Led0Current register.
        """
        address = 73
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Led0Current", reply.error_message)
    def read_led1_current(self) -> int:
        """
        Reads the contents of the Led1Current register.

        Returns
        -------
        int
            Value read from the Led1Current register.
        """
        address = 74
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Led1Current", reply.error_message)

        return reply.payload

    def write_led1_current(self, value: int):
        """
        Writes a value to the Led1Current register.

        Parameters
        ----------
        value : int
            Value to write to the Led1Current register.
        """
        address = 74
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Led1Current", reply.error_message)
    def read_led0_max_current(self) -> int:
        """
        Reads the contents of the Led0MaxCurrent register.

        Returns
        -------
        int
            Value read from the Led0MaxCurrent register.
        """
        address = 75
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Led0MaxCurrent", reply.error_message)

        return reply.payload

    def write_led0_max_current(self, value: int):
        """
        Writes a value to the Led0MaxCurrent register.

        Parameters
        ----------
        value : int
            Value to write to the Led0MaxCurrent register.
        """
        address = 75
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Led0MaxCurrent", reply.error_message)
    def read_led1_max_current(self) -> int:
        """
        Reads the contents of the Led1MaxCurrent register.

        Returns
        -------
        int
            Value read from the Led1MaxCurrent register.
        """
        address = 76
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Led1MaxCurrent", reply.error_message)

        return reply.payload

    def write_led1_max_current(self, value: int):
        """
        Writes a value to the Led1MaxCurrent register.

        Parameters
        ----------
        value : int
            Value to write to the Led1MaxCurrent register.
        """
        address = 76
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Led1MaxCurrent", reply.error_message)
    def read_event_enable(self) -> Events:
        """
        Reads the contents of the EventEnable register.

        Returns
        -------
        Events
            Value read from the EventEnable register.
        """
        address = 77
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EventEnable", reply.error_message)

        return reply.payload

    def write_event_enable(self, value: Events):
        """
        Writes a value to the EventEnable register.

        Parameters
        ----------
        value : Events
            Value to write to the EventEnable register.
        """
        address = 77
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EventEnable", reply.error_message)
    def read_start_cameras(self) -> CameraOutputs:
        """
        Reads the contents of the StartCameras register.

        Returns
        -------
        CameraOutputs
            Value read from the StartCameras register.
        """
        address = 78
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("StartCameras", reply.error_message)

        return reply.payload

    def write_start_cameras(self, value: CameraOutputs):
        """
        Writes a value to the StartCameras register.

        Parameters
        ----------
        value : CameraOutputs
            Value to write to the StartCameras register.
        """
        address = 78
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("StartCameras", reply.error_message)
    def read_stop_cameras(self) -> CameraOutputs:
        """
        Reads the contents of the StopCameras register.

        Returns
        -------
        CameraOutputs
            Value read from the StopCameras register.
        """
        address = 79
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("StopCameras", reply.error_message)

        return reply.payload

    def write_stop_cameras(self, value: CameraOutputs):
        """
        Writes a value to the StopCameras register.

        Parameters
        ----------
        value : CameraOutputs
            Value to write to the StopCameras register.
        """
        address = 79
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("StopCameras", reply.error_message)
    def read_enable_servos(self) -> ServoOutputs:
        """
        Reads the contents of the EnableServos register.

        Returns
        -------
        ServoOutputs
            Value read from the EnableServos register.
        """
        address = 80
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableServos", reply.error_message)

        return reply.payload

    def write_enable_servos(self, value: ServoOutputs):
        """
        Writes a value to the EnableServos register.

        Parameters
        ----------
        value : ServoOutputs
            Value to write to the EnableServos register.
        """
        address = 80
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableServos", reply.error_message)
    def read_disable_servos(self) -> ServoOutputs:
        """
        Reads the contents of the DisableServos register.

        Returns
        -------
        ServoOutputs
            Value read from the DisableServos register.
        """
        address = 81
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DisableServos", reply.error_message)

        return reply.payload

    def write_disable_servos(self, value: ServoOutputs):
        """
        Writes a value to the DisableServos register.

        Parameters
        ----------
        value : ServoOutputs
            Value to write to the DisableServos register.
        """
        address = 81
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DisableServos", reply.error_message)
    def read_enable_encoders(self) -> EncoderInputs:
        """
        Reads the contents of the EnableEncoders register.

        Returns
        -------
        EncoderInputs
            Value read from the EnableEncoders register.
        """
        address = 82
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableEncoders", reply.error_message)

        return reply.payload

    def write_enable_encoders(self, value: EncoderInputs):
        """
        Writes a value to the EnableEncoders register.

        Parameters
        ----------
        value : EncoderInputs
            Value to write to the EnableEncoders register.
        """
        address = 82
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableEncoders", reply.error_message)
    def read_encoder_mode(self) -> EncoderModeConfig:
        """
        Reads the contents of the EncoderMode register.

        Returns
        -------
        EncoderModeConfig
            Value read from the EncoderMode register.
        """
        address = 83
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EncoderMode", reply.error_message)

        return reply.payload

    def write_encoder_mode(self, value: EncoderModeConfig):
        """
        Writes a value to the EncoderMode register.

        Parameters
        ----------
        value : EncoderModeConfig
            Value to write to the EncoderMode register.
        """
        address = 83
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EncoderMode", reply.error_message)
    def read_camera0_frame(self) -> FrameAcquired:
        """
        Reads the contents of the Camera0Frame register.

        Returns
        -------
        FrameAcquired
            Value read from the Camera0Frame register.
        """
        address = 92
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Camera0Frame", reply.error_message)

        return reply.payload

    def read_camera0_frequency(self) -> int:
        """
        Reads the contents of the Camera0Frequency register.

        Returns
        -------
        int
            Value read from the Camera0Frequency register.
        """
        address = 93
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Camera0Frequency", reply.error_message)

        return reply.payload

    def write_camera0_frequency(self, value: int):
        """
        Writes a value to the Camera0Frequency register.

        Parameters
        ----------
        value : int
            Value to write to the Camera0Frequency register.
        """
        address = 93
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Camera0Frequency", reply.error_message)
    def read_camera1_frame(self) -> FrameAcquired:
        """
        Reads the contents of the Camera1Frame register.

        Returns
        -------
        FrameAcquired
            Value read from the Camera1Frame register.
        """
        address = 94
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Camera1Frame", reply.error_message)

        return reply.payload

    def read_camera1_frequency(self) -> int:
        """
        Reads the contents of the Camera1Frequency register.

        Returns
        -------
        int
            Value read from the Camera1Frequency register.
        """
        address = 95
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Camera1Frequency", reply.error_message)

        return reply.payload

    def write_camera1_frequency(self, value: int):
        """
        Writes a value to the Camera1Frequency register.

        Parameters
        ----------
        value : int
            Value to write to the Camera1Frequency register.
        """
        address = 95
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Camera1Frequency", reply.error_message)
    def read_servo_motor2_period(self) -> int:
        """
        Reads the contents of the ServoMotor2Period register.

        Returns
        -------
        int
            Value read from the ServoMotor2Period register.
        """
        address = 100
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("ServoMotor2Period", reply.error_message)

        return reply.payload

    def write_servo_motor2_period(self, value: int):
        """
        Writes a value to the ServoMotor2Period register.

        Parameters
        ----------
        value : int
            Value to write to the ServoMotor2Period register.
        """
        address = 100
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("ServoMotor2Period", reply.error_message)
    def read_servo_motor2_pulse(self) -> int:
        """
        Reads the contents of the ServoMotor2Pulse register.

        Returns
        -------
        int
            Value read from the ServoMotor2Pulse register.
        """
        address = 101
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("ServoMotor2Pulse", reply.error_message)

        return reply.payload

    def write_servo_motor2_pulse(self, value: int):
        """
        Writes a value to the ServoMotor2Pulse register.

        Parameters
        ----------
        value : int
            Value to write to the ServoMotor2Pulse register.
        """
        address = 101
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("ServoMotor2Pulse", reply.error_message)
    def read_servo_motor3_period(self) -> int:
        """
        Reads the contents of the ServoMotor3Period register.

        Returns
        -------
        int
            Value read from the ServoMotor3Period register.
        """
        address = 102
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("ServoMotor3Period", reply.error_message)

        return reply.payload

    def write_servo_motor3_period(self, value: int):
        """
        Writes a value to the ServoMotor3Period register.

        Parameters
        ----------
        value : int
            Value to write to the ServoMotor3Period register.
        """
        address = 102
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("ServoMotor3Period", reply.error_message)
    def read_servo_motor3_pulse(self) -> int:
        """
        Reads the contents of the ServoMotor3Pulse register.

        Returns
        -------
        int
            Value read from the ServoMotor3Pulse register.
        """
        address = 103
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("ServoMotor3Pulse", reply.error_message)

        return reply.payload

    def write_servo_motor3_pulse(self, value: int):
        """
        Writes a value to the ServoMotor3Pulse register.

        Parameters
        ----------
        value : int
            Value to write to the ServoMotor3Pulse register.
        """
        address = 103
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("ServoMotor3Pulse", reply.error_message)
    def read_encoder_reset(self) -> EncoderInputs:
        """
        Reads the contents of the EncoderReset register.

        Returns
        -------
        EncoderInputs
            Value read from the EncoderReset register.
        """
        address = 108
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EncoderReset", reply.error_message)

        return reply.payload

    def write_encoder_reset(self, value: EncoderInputs):
        """
        Writes a value to the EncoderReset register.

        Parameters
        ----------
        value : EncoderInputs
            Value to write to the EncoderReset register.
        """
        address = 108
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EncoderReset", reply.error_message)
    def read_enable_serial_timestamp(self) -> int:
        """
        Reads the contents of the EnableSerialTimestamp register.

        Returns
        -------
        int
            Value read from the EnableSerialTimestamp register.
        """
        address = 110
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableSerialTimestamp", reply.error_message)

        return reply.payload

    def write_enable_serial_timestamp(self, value: int):
        """
        Writes a value to the EnableSerialTimestamp register.

        Parameters
        ----------
        value : int
            Value to write to the EnableSerialTimestamp register.
        """
        address = 110
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableSerialTimestamp", reply.error_message)
    def read_mimic_port0_ir(self) -> MimicOutput:
        """
        Reads the contents of the MimicPort0IR register.

        Returns
        -------
        MimicOutput
            Value read from the MimicPort0IR register.
        """
        address = 111
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("MimicPort0IR", reply.error_message)

        return reply.payload

    def write_mimic_port0_ir(self, value: MimicOutput):
        """
        Writes a value to the MimicPort0IR register.

        Parameters
        ----------
        value : MimicOutput
            Value to write to the MimicPort0IR register.
        """
        address = 111
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("MimicPort0IR", reply.error_message)
    def read_mimic_port1_ir(self) -> MimicOutput:
        """
        Reads the contents of the MimicPort1IR register.

        Returns
        -------
        MimicOutput
            Value read from the MimicPort1IR register.
        """
        address = 112
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("MimicPort1IR", reply.error_message)

        return reply.payload

    def write_mimic_port1_ir(self, value: MimicOutput):
        """
        Writes a value to the MimicPort1IR register.

        Parameters
        ----------
        value : MimicOutput
            Value to write to the MimicPort1IR register.
        """
        address = 112
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("MimicPort1IR", reply.error_message)
    def read_mimic_port2_ir(self) -> MimicOutput:
        """
        Reads the contents of the MimicPort2IR register.

        Returns
        -------
        MimicOutput
            Value read from the MimicPort2IR register.
        """
        address = 113
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("MimicPort2IR", reply.error_message)

        return reply.payload

    def write_mimic_port2_ir(self, value: MimicOutput):
        """
        Writes a value to the MimicPort2IR register.

        Parameters
        ----------
        value : MimicOutput
            Value to write to the MimicPort2IR register.
        """
        address = 113
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("MimicPort2IR", reply.error_message)
    def read_mimic_port0_valve(self) -> MimicOutput:
        """
        Reads the contents of the MimicPort0Valve register.

        Returns
        -------
        MimicOutput
            Value read from the MimicPort0Valve register.
        """
        address = 117
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("MimicPort0Valve", reply.error_message)

        return reply.payload

    def write_mimic_port0_valve(self, value: MimicOutput):
        """
        Writes a value to the MimicPort0Valve register.

        Parameters
        ----------
        value : MimicOutput
            Value to write to the MimicPort0Valve register.
        """
        address = 117
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("MimicPort0Valve", reply.error_message)
    def read_mimic_port1_valve(self) -> MimicOutput:
        """
        Reads the contents of the MimicPort1Valve register.

        Returns
        -------
        MimicOutput
            Value read from the MimicPort1Valve register.
        """
        address = 118
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("MimicPort1Valve", reply.error_message)

        return reply.payload

    def write_mimic_port1_valve(self, value: MimicOutput):
        """
        Writes a value to the MimicPort1Valve register.

        Parameters
        ----------
        value : MimicOutput
            Value to write to the MimicPort1Valve register.
        """
        address = 118
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("MimicPort1Valve", reply.error_message)
    def read_mimic_port2_valve(self) -> MimicOutput:
        """
        Reads the contents of the MimicPort2Valve register.

        Returns
        -------
        MimicOutput
            Value read from the MimicPort2Valve register.
        """
        address = 119
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("MimicPort2Valve", reply.error_message)

        return reply.payload

    def write_mimic_port2_valve(self, value: MimicOutput):
        """
        Writes a value to the MimicPort2Valve register.

        Parameters
        ----------
        value : MimicOutput
            Value to write to the MimicPort2Valve register.
        """
        address = 119
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("MimicPort2Valve", reply.error_message)
    def read_poke_input_filter(self) -> int:
        """
        Reads the contents of the PokeInputFilter register.

        Returns
        -------
        int
            Value read from the PokeInputFilter register.
        """
        address = 122
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("PokeInputFilter", reply.error_message)

        return reply.payload

    def write_poke_input_filter(self, value: int):
        """
        Writes a value to the PokeInputFilter register.

        Parameters
        ----------
        value : int
            Value to write to the PokeInputFilter register.
        """
        address = 122
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("PokeInputFilter", reply.error_message)

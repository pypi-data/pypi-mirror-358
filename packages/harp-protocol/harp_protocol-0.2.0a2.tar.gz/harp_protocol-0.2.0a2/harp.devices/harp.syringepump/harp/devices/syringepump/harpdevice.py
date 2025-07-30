from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage



class DigitalOutputs(IntFlag):
    """
    The digital output lines.

    Attributes
    ----------
    DO0 : int
        TODO
    DO1 : int
        TODO
    """

    NONE = 0x0
    DO0 = 0x1
    DO1 = 0x2


class DigitalInputs(IntFlag):
    """
    The state of the digital input pin.

    Attributes
    ----------
    DI0 : int
        TODO
    """

    NONE = 0x0
    DI0 = 0x1


class PumpEvents(IntFlag):
    """
    The events that can be enabled/disabled.

    Attributes
    ----------
    STEP : int
        TODO
    DIRECTION : int
        TODO
    FORWARD_SWITCH : int
        TODO
    REVERSE_SWITCH : int
        TODO
    DIGITAL_INPUT : int
        TODO
    PROTOCOL : int
        TODO
    """

    NONE = 0x0
    STEP = 0x1
    DIRECTION = 0x2
    FORWARD_SWITCH = 0x4
    REVERSE_SWITCH = 0x8
    DIGITAL_INPUT = 0x10
    PROTOCOL = 0x20


class StepState(Enum):
    """
    The state of the STEP motor controller pin.

    Attributes
    ----------
    LOW : int
        TODO
    HIGH : int
        TODO
    """

    LOW = 0
    HIGH = 1


class DirectionState(Enum):
    """
    The state of the DIR motor controller pin.

    Attributes
    ----------
    REVERSE : int
        TODO
    FORWARD : int
        TODO
    """

    REVERSE = 0
    FORWARD = 1


class ForwardSwitchState(Enum):
    """
    The state of the forward limit switch.

    Attributes
    ----------
    LOW : int
        TODO
    HIGH : int
        TODO
    """

    LOW = 0
    HIGH = 1


class ReverseSwitchState(Enum):
    """
    The state of the reverse limit switch.

    Attributes
    ----------
    LOW : int
        TODO
    HIGH : int
        TODO
    """

    LOW = 0
    HIGH = 1


class DO0SyncConfig(Enum):
    """
    Configures which signal is mimicked in the digital output 0.

    Attributes
    ----------
    NONE : int
        TODO
    SWITCH_STATE : int
        TODO
    """

    NONE = 0
    SWITCH_STATE = 1


class DO1SyncConfig(Enum):
    """
    Configures which signal is mimicked in the digital output 1.

    Attributes
    ----------
    NONE : int
        TODO
    HEARTBEAT : int
        TODO
    STEP : int
        TODO
    """

    NONE = 0
    HEARTBEAT = 1
    STEP = 2


class DI0TriggerConfig(Enum):
    """
    Configures the function executed when digital input is triggered.

    Attributes
    ----------
    NONE : int
        TODO
    STEP : int
        TODO
    START_PROTOCOL : int
        TODO
    """

    NONE = 0
    STEP = 1
    START_PROTOCOL = 2


class StepModeType(Enum):
    """
    Available step modes.

    Attributes
    ----------
    FULL : int
        TODO
    HALF : int
        TODO
    QUARTER : int
        TODO
    EIGHTH : int
        TODO
    SIXTEENTH : int
        TODO
    """

    FULL = 0
    HALF = 1
    QUARTER = 2
    EIGHTH = 3
    SIXTEENTH = 4


class PumpProtocolType(Enum):
    """
    Available protocol types.

    Attributes
    ----------
    STEP : int
        TODO
    VOLUME : int
        TODO
    """

    STEP = 0
    VOLUME = 1


class PumpBoardType(Enum):
    """
    Available board configurations.

    Attributes
    ----------
    PUMP : int
        TODO
    FISH_FEEDER : int
        TODO
    STEPPER_MOTOR : int
        TODO
    """

    PUMP = 0
    FISH_FEEDER = 1
    STEPPER_MOTOR = 2


class ProtocolState(Enum):
    """
    The state of the protocol execution.

    Attributes
    ----------
    IDLE : int
        TODO
    RUNNING : int
        TODO
    """

    IDLE = 0
    RUNNING = 1


class ProtocolDirectionState(Enum):
    """
    The state of the protocol execution.

    Attributes
    ----------
    REVERSE : int
        TODO
    FORWARD : int
        TODO
    """

    REVERSE = 0
    FORWARD = 1


# All available registers for the device as a Enum
class SyringePumpRegisters(Enum):
    """Enum for all available registers in the SyringePump device.

    Attributes
    ----------
    ENABLE_MOTOR_DRIVER : int
        Enables the motor driver.
    ENABLE_PROTOCOL : int
        Enables the currently defined protocol.
    STEP : int
        Status of the STEP motor controller pin.
    DIRECTION : int
        Status of the DIR motor controller pin.
    FORWARD_SWITCH : int
        Status of the forward limit switch.
    REVERSE_SWITCH : int
        Status of the reverse limit switch.
    DIGITAL_INPUT_STATE : int
        Status of the digital input pin.
    DIGITAL_OUTPUT_SET : int
        Set the specified digital output lines.
    DIGITAL_OUTPUT_CLEAR : int
        Clear the specified digital output lines.
    DO0_SYNC : int
        Configures which signal is mimicked in the digital output 0.
    DO1_SYNC : int
        Configures which signal is mimicked in the digital output 1.
    DI0_TRIGGER : int
        Configures the callback function triggered when digital input is triggered.
    STEP_MODE : int
        Sets the motor step mode from a list of available types.
    PROTOCOL_STEP_COUNT : int
        Sets the number of steps to be executed in the current protocol.
    PROTOCOL_FLOWRATE : int
        Sets the flowrate of the protocol in ul/s.
    PROTOCOL_PERIOD : int
        Sets the period, in ms, of of each step in the protocol.
    PROTOCOL_VOLUME : int
        Sets the volume to be delivered, in ul.
    PROTOCOL_TYPE : int
        Sets the type of protocol to be executed.
    CALIBRATION_OFFSET : int
        Sets the offset value of the calibration curve.
    CALIBRATION_SLOPE : int
        Sets the slope value of the calibration curve.
    ENABLE_EVENTS : int
        Specifies all the active events in the device.
    BOARD_TYPE : int
        Sets the board type.
    PROTOCOL : int
        Status of the protocol execution.
    PROTOCOL_DIRECTION : int
        Sets the direction of the protocol execution.
    """
    ENABLE_MOTOR_DRIVER = 32
    ENABLE_PROTOCOL = 33
    STEP = 34
    DIRECTION = 35
    FORWARD_SWITCH = 36
    REVERSE_SWITCH = 37
    DIGITAL_INPUT_STATE = 38
    DIGITAL_OUTPUT_SET = 39
    DIGITAL_OUTPUT_CLEAR = 40
    DO0_SYNC = 41
    DO1_SYNC = 42
    DI0_TRIGGER = 43
    STEP_MODE = 44
    PROTOCOL_STEP_COUNT = 45
    PROTOCOL_FLOWRATE = 46
    PROTOCOL_PERIOD = 47
    PROTOCOL_VOLUME = 48
    PROTOCOL_TYPE = 49
    CALIBRATION_OFFSET = 50
    CALIBRATION_SLOPE = 51
    ENABLE_EVENTS = 52
    BOARD_TYPE = 53
    PROTOCOL = 54
    PROTOCOL_DIRECTION = 55


class SyringePump(Device):
    """
    SyringePump class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1296:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1296}, got {self.WHO_AM_I}")

    def read_enable_motor_driver(self) -> bool:
        """
        Reads the contents of the EnableMotorDriver register.

        Returns
        -------
        bool
            Value read from the EnableMotorDriver register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableMotorDriver", reply.error_message)

        return reply.payload

    def write_enable_motor_driver(self, value: bool):
        """
        Writes a value to the EnableMotorDriver register.

        Parameters
        ----------
        value : bool
            Value to write to the EnableMotorDriver register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableMotorDriver", reply.error_message)
    def read_enable_protocol(self) -> bool:
        """
        Reads the contents of the EnableProtocol register.

        Returns
        -------
        bool
            Value read from the EnableProtocol register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableProtocol", reply.error_message)

        return reply.payload

    def write_enable_protocol(self, value: bool):
        """
        Writes a value to the EnableProtocol register.

        Parameters
        ----------
        value : bool
            Value to write to the EnableProtocol register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableProtocol", reply.error_message)
    def read_step(self) -> StepState:
        """
        Reads the contents of the Step register.

        Returns
        -------
        StepState
            Value read from the Step register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Step", reply.error_message)

        return reply.payload

    def write_step(self, value: StepState):
        """
        Writes a value to the Step register.

        Parameters
        ----------
        value : StepState
            Value to write to the Step register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Step", reply.error_message)
    def read_direction(self) -> DirectionState:
        """
        Reads the contents of the Direction register.

        Returns
        -------
        DirectionState
            Value read from the Direction register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Direction", reply.error_message)

        return reply.payload

    def write_direction(self, value: DirectionState):
        """
        Writes a value to the Direction register.

        Parameters
        ----------
        value : DirectionState
            Value to write to the Direction register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Direction", reply.error_message)
    def read_forward_switch(self) -> ForwardSwitchState:
        """
        Reads the contents of the ForwardSwitch register.

        Returns
        -------
        ForwardSwitchState
            Value read from the ForwardSwitch register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("ForwardSwitch", reply.error_message)

        return reply.payload

    def read_reverse_switch(self) -> ReverseSwitchState:
        """
        Reads the contents of the ReverseSwitch register.

        Returns
        -------
        ReverseSwitchState
            Value read from the ReverseSwitch register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("ReverseSwitch", reply.error_message)

        return reply.payload

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_digital_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputSet register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalOutputSet", reply.error_message)

        return reply.payload

    def write_digital_output_set(self, value: DigitalOutputs):
        """
        Writes a value to the DigitalOutputSet register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputSet register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputSet", reply.error_message)
    def read_digital_output_clear(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputClear register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputClear register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalOutputClear", reply.error_message)

        return reply.payload

    def write_digital_output_clear(self, value: DigitalOutputs):
        """
        Writes a value to the DigitalOutputClear register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputClear register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputClear", reply.error_message)
    def read_do0_sync(self) -> DO0SyncConfig:
        """
        Reads the contents of the DO0Sync register.

        Returns
        -------
        DO0SyncConfig
            Value read from the DO0Sync register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO0Sync", reply.error_message)

        return reply.payload

    def write_do0_sync(self, value: DO0SyncConfig):
        """
        Writes a value to the DO0Sync register.

        Parameters
        ----------
        value : DO0SyncConfig
            Value to write to the DO0Sync register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO0Sync", reply.error_message)
    def read_do1_sync(self) -> DO1SyncConfig:
        """
        Reads the contents of the DO1Sync register.

        Returns
        -------
        DO1SyncConfig
            Value read from the DO1Sync register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO1Sync", reply.error_message)

        return reply.payload

    def write_do1_sync(self, value: DO1SyncConfig):
        """
        Writes a value to the DO1Sync register.

        Parameters
        ----------
        value : DO1SyncConfig
            Value to write to the DO1Sync register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO1Sync", reply.error_message)
    def read_di0_trigger(self) -> DI0TriggerConfig:
        """
        Reads the contents of the DI0Trigger register.

        Returns
        -------
        DI0TriggerConfig
            Value read from the DI0Trigger register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DI0Trigger", reply.error_message)

        return reply.payload

    def write_di0_trigger(self, value: DI0TriggerConfig):
        """
        Writes a value to the DI0Trigger register.

        Parameters
        ----------
        value : DI0TriggerConfig
            Value to write to the DI0Trigger register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DI0Trigger", reply.error_message)
    def read_step_mode(self) -> StepModeType:
        """
        Reads the contents of the StepMode register.

        Returns
        -------
        StepModeType
            Value read from the StepMode register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("StepMode", reply.error_message)

        return reply.payload

    def write_step_mode(self, value: StepModeType):
        """
        Writes a value to the StepMode register.

        Parameters
        ----------
        value : StepModeType
            Value to write to the StepMode register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("StepMode", reply.error_message)
    def read_protocol_step_count(self) -> int:
        """
        Reads the contents of the ProtocolStepCount register.

        Returns
        -------
        int
            Value read from the ProtocolStepCount register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("ProtocolStepCount", reply.error_message)

        return reply.payload

    def write_protocol_step_count(self, value: int):
        """
        Writes a value to the ProtocolStepCount register.

        Parameters
        ----------
        value : int
            Value to write to the ProtocolStepCount register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("ProtocolStepCount", reply.error_message)
    def read_protocol_period(self) -> int:
        """
        Reads the contents of the ProtocolPeriod register.

        Returns
        -------
        int
            Value read from the ProtocolPeriod register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("ProtocolPeriod", reply.error_message)

        return reply.payload

    def write_protocol_period(self, value: int):
        """
        Writes a value to the ProtocolPeriod register.

        Parameters
        ----------
        value : int
            Value to write to the ProtocolPeriod register.
        """
        address = 47
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("ProtocolPeriod", reply.error_message)
    def read_enable_events(self) -> PumpEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        PumpEvents
            Value read from the EnableEvents register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableEvents", reply.error_message)

        return reply.payload

    def write_enable_events(self, value: PumpEvents):
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : PumpEvents
            Value to write to the EnableEvents register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableEvents", reply.error_message)
    def read_protocol(self) -> ProtocolState:
        """
        Reads the contents of the Protocol register.

        Returns
        -------
        ProtocolState
            Value read from the Protocol register.
        """
        address = 54
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Protocol", reply.error_message)

        return reply.payload

    def read_protocol_direction(self) -> ProtocolDirectionState:
        """
        Reads the contents of the ProtocolDirection register.

        Returns
        -------
        ProtocolDirectionState
            Value read from the ProtocolDirection register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("ProtocolDirection", reply.error_message)

        return reply.payload

    def write_protocol_direction(self, value: ProtocolDirectionState):
        """
        Writes a value to the ProtocolDirection register.

        Parameters
        ----------
        value : ProtocolDirectionState
            Value to write to the ProtocolDirection register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("ProtocolDirection", reply.error_message)

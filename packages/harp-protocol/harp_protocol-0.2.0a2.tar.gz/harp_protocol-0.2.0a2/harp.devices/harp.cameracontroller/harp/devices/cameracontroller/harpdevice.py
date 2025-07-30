from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage



class Cameras(IntFlag):
    """
    Specifies the target camera line.

    Attributes
    ----------
    CAMERA0 : int
        TODO
    CAMERA1 : int
        TODO
    """

    NONE = 0x0
    CAMERA0 = 0x1
    CAMERA1 = 0x2


class Servos(IntFlag):
    """
    Specifies the target servo-motor lines.

    Attributes
    ----------
    SERVO0 : int
        TODO
    SERVO1 : int
        TODO
    """

    NONE = 0x0
    SERVO0 = 0x1
    SERVO1 = 0x2


class DigitalOutputs(IntFlag):
    """
    Available digital output lines.

    Attributes
    ----------
    TRIGGER0 : int
        TODO
    SYNC0 : int
        TODO
    TRIGGER1 : int
        TODO
    SYNC1 : int
        TODO
    """

    NONE = 0x0
    TRIGGER0 = 0x1
    SYNC0 = 0x2
    TRIGGER1 = 0x4
    SYNC1 = 0x8


class DigitalInputs(IntFlag):
    """
    Available digital input lines.

    Attributes
    ----------
    DI0 : int
        TODO
    """

    NONE = 0x0
    DI0 = 0x1


class CameraControllerEvents(IntFlag):
    """
    Specifies the active events in the device.

    Attributes
    ----------
    TRIGGER_AND_SYNCH : int
        Enables CameraTrigger and CameraSync events.
    DIGITAL_INPUTS : int
        Enables DigitalInputs
    """

    NONE = 0x0
    TRIGGER_AND_SYNCH = 0x1
    DIGITAL_INPUTS = 0x2


class DI0ModeConfig(Enum):
    """
    Specifies the operation mode of digital input line 0.

    Attributes
    ----------
    HIGH_ENABLES_CAMERA0 : int
        When High, enables Camera0 or Servo0.
    HIGH_ENABLES_CAMERA1 : int
        When High, enables Camera1 or Servo1.
    HIGH_ENABLES_CAMERA_BOTH : int
        When High, enables both Cameras or Servos.
    LOW_ENABLES_CAMERA0 : int
        When Low, enables Camera0 or Servo0.
    LOW_ENABLES_CAMERA1 : int
        When Low, enables Camera1 or Servo1.
    LOW_ENABLES_CAMERA_BOTH : int
        When Low, enables both Cameras or Servos.
    DEFAULT : int
        The line will function as a passive digital input.
    """

    HIGH_ENABLES_CAMERA0 = 0
    HIGH_ENABLES_CAMERA1 = 1
    HIGH_ENABLES_CAMERA_BOTH = 2
    LOW_ENABLES_CAMERA0 = 3
    LOW_ENABLES_CAMERA1 = 4
    LOW_ENABLES_CAMERA_BOTH = 5
    DEFAULT = 6


class ControlModeConfig(Enum):
    """
    Specifies the operation mode of a specific output line.

    Attributes
    ----------
    CAMERA : int
        Enables Camera mode and it will produce the configured trigger.
    SERVO : int
        Enables Servo mode and it will produce the configured trigger.
    """

    CAMERA = 0
    SERVO = 1


# All available registers for the device as a Enum
class CameraControllerRegisters(Enum):
    """Enum for all available registers in the CameraController device.

    Attributes
    ----------
    CAMERA_START : int
        Starts the generation of triggers on the specified camera lines.
    CAMERA_STOP : int
        Stops the generation of triggers on the specified camera lines.
    SERVO_ENABLE : int
        Enables servo control on the specified camera lines.
    SERVO_DISABLE : int
        Disables servo control on the specified camera lines.
    OUTPUT_SET : int
        Set the specified digital output lines.
    OUTPUT_CLEAR : int
        Clear the specified digital output lines
    OUTPUT_STATE : int
        Write the state of all digital output lines
    DIGITAL_INPUT_STATE : int
        Emits an event when the state of the digital input line changes.
    CAMERA0_TRIGGER : int
        Emits an event when a frame is triggered on camera 0.
    CAMERA1_TRIGGER : int
        Emits an event when a frame is triggered on camera 1.
    CAMERA0_SYNC : int
        Emits an event when a sync state is toggled on camera 0.
    CAMERA1_SYNC : int
        Emits an event when a sync state is toggled on camera 0.
    SERVO_STATE : int
        Returns the current state of the servo motors.
    RESERVED0 : int
        Reserved for future use.
    SYNC_INTERVAL : int
        Configures the interval in seconds between each sync pulse
    RESERVED1 : int
        Reserved for future use.
    DI0_MODE : int
        Configures the mode of the digital input line 0.
    CONTROL0_MODE : int
        Configures the control mode of Camera/Servo 0.
    CAMERA0_FREQUENCY : int
        Configures the frequency (Hz) of the trigger pulses on Camera 0 when using Camera mode.
    SERVO0_PERIOD : int
        Configures the servo motor period (us) when using Servo mode (sensitive to 2 us)
    SERVO0_PULSE_WIDTH : int
        Configures the servo pulse width (us) when using Servo mode (sensitive to 2 us)
    CONTROL1_MODE : int
        Configures the control mode of Camera/Servo 1.
    CAMERA1_FREQUENCY : int
        Configures the frequency (Hz) of the trigger pulses on Camera 1 when using Camera mode.
    SERVO1_PERIOD : int
        Configures the servo motor period (us) when using Servo mode (sensitive to 2 us)
    SERVO1_PULSE_WIDTH : int
        Configures the servo pulse width (us) when using Servo mode (sensitive to 2 us)
    RESERVED2 : int
        Reserved for future use.
    RESERVED3 : int
        Reserved for future use.
    ENABLE_EVENTS : int
        Specifies the active events in the device.
    """
    CAMERA_START = 32
    CAMERA_STOP = 33
    SERVO_ENABLE = 34
    SERVO_DISABLE = 35
    OUTPUT_SET = 36
    OUTPUT_CLEAR = 37
    OUTPUT_STATE = 38
    DIGITAL_INPUT_STATE = 39
    CAMERA0_TRIGGER = 40
    CAMERA1_TRIGGER = 41
    CAMERA0_SYNC = 42
    CAMERA1_SYNC = 43
    SERVO_STATE = 44
    RESERVED0 = 45
    SYNC_INTERVAL = 46
    RESERVED1 = 47
    DI0_MODE = 48
    CONTROL0_MODE = 49
    CAMERA0_FREQUENCY = 50
    SERVO0_PERIOD = 51
    SERVO0_PULSE_WIDTH = 52
    CONTROL1_MODE = 53
    CAMERA1_FREQUENCY = 54
    SERVO1_PERIOD = 55
    SERVO1_PULSE_WIDTH = 56
    RESERVED2 = 57
    RESERVED3 = 58
    ENABLE_EVENTS = 59


class CameraController(Device):
    """
    CameraController class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1168:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1168}, got {self.WHO_AM_I}")

    def read_camera_start(self) -> Cameras:
        """
        Reads the contents of the CameraStart register.

        Returns
        -------
        Cameras
            Value read from the CameraStart register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("CameraStart", reply.error_message)

        return reply.payload

    def write_camera_start(self, value: Cameras):
        """
        Writes a value to the CameraStart register.

        Parameters
        ----------
        value : Cameras
            Value to write to the CameraStart register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("CameraStart", reply.error_message)
    def read_camera_stop(self) -> Cameras:
        """
        Reads the contents of the CameraStop register.

        Returns
        -------
        Cameras
            Value read from the CameraStop register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("CameraStop", reply.error_message)

        return reply.payload

    def write_camera_stop(self, value: Cameras):
        """
        Writes a value to the CameraStop register.

        Parameters
        ----------
        value : Cameras
            Value to write to the CameraStop register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("CameraStop", reply.error_message)
    def read_servo_enable(self) -> Servos:
        """
        Reads the contents of the ServoEnable register.

        Returns
        -------
        Servos
            Value read from the ServoEnable register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("ServoEnable", reply.error_message)

        return reply.payload

    def write_servo_enable(self, value: Servos):
        """
        Writes a value to the ServoEnable register.

        Parameters
        ----------
        value : Servos
            Value to write to the ServoEnable register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("ServoEnable", reply.error_message)
    def read_servo_disable(self) -> Servos:
        """
        Reads the contents of the ServoDisable register.

        Returns
        -------
        Servos
            Value read from the ServoDisable register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("ServoDisable", reply.error_message)

        return reply.payload

    def write_servo_disable(self, value: Servos):
        """
        Writes a value to the ServoDisable register.

        Parameters
        ----------
        value : Servos
            Value to write to the ServoDisable register.
        """
        address = 35
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("ServoDisable", reply.error_message)
    def read_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputSet register.
        """
        address = 36
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
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
        address = 36
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
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
        address = 37
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
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
        address = 37
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("OutputClear", reply.error_message)
    def read_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputState register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
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
        address = 38
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("OutputState", reply.error_message)
    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_camera0_trigger(self) -> int:
        """
        Reads the contents of the Camera0Trigger register.

        Returns
        -------
        int
            Value read from the Camera0Trigger register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Camera0Trigger", reply.error_message)

        return reply.payload

    def read_camera1_trigger(self) -> int:
        """
        Reads the contents of the Camera1Trigger register.

        Returns
        -------
        int
            Value read from the Camera1Trigger register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Camera1Trigger", reply.error_message)

        return reply.payload

    def read_camera0_sync(self) -> int:
        """
        Reads the contents of the Camera0Sync register.

        Returns
        -------
        int
            Value read from the Camera0Sync register.
        """
        address = 42
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Camera0Sync", reply.error_message)

        return reply.payload

    def read_camera1_sync(self) -> int:
        """
        Reads the contents of the Camera1Sync register.

        Returns
        -------
        int
            Value read from the Camera1Sync register.
        """
        address = 43
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Camera1Sync", reply.error_message)

        return reply.payload

    def read_servo_state(self) -> Servos:
        """
        Reads the contents of the ServoState register.

        Returns
        -------
        Servos
            Value read from the ServoState register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("ServoState", reply.error_message)

        return reply.payload

    def read_sync_interval(self) -> int:
        """
        Reads the contents of the SyncInterval register.

        Returns
        -------
        int
            Value read from the SyncInterval register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("SyncInterval", reply.error_message)

        return reply.payload

    def write_sync_interval(self, value: int):
        """
        Writes a value to the SyncInterval register.

        Parameters
        ----------
        value : int
            Value to write to the SyncInterval register.
        """
        address = 46
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("SyncInterval", reply.error_message)
    def read_di0_mode(self) -> DI0ModeConfig:
        """
        Reads the contents of the DI0Mode register.

        Returns
        -------
        DI0ModeConfig
            Value read from the DI0Mode register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DI0Mode", reply.error_message)

        return reply.payload

    def write_di0_mode(self, value: DI0ModeConfig):
        """
        Writes a value to the DI0Mode register.

        Parameters
        ----------
        value : DI0ModeConfig
            Value to write to the DI0Mode register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DI0Mode", reply.error_message)
    def read_control0_mode(self) -> ControlModeConfig:
        """
        Reads the contents of the Control0Mode register.

        Returns
        -------
        ControlModeConfig
            Value read from the Control0Mode register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Control0Mode", reply.error_message)

        return reply.payload

    def write_control0_mode(self, value: ControlModeConfig):
        """
        Writes a value to the Control0Mode register.

        Parameters
        ----------
        value : ControlModeConfig
            Value to write to the Control0Mode register.
        """
        address = 49
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Control0Mode", reply.error_message)
    def read_camera0_frequency(self) -> int:
        """
        Reads the contents of the Camera0Frequency register.

        Returns
        -------
        int
            Value read from the Camera0Frequency register.
        """
        address = 50
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
        address = 50
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Camera0Frequency", reply.error_message)
    def read_servo0_period(self) -> int:
        """
        Reads the contents of the Servo0Period register.

        Returns
        -------
        int
            Value read from the Servo0Period register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Servo0Period", reply.error_message)

        return reply.payload

    def write_servo0_period(self, value: int):
        """
        Writes a value to the Servo0Period register.

        Parameters
        ----------
        value : int
            Value to write to the Servo0Period register.
        """
        address = 51
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Servo0Period", reply.error_message)
    def read_servo0_pulse_width(self) -> int:
        """
        Reads the contents of the Servo0PulseWidth register.

        Returns
        -------
        int
            Value read from the Servo0PulseWidth register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Servo0PulseWidth", reply.error_message)

        return reply.payload

    def write_servo0_pulse_width(self, value: int):
        """
        Writes a value to the Servo0PulseWidth register.

        Parameters
        ----------
        value : int
            Value to write to the Servo0PulseWidth register.
        """
        address = 52
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Servo0PulseWidth", reply.error_message)
    def read_control1_mode(self) -> ControlModeConfig:
        """
        Reads the contents of the Control1Mode register.

        Returns
        -------
        ControlModeConfig
            Value read from the Control1Mode register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("Control1Mode", reply.error_message)

        return reply.payload

    def write_control1_mode(self, value: ControlModeConfig):
        """
        Writes a value to the Control1Mode register.

        Parameters
        ----------
        value : ControlModeConfig
            Value to write to the Control1Mode register.
        """
        address = 53
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("Control1Mode", reply.error_message)
    def read_camera1_frequency(self) -> int:
        """
        Reads the contents of the Camera1Frequency register.

        Returns
        -------
        int
            Value read from the Camera1Frequency register.
        """
        address = 54
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
        address = 54
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Camera1Frequency", reply.error_message)
    def read_servo1_period(self) -> int:
        """
        Reads the contents of the Servo1Period register.

        Returns
        -------
        int
            Value read from the Servo1Period register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Servo1Period", reply.error_message)

        return reply.payload

    def write_servo1_period(self, value: int):
        """
        Writes a value to the Servo1Period register.

        Parameters
        ----------
        value : int
            Value to write to the Servo1Period register.
        """
        address = 55
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Servo1Period", reply.error_message)
    def read_servo1_pulse_width(self) -> int:
        """
        Reads the contents of the Servo1PulseWidth register.

        Returns
        -------
        int
            Value read from the Servo1PulseWidth register.
        """
        address = 56
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("Servo1PulseWidth", reply.error_message)

        return reply.payload

    def write_servo1_pulse_width(self, value: int):
        """
        Writes a value to the Servo1PulseWidth register.

        Parameters
        ----------
        value : int
            Value to write to the Servo1PulseWidth register.
        """
        address = 56
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("Servo1PulseWidth", reply.error_message)
    def read_enable_events(self) -> CameraControllerEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        CameraControllerEvents
            Value read from the EnableEvents register.
        """
        address = 59
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("EnableEvents", reply.error_message)

        return reply.payload

    def write_enable_events(self, value: CameraControllerEvents):
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : CameraControllerEvents
            Value to write to the EnableEvents register.
        """
        address = 59
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("EnableEvents", reply.error_message)

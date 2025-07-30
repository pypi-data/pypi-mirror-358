from dataclasses import dataclass
from enum import Enum, IntFlag

from harp.communication import Device
from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage


@dataclass
class AnalogDataPayload:
    Channel0: int
    Channel1: int
    Channel2: int
    Channel3: int


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


class DigitalOutputs(IntFlag):
    """
    Specifies the state of port digital output lines.

    Attributes
    ----------
    DO0 : int
        TODO
    DO1 : int
        TODO
    DO2 : int
        TODO
    DO3 : int
        TODO
    DO0_CHANGED : int
        TODO
    DO1_CHANGED : int
        TODO
    DO2_CHANGED : int
        TODO
    DO4_CHANGED : int
        TODO
    """

    NONE = 0x0
    DO0 = 0x1
    DO1 = 0x2
    DO2 = 0x4
    DO3 = 0x8
    DO0_CHANGED = 0x10
    DO1_CHANGED = 0x20
    DO2_CHANGED = 0x40
    DO4_CHANGED = 0x80


class RangeAndFilterConfig(Enum):
    """
    Available settings to set the range (Volt) and LowPass filter cutoff (Hz) of the ADC.

    Attributes
    ----------
    RANGE5_V_LOW_PASS1500_HZ : int
        TODO
    RANGE5_V_LOW_PASS3000_HZ : int
        TODO
    RANGE5_V_LOW_PASS6000_HZ : int
        TODO
    RANGE5_V_LOW_PASS10300_HZ : int
        TODO
    RANGE5_V_LOW_PASS13700_HZ : int
        TODO
    RANGE5_V_LOW_PASS15000_HZ : int
        TODO
    RANGE10_V_LOW_PASS1500_HZ : int
        TODO
    RANGE10_V_LOW_PASS3000_HZ : int
        TODO
    RANGE10_V_LOW_PASS6000_HZ : int
        TODO
    RANGE10_V_LOW_PASS11900_HZ : int
        TODO
    RANGE10_V_LOW_PASS18500_HZ : int
        TODO
    RANGE10_V_LOW_PASS22000_HZ : int
        TODO
    """

    RANGE5_V_LOW_PASS1500_HZ = 6
    RANGE5_V_LOW_PASS3000_HZ = 5
    RANGE5_V_LOW_PASS6000_HZ = 4
    RANGE5_V_LOW_PASS10300_HZ = 3
    RANGE5_V_LOW_PASS13700_HZ = 2
    RANGE5_V_LOW_PASS15000_HZ = 1
    RANGE10_V_LOW_PASS1500_HZ = 22
    RANGE10_V_LOW_PASS3000_HZ = 21
    RANGE10_V_LOW_PASS6000_HZ = 20
    RANGE10_V_LOW_PASS11900_HZ = 19
    RANGE10_V_LOW_PASS18500_HZ = 18
    RANGE10_V_LOW_PASS22000_HZ = 17


class SamplingRateMode(Enum):
    """
    Available sampling frequency settings of the ADC.

    Attributes
    ----------
    SAMPLING_RATE1000_HZ : int
        TODO
    SAMPLING_RATE2000_HZ : int
        TODO
    """

    SAMPLING_RATE1000_HZ = 0
    SAMPLING_RATE2000_HZ = 1


class TriggerConfig(Enum):
    """
    Available configurations for when using DI0 as an acquisition trigger.

    Attributes
    ----------
    NONE : int
        TODO
    START_ON_RISING_EDGE : int
        TODO
    START_ON_FALLING_EDGE : int
        TODO
    SAMPLE_ON_RISING_EDGE : int
        TODO
    """

    NONE = 0
    START_ON_RISING_EDGE = 1
    START_ON_FALLING_EDGE = 2
    SAMPLE_ON_RISING_EDGE = 3


class SyncConfig(Enum):
    """
    Available configurations when using DO0 pin to report firmware events.

    Attributes
    ----------
    NONE : int
        TODO
    HEARTBEAT : int
        TODO
    PULSE : int
        TODO
    """

    NONE = 0
    HEARTBEAT = 1
    PULSE = 2


class StartSyncOutputTarget(Enum):
    """
    Available digital output pins that are able to be triggered on acquisition start.

    Attributes
    ----------
    NONE : int
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
    DO0 = 1
    DO1 = 2
    DO2 = 3
    DO3 = 4


class AdcChannel(Enum):
    """
    Available target analog channels to be targeted for threshold events.

    Attributes
    ----------
    CHANNEL0 : int
        TODO
    CHANNEL1 : int
        TODO
    CHANNEL2 : int
        TODO
    CHANNEL3 : int
        TODO
    NONE : int
        TODO
    """

    CHANNEL0 = 0
    CHANNEL1 = 1
    CHANNEL2 = 2
    CHANNEL3 = 3
    NONE = 8


# All available registers for the device as a Enum
class AnalogInputRegisters(Enum):
    """Enum for all available registers in the AnalogInput device.

    Attributes
    ----------
    ACQUISITION_STATE : int
        Enables the data acquisition.
    ANALOG_DATA : int
        Value from a single read of all ADC channels.
    DIGITAL_INPUT_STATE : int
        State of the digital input pin 0.
    RESERVED0 : int
        Reserved
    RESERVED1 : int
        Reserved
    RANGE_AND_FILTER : int
        Sets the range and LowPass filter cutoff of the ADC.
    SAMPLING_RATE : int
        Sets the sampling frequency of the ADC.
    DI0_TRIGGER : int
        Configuration of the digital input pin 0.
    DO0_SYNC : int
        Configuration of the digital output pin 0.
    DO0_PULSE_WIDTH : int
        Pulse duration (ms) for the digital output pin 0. The pulse will only be emitted when DO0Sync == Pulse.
    DIGITAL_OUTPUT_SET : int
        Set the specified digital output lines.
    DIGITAL_OUTPUT_CLEAR : int
        Clear the specified digital output lines.
    DIGITAL_OUTPUT_TOGGLE : int
        Toggle the specified digital output lines
    DIGITAL_OUTPUT_STATE : int
        Write the state of all digital output lines. An event will be emitted when the value of any pin was changed by a threshold event.
    RESERVED2 : int
        Reserved
    RESERVED3 : int
        Reserved
    SYNC_OUTPUT : int
        Digital output that will be set when acquisition starts.
    RESERVED4 : int
        Reserved
    RESERVED5 : int
        Reserved
    RESERVED6 : int
        Reserved
    RESERVED7 : int
        Reserved
    RESERVED8 : int
        Reserved
    RESERVED9 : int
        Reserved
    RESERVED10 : int
        Reserved
    RESERVED11 : int
        Reserved
    RESERVED12 : int
        Reserved
    DO0_TARGET_CHANNEL : int
        Target ADC channel that will be used to trigger a threshold event on DO0 pin.
    DO1_TARGET_CHANNEL : int
        Target ADC channel that will be used to trigger a threshold event on DO1 pin.
    DO2_TARGET_CHANNEL : int
        Target ADC channel that will be used to trigger a threshold event on DO2 pin.
    DO3_TARGET_CHANNEL : int
        Target ADC channel that will be used to trigger a threshold event on DO3 pin.
    RESERVED13 : int
        Reserved
    RESERVED14 : int
        Reserved
    RESERVED15 : int
        Reserved
    RESERVED16 : int
        Reserved
    DO0_THRESHOLD : int
        Value used to threshold an ADC read, and trigger DO0 pin.
    DO1_THRESHOLD : int
        Value used to threshold an ADC read, and trigger DO1 pin.
    DO2_THRESHOLD : int
        Value used to threshold an ADC read, and trigger DO2 pin.
    DO3_THRESHOLD : int
        Value used to threshold an ADC read, and trigger DO3 pin.
    RESERVED17 : int
        Reserved
    RESERVED18 : int
        Reserved
    RESERVED19 : int
        Reserved
    RESERVED20 : int
        Reserved
    DO0_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO0 pin event.
    DO1_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO1 pin event.
    DO2_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO2 pin event.
    DO3_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO3 pin event.
    RESERVED21 : int
        Reserved
    RESERVED22 : int
        Reserved
    RESERVED23 : int
        Reserved
    RESERVED24 : int
        Reserved
    DO0_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO0 pin event.
    DO1_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO1 pin event.
    DO2_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO2 pin event.
    DO3_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO3 pin event.
    RESERVED25 : int
        Reserved
    RESERVED26 : int
        Reserved
    RESERVED27 : int
        Reserved
    RESERVED28 : int
        Reserved
    RESERVED29 : int
        Reserved
    """
    ACQUISITION_STATE = 32
    ANALOG_DATA = 33
    DIGITAL_INPUT_STATE = 34
    RESERVED0 = 35
    RESERVED1 = 36
    RANGE_AND_FILTER = 37
    SAMPLING_RATE = 38
    DI0_TRIGGER = 39
    DO0_SYNC = 40
    DO0_PULSE_WIDTH = 41
    DIGITAL_OUTPUT_SET = 42
    DIGITAL_OUTPUT_CLEAR = 43
    DIGITAL_OUTPUT_TOGGLE = 44
    DIGITAL_OUTPUT_STATE = 45
    RESERVED2 = 46
    RESERVED3 = 47
    SYNC_OUTPUT = 48
    RESERVED4 = 49
    RESERVED5 = 50
    RESERVED6 = 51
    RESERVED7 = 52
    RESERVED8 = 53
    RESERVED9 = 54
    RESERVED10 = 55
    RESERVED11 = 56
    RESERVED12 = 57
    DO0_TARGET_CHANNEL = 58
    DO1_TARGET_CHANNEL = 59
    DO2_TARGET_CHANNEL = 60
    DO3_TARGET_CHANNEL = 61
    RESERVED13 = 62
    RESERVED14 = 63
    RESERVED15 = 64
    RESERVED16 = 65
    DO0_THRESHOLD = 66
    DO1_THRESHOLD = 67
    DO2_THRESHOLD = 68
    DO3_THRESHOLD = 69
    RESERVED17 = 70
    RESERVED18 = 71
    RESERVED19 = 72
    RESERVED20 = 73
    DO0_TIME_ABOVE_THRESHOLD = 74
    DO1_TIME_ABOVE_THRESHOLD = 75
    DO2_TIME_ABOVE_THRESHOLD = 76
    DO3_TIME_ABOVE_THRESHOLD = 77
    RESERVED21 = 78
    RESERVED22 = 79
    RESERVED23 = 80
    RESERVED24 = 81
    DO0_TIME_BELOW_THRESHOLD = 82
    DO1_TIME_BELOW_THRESHOLD = 83
    DO2_TIME_BELOW_THRESHOLD = 84
    DO3_TIME_BELOW_THRESHOLD = 85
    RESERVED25 = 86
    RESERVED26 = 87
    RESERVED27 = 88
    RESERVED28 = 89
    RESERVED29 = 90


class AnalogInput(Device):
    """
    AnalogInput class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1236:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1236}, got {self.WHO_AM_I}")

    def read_acquisition_state(self) -> bool:
        """
        Reads the contents of the AcquisitionState register.

        Returns
        -------
        bool
            Value read from the AcquisitionState register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("AcquisitionState", reply.error_message)

        return reply.payload

    def write_acquisition_state(self, value: bool):
        """
        Writes a value to the AcquisitionState register.

        Parameters
        ----------
        value : bool
            Value to write to the AcquisitionState register.
        """
        address = 32
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("AcquisitionState", reply.error_message)
    def read_analog_data(self) -> AnalogDataPayload:
        """
        Reads the contents of the AnalogData register.

        Returns
        -------
        AnalogDataPayload
            Value read from the AnalogData register.
        """
        address = 33
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply.is_error:
            raise HarpReadException("AnalogData", reply.error_message)

        return reply.payload

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = 34
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalInputState", reply.error_message)

        return reply.payload

    def read_range_and_filter(self) -> RangeAndFilterConfig:
        """
        Reads the contents of the RangeAndFilter register.

        Returns
        -------
        RangeAndFilterConfig
            Value read from the RangeAndFilter register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("RangeAndFilter", reply.error_message)

        return reply.payload

    def write_range_and_filter(self, value: RangeAndFilterConfig):
        """
        Writes a value to the RangeAndFilter register.

        Parameters
        ----------
        value : RangeAndFilterConfig
            Value to write to the RangeAndFilter register.
        """
        address = 37
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("RangeAndFilter", reply.error_message)
    def read_sampling_rate(self) -> SamplingRateMode:
        """
        Reads the contents of the SamplingRate register.

        Returns
        -------
        SamplingRateMode
            Value read from the SamplingRate register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("SamplingRate", reply.error_message)

        return reply.payload

    def write_sampling_rate(self, value: SamplingRateMode):
        """
        Writes a value to the SamplingRate register.

        Parameters
        ----------
        value : SamplingRateMode
            Value to write to the SamplingRate register.
        """
        address = 38
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("SamplingRate", reply.error_message)
    def read_di0_trigger(self) -> TriggerConfig:
        """
        Reads the contents of the DI0Trigger register.

        Returns
        -------
        TriggerConfig
            Value read from the DI0Trigger register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DI0Trigger", reply.error_message)

        return reply.payload

    def write_di0_trigger(self, value: TriggerConfig):
        """
        Writes a value to the DI0Trigger register.

        Parameters
        ----------
        value : TriggerConfig
            Value to write to the DI0Trigger register.
        """
        address = 39
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DI0Trigger", reply.error_message)
    def read_do0_sync(self) -> SyncConfig:
        """
        Reads the contents of the DO0Sync register.

        Returns
        -------
        SyncConfig
            Value read from the DO0Sync register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO0Sync", reply.error_message)

        return reply.payload

    def write_do0_sync(self, value: SyncConfig):
        """
        Writes a value to the DO0Sync register.

        Parameters
        ----------
        value : SyncConfig
            Value to write to the DO0Sync register.
        """
        address = 40
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO0Sync", reply.error_message)
    def read_do0_pulse_width(self) -> int:
        """
        Reads the contents of the DO0PulseWidth register.

        Returns
        -------
        int
            Value read from the DO0PulseWidth register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO0PulseWidth", reply.error_message)

        return reply.payload

    def write_do0_pulse_width(self, value: int):
        """
        Writes a value to the DO0PulseWidth register.

        Parameters
        ----------
        value : int
            Value to write to the DO0PulseWidth register.
        """
        address = 41
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO0PulseWidth", reply.error_message)
    def read_digital_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputSet register.
        """
        address = 42
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
        address = 42
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
        address = 43
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
        address = 43
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputClear", reply.error_message)
    def read_digital_output_toggle(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputToggle register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputToggle register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalOutputToggle", reply.error_message)

        return reply.payload

    def write_digital_output_toggle(self, value: DigitalOutputs):
        """
        Writes a value to the DigitalOutputToggle register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputToggle register.
        """
        address = 44
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputToggle", reply.error_message)
    def read_digital_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputState register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DigitalOutputState", reply.error_message)

        return reply.payload

    def write_digital_output_state(self, value: DigitalOutputs):
        """
        Writes a value to the DigitalOutputState register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputState register.
        """
        address = 45
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DigitalOutputState", reply.error_message)
    def read_sync_output(self) -> StartSyncOutputTarget:
        """
        Reads the contents of the SyncOutput register.

        Returns
        -------
        StartSyncOutputTarget
            Value read from the SyncOutput register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("SyncOutput", reply.error_message)

        return reply.payload

    def write_sync_output(self, value: StartSyncOutputTarget):
        """
        Writes a value to the SyncOutput register.

        Parameters
        ----------
        value : StartSyncOutputTarget
            Value to write to the SyncOutput register.
        """
        address = 48
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("SyncOutput", reply.error_message)
    def read_do0_target_channel(self) -> AdcChannel:
        """
        Reads the contents of the DO0TargetChannel register.

        Returns
        -------
        AdcChannel
            Value read from the DO0TargetChannel register.
        """
        address = 58
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO0TargetChannel", reply.error_message)

        return reply.payload

    def write_do0_target_channel(self, value: AdcChannel):
        """
        Writes a value to the DO0TargetChannel register.

        Parameters
        ----------
        value : AdcChannel
            Value to write to the DO0TargetChannel register.
        """
        address = 58
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO0TargetChannel", reply.error_message)
    def read_do1_target_channel(self) -> AdcChannel:
        """
        Reads the contents of the DO1TargetChannel register.

        Returns
        -------
        AdcChannel
            Value read from the DO1TargetChannel register.
        """
        address = 59
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO1TargetChannel", reply.error_message)

        return reply.payload

    def write_do1_target_channel(self, value: AdcChannel):
        """
        Writes a value to the DO1TargetChannel register.

        Parameters
        ----------
        value : AdcChannel
            Value to write to the DO1TargetChannel register.
        """
        address = 59
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO1TargetChannel", reply.error_message)
    def read_do2_target_channel(self) -> AdcChannel:
        """
        Reads the contents of the DO2TargetChannel register.

        Returns
        -------
        AdcChannel
            Value read from the DO2TargetChannel register.
        """
        address = 60
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO2TargetChannel", reply.error_message)

        return reply.payload

    def write_do2_target_channel(self, value: AdcChannel):
        """
        Writes a value to the DO2TargetChannel register.

        Parameters
        ----------
        value : AdcChannel
            Value to write to the DO2TargetChannel register.
        """
        address = 60
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO2TargetChannel", reply.error_message)
    def read_do3_target_channel(self) -> AdcChannel:
        """
        Reads the contents of the DO3TargetChannel register.

        Returns
        -------
        AdcChannel
            Value read from the DO3TargetChannel register.
        """
        address = 61
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply.is_error:
            raise HarpReadException("DO3TargetChannel", reply.error_message)

        return reply.payload

    def write_do3_target_channel(self, value: AdcChannel):
        """
        Writes a value to the DO3TargetChannel register.

        Parameters
        ----------
        value : AdcChannel
            Value to write to the DO3TargetChannel register.
        """
        address = 61
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply.is_error:
            raise HarpWriteException("DO3TargetChannel", reply.error_message)
    def read_do0_threshold(self) -> int:
        """
        Reads the contents of the DO0Threshold register.

        Returns
        -------
        int
            Value read from the DO0Threshold register.
        """
        address = 66
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply.is_error:
            raise HarpReadException("DO0Threshold", reply.error_message)

        return reply.payload

    def write_do0_threshold(self, value: int):
        """
        Writes a value to the DO0Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO0Threshold register.
        """
        address = 66
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply.is_error:
            raise HarpWriteException("DO0Threshold", reply.error_message)
    def read_do1_threshold(self) -> int:
        """
        Reads the contents of the DO1Threshold register.

        Returns
        -------
        int
            Value read from the DO1Threshold register.
        """
        address = 67
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply.is_error:
            raise HarpReadException("DO1Threshold", reply.error_message)

        return reply.payload

    def write_do1_threshold(self, value: int):
        """
        Writes a value to the DO1Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO1Threshold register.
        """
        address = 67
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply.is_error:
            raise HarpWriteException("DO1Threshold", reply.error_message)
    def read_do2_threshold(self) -> int:
        """
        Reads the contents of the DO2Threshold register.

        Returns
        -------
        int
            Value read from the DO2Threshold register.
        """
        address = 68
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply.is_error:
            raise HarpReadException("DO2Threshold", reply.error_message)

        return reply.payload

    def write_do2_threshold(self, value: int):
        """
        Writes a value to the DO2Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO2Threshold register.
        """
        address = 68
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply.is_error:
            raise HarpWriteException("DO2Threshold", reply.error_message)
    def read_do3_threshold(self) -> int:
        """
        Reads the contents of the DO3Threshold register.

        Returns
        -------
        int
            Value read from the DO3Threshold register.
        """
        address = 69
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply.is_error:
            raise HarpReadException("DO3Threshold", reply.error_message)

        return reply.payload

    def write_do3_threshold(self, value: int):
        """
        Writes a value to the DO3Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO3Threshold register.
        """
        address = 69
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply.is_error:
            raise HarpWriteException("DO3Threshold", reply.error_message)
    def read_do0_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO0TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO0TimeAboveThreshold register.
        """
        address = 74
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO0TimeAboveThreshold", reply.error_message)

        return reply.payload

    def write_do0_time_above_threshold(self, value: int):
        """
        Writes a value to the DO0TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO0TimeAboveThreshold register.
        """
        address = 74
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO0TimeAboveThreshold", reply.error_message)
    def read_do1_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO1TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO1TimeAboveThreshold register.
        """
        address = 75
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO1TimeAboveThreshold", reply.error_message)

        return reply.payload

    def write_do1_time_above_threshold(self, value: int):
        """
        Writes a value to the DO1TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO1TimeAboveThreshold register.
        """
        address = 75
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO1TimeAboveThreshold", reply.error_message)
    def read_do2_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO2TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO2TimeAboveThreshold register.
        """
        address = 76
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO2TimeAboveThreshold", reply.error_message)

        return reply.payload

    def write_do2_time_above_threshold(self, value: int):
        """
        Writes a value to the DO2TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO2TimeAboveThreshold register.
        """
        address = 76
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO2TimeAboveThreshold", reply.error_message)
    def read_do3_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO3TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO3TimeAboveThreshold register.
        """
        address = 77
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO3TimeAboveThreshold", reply.error_message)

        return reply.payload

    def write_do3_time_above_threshold(self, value: int):
        """
        Writes a value to the DO3TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO3TimeAboveThreshold register.
        """
        address = 77
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO3TimeAboveThreshold", reply.error_message)
    def read_do0_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO0TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO0TimeBelowThreshold register.
        """
        address = 82
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO0TimeBelowThreshold", reply.error_message)

        return reply.payload

    def write_do0_time_below_threshold(self, value: int):
        """
        Writes a value to the DO0TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO0TimeBelowThreshold register.
        """
        address = 82
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO0TimeBelowThreshold", reply.error_message)
    def read_do1_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO1TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO1TimeBelowThreshold register.
        """
        address = 83
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO1TimeBelowThreshold", reply.error_message)

        return reply.payload

    def write_do1_time_below_threshold(self, value: int):
        """
        Writes a value to the DO1TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO1TimeBelowThreshold register.
        """
        address = 83
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO1TimeBelowThreshold", reply.error_message)
    def read_do2_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO2TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO2TimeBelowThreshold register.
        """
        address = 84
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO2TimeBelowThreshold", reply.error_message)

        return reply.payload

    def write_do2_time_below_threshold(self, value: int):
        """
        Writes a value to the DO2TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO2TimeBelowThreshold register.
        """
        address = 84
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO2TimeBelowThreshold", reply.error_message)
    def read_do3_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO3TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO3TimeBelowThreshold register.
        """
        address = 85
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply.is_error:
            raise HarpReadException("DO3TimeBelowThreshold", reply.error_message)

        return reply.payload

    def write_do3_time_below_threshold(self, value: int):
        """
        Writes a value to the DO3TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO3TimeBelowThreshold register.
        """
        address = 85
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply.is_error:
            raise HarpWriteException("DO3TimeBelowThreshold", reply.error_message)

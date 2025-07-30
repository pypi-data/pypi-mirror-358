import time
from statistics import mean

from harp.communication.device import Device
from harp.protocol import MessageType, OperationMode, PayloadType
from harp.protocol.messages import HarpMessage

SERIAL_PORT = (
    "/dev/ttyUSB0"  # or "COMx" in Windows ("x" is the number of the serial port)
)

# Open serial connection and save communication to a file
device = Device(SERIAL_PORT)

# Display device's info on screen
device.info()

reply = device.set_mode(OperationMode.ACTIVE)
print(reply)

# calculate the average time to read a register
latencies = []
num_commands = 10000

for _ in range(num_commands):
    start = time.perf_counter()
    # LoadCells define only Cells data and ignoring the rest of the events
    reply = device.send(HarpMessage.create(MessageType.WRITE, 90, PayloadType.U8, 1))
    # AnalogInput change to 2KHz sampling rate
    # reply = device.send(HarpMessage.create(MessageType.WRITE, 38, PayloadType.U8, 1))
    end = time.perf_counter()
    latencies.append(end - start)

avg_latency = mean(latencies)
throughput = num_commands / sum(latencies)

print(f"Average latency: {avg_latency * 1000:.2f} ms")
print(f"Total time for {num_commands} commands: {sum(latencies) * 1000:.2f} ms")
print(f"Approximate throughput: {throughput:.2f} messages/sec")

# LoadCells define only Cells data and ignoring the rest of the events
reply = device.send(HarpMessage.create(MessageType.WRITE, 90, PayloadType.U8, 1))
# AnalogInput change to 2KHz sampling rate
# reply = device.send(HarpMessage.create(MessageType.WRITE, 38, PayloadType.U8, 1))

reply = device.send(HarpMessage.create(MessageType.WRITE, 32, PayloadType.U8, 1))

i = 0

event_latencies = []
last_event_time = None

print("Starting to read events...")

while True:
    for event in device.get_events():
        current_time = time.perf_counter()
        if last_event_time is not None:
            event_latencies.append(current_time - last_event_time)
        last_event_time = current_time

        i += 1
        if i == 100000:
            avg_event_latency = mean(event_latencies) if event_latencies else 0
            throughput = (
                len(event_latencies) / sum(event_latencies) if event_latencies else 0
            )
            print(f"Average event interval: {avg_event_latency * 1000:.2f} ms")
            print(f"Approximate event throughput: {throughput:.2f} events/sec")
            print(f"Total events: {len(event_latencies)}")
            print(f"Total time: {sum(event_latencies) * 1000:.2f} ms")

            exit(0)
        # print(event.payload)


device.disconnect()

# # Dump device's registers
# reg_dump = device.dump_registers()
# for reg_reply in reg_dump:
#     print(reg_reply)
#     print()

# # Close connection
# device.disconnect

# harp.devices

This repository contains multiple Python packages for interacting with various Harp hardware devices. Each subdirectory corresponds to a different device and provides a Python interface for communication and control using the Harp protocol.

## Repository Structure

- Each `harp.<device>` folder is a standalone Python package for a specific device (e.g., analog input, audio switch, behavior, camera controller, current driver, LED array, load cells, olfactometer, RGB array, sound card, synchronizer, syringe pump).
- Each package includes its own documentation, usage examples, and installation instructions.
- All packages are maintained by the Hardware and Software Platform, Champalimaud Foundation.

## Getting Started

To use a specific device package, refer to the README in the corresponding subdirectory (e.g., `harp.analoginput/README.md`). Each package can be installed individually using `pip` or `uv`.

Example:
```bash
uv add harp.analoginput

# or if you prefer to use pip, you can install the package directly
pip install harp.analoginput
```

## Documentation

Comprehensive documentation for each device package is available online. See the links in each package's README or visit the [harp.devices GitHub repository](https://github.com/fchampalimaud/harp.devices/) for more information.

## License

All packages in this repository are licensed under the MIT License. See the `LICENSE` file in each package for details.
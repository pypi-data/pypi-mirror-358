# SIRF Config

A Python package for managing scanner and reconstruction configurations for SIRF SPECT/PET workflows.

[![PyPI version](https://badge.fury.io/py/sirf-config.svg)](https://badge.fury.io/py/sirf-config)
[![Python versions](https://img.shields.io/pypi/pyversions/sirf-config.svg)](https://pypi.org/project/sirf-config/)
[![License](https://img.shields.io/github/license/yourusername/sirf-config.svg)](https://github.com/yourusername/sirf-config/blob/main/LICENSE)

## Features

- **Centralized Configuration**: Manage scanner specifications, radionuclide properties, and reconstruction protocols in YAML files
- **Type Safety**: Full type hints and validation for configuration parameters
- **Extensible**: Easy to add new scanners, radionuclides, and protocols
- **SIRF Integration**: Drop-in replacement for manual parameter management in SIRF workflows
- **Default Configurations**: Includes configurations for common scanners (GE Discovery, Mediso AnyScan Trio)

## Quick Start

### Installation

```bash
pip install sirf-config
```

### Basic Usage

```python
from sirf_config import get_y90_spect_params, ConfigLoader

# Quick Y-90 SPECT reconstruction parameters
params = get_y90_spect_params('ge_670', '/path/to/data')
print(params)
# {'data_path': '/path/to/data', 'num_subsets': 12, 'num_epochs': 5, 
#  'resolution_model': (1.68, 0.03, False), 'smoothing_kernel': (6.8, 6.8, 6.8)}

# Advanced configuration management
config = ConfigLoader()
available_scanners = config.list_scanners()
protocol_config = config.get_protocol_config('y90_mediso_spect')
```

### Command Line Usage

Create a user configuration template:
```bash
python -m sirf_config.utils --create-template ./my_configs
```

Validate configuration files:
```bash
python -m sirf_config.utils --validate ./my_configs
```

List available configurations:
```bash
python -m sirf_config.utils --list-configs
```

## Supported Scanners

The package includes default configurations for:

### SPECT Scanners
- **GE Discovery 670**: `ge_discovery_670`
- **Mediso AnyScan Trio**: `mediso_anyscan_trio_spect`

### PET Scanners  
- **GE Discovery 690**: `ge_discovery_690`
- **Mediso AnyScan Trio**: `mediso_anyscan_trio_pet`

### Radionuclides
- **Yttrium-90**: `y90` (bremsstrahlung imaging)

## Configuration Structure

The package uses three YAML configuration files:

1. **`scanners.yaml`**: Scanner technical specifications
2. **`radionuclides.yaml`**: Radionuclide properties
3. **`protocols.yaml`**: Pre-configured scanner+radionuclide combinations

### Example Scanner Configuration

```yaml
scanners:
  ge_discovery_670:
    name: "GE Discovery 670"
    modality: "SPECT"
    psf:
      sigma_0: 1.68  # mm
      alpha: 0.03
      full_3d: false
    bremsstrahlung:
      smoothing_fwhm: [6.8, 6.8, 6.8]  # mm isotropic
    default_params:
      num_subsets: 12
      num_epochs: 2
```

## Integration with SIRF Scripts

### SPECT Reconstruction

```python
#!/usr/bin/env python3
import argparse
from sirf_config import get_y90_spect_params
from sirf.STIR import *

parser = argparse.ArgumentParser()
parser.add_argument('--scanner', type=str, help='Scanner: ge_670, mediso')
parser.add_argument('--data_path', type=str, required=True)
args = parser.parse_args()

# Get configuration parameters
params = get_y90_spect_params(args.scanner, args.data_path)

# Use in SIRF reconstruction
spect_mat = SPECTUBMatrix()
spect_mat.set_resolution_model(*params['resolution_model'])
# ... rest of reconstruction
```

### PET Reconstruction

```python
from sirf_config import get_y90_pet_params

params = get_y90_pet_params('ge_690', '/path/to/data')
gauss = SeparableGaussianImageFilter()
gauss.set_fwhms(params['psf_kernel'])
```

## Adding Custom Configurations

### 1. Create Custom Configuration Directory

```python
from sirf_config import create_user_config_template

config_dir = create_user_config_template('./my_custom_configs')
```

### 2. Edit Configuration Files

Add your scanner to `scanners.yaml`:

```yaml
scanners:
  my_custom_scanner:
    name: "My Custom Scanner"
    modality: "SPECT"
    psf:
      sigma_0: 1.5
      alpha: 0.025
      full_3d: false
    default_params:
      num_subsets: 16
      num_epochs: 3
```

Add a protocol to `protocols.yaml`:

```yaml
protocols:
  y90_my_custom_spect:
    scanner: "my_custom_scanner"
    radionuclide: "y90"
    description: "Y-90 SPECT on My Custom Scanner"
    reconstruction_params:
      num_subsets: 16
      num_epochs: 5
      resolution_model: [1.5, 0.025, false]
      smoothing_kernel: [7.0, 7.0, 7.0]
```

### 3. Use Custom Configurations

```python
from sirf_config import ConfigLoader

config = ConfigLoader('./my_custom_configs')
params = config.get_reconstruction_params('y90_my_custom_spect')
```

## API Reference

### Core Classes

- **`ConfigLoader`**: Main configuration management class
- **`create_reconstruction_args()`**: Convert configurations to reconstruction parameters

### Convenience Functions

- **`get_y90_spect_params(scanner, data_path)`**: Quick Y-90 SPECT parameters
- **`get_y90_pet_params(scanner, data_path)`**: Quick Y-90 PET parameters

### Utilities

- **`get_default_config_dir()`**: Get path to package default configurations
- **`create_user_config_template()`**: Create user configuration template
- **`validate_config_files()`**: Validate configuration file syntax and structure

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/yourusername/sirf-config.git
cd sirf-config
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
isort src/
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{sirf_config,
  title={SIRF Config: Configuration Management for SIRF Workflows},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/sirf-config}
}
```

## Acknowledgments

- Built for use with [SIRF (Synergistic Image Reconstruction Framework)](https://github.com/SyneRBI/SIRF)
- Supports medical imaging workflows for SPECT and PET reconstruction
# SIRF Config Documentation

Welcome to the SIRF Config documentation. This package provides configuration management for SIRF SPECT and PET reconstruction workflows.

## Quick Start

### Installation
```bash
pip install sirf-config
```

### Basic Usage
```python
from sirf_config import get_y90_spect_params, get_y90_pet_params

# Get Y-90 SPECT parameters for Mediso scanner
spect_params = get_y90_spect_params('mediso')

# Get Y-90 PET parameters for GE scanner  
pet_params = get_y90_pet_params('ge_690')
```

## Documentation Structure

- **[API Reference](api.md)** - Complete API documentation
- **[Configuration Guide](configuration_guide.md)** - How to create and customize configurations
- **Examples** - See the `examples/` directory for complete usage examples

## Key Concepts

### Scanners
Scanners define the technical specifications of imaging equipment:
- PSF (Point Spread Function) parameters
- Default reconstruction settings
- Modality-specific configurations

### Radionuclides  
Radionuclides define the properties of imaging isotopes:
- Physical characteristics (half-life, emission type)
- Energy spectrum information
- Reconstruction considerations

### Protocols
Protocols combine scanners and radionuclides with specific reconstruction parameters:
- Scanner + radionuclide combinations
- Optimized reconstruction parameters
- Default data paths for common datasets

## Supported Configurations

### Scanners
- **GE Discovery 670** (SPECT)
- **GE Discovery 690** (PET)  
- **Mediso AnyScan Trio** (SPECT/PET)

### Radionu
# API Reference

Complete API documentation for SIRF Config package.

## Core Classes

### ConfigLoader

Main class for loading and managing configurations.

```python
class ConfigLoader:
    def __init__(self, config_dir: Optional[str] = None)
```

**Parameters:**
- `config_dir` (str, optional): Directory containing configuration files. If None, uses package default configurations.

#### Methods

##### `get_scanner_config(scanner_id: str) -> Dict[str, Any]`
Get configuration for a specific scanner.

**Parameters:**
- `scanner_id` (str): Scanner identifier

**Returns:**
- `Dict[str, Any]`: Scanner configuration dictionary

**Raises:**
- `ValueError`: If scanner not found

**Example:**
```python
config = ConfigLoader()
scanner_config = config.get_scanner_config('ge_discovery_670')
print(scanner_config['name'])  # "GE Discovery 670"
```

##### `get_radionuclide_config(radionuclide_id: str) -> Dict[str, Any]`
Get configuration for a specific radionuclide.

**Parameters:**
- `radionuclide_id` (str): Radionuclide identifier

**Returns:**
- `Dict[str, Any]`: Radionuclide configuration dictionary

##### `get_protocol_config(protocol_id: str) -> Dict[str, Any]`
Get configuration for a specific protocol.

**Parameters:**
- `protocol_id` (str): Protocol identifier

**Returns:**
- `Dict[str, Any]`: Protocol configuration with merged scanner and radionuclide configs

##### `list_scanners() -> List[str]`
List available scanner IDs.

**Returns:**
- `List[str]`: List of scanner identifiers

##### `list_radionuclides() -> List[str]`
List available radionuclide IDs.

**Returns:**
- `List[str]`: List of radionuclide identifiers

##### `list_protocols() -> List[str]`
List available protocol IDs.

**Returns:**
- `List[str]`: List of protocol identifiers

##### `get_reconstruction_params(protocol_id: str) -> Dict[str, Any]`
Get reconstruction parameters for a protocol.

**Parameters:**
- `protocol_id` (str): Protocol identifier

**Returns:**
- `Dict[str, Any]`: Merged reconstruction parameters (scanner defaults + protocol overrides)

## Core Functions

### create_reconstruction_args

```python
def create_reconstruction_args(
    config_loader: ConfigLoader, 
    protocol_id: str, 
    data_path: Optional[str] = None,
    output_path: Optional[str] = None,
    **overrides
) -> Dict[str, Any]
```

Create reconstruction arguments from protocol configuration.

**Parameters:**
- `config_loader` (ConfigLoader): Initialized ConfigLoader instance
- `protocol_id` (str): Protocol identifier
- `data_path` (str, optional): Path to data directory. Uses protocol default if None.
- `output_path` (str, optional): Output path. Defaults to data_path.
- `**overrides`: Additional parameters to override

**Returns:**
- `Dict[str, Any]`: Dictionary of reconstruction arguments

**Example:**
```python
config = ConfigLoader()
args = create_reconstruction_args(
    config, 'y90_mediso_spect',
    data_path='/custom/data',
    num_epochs=10  # Override
)
```

## Convenience Functions

### get_y90_spect_params

```python
def get_y90_spect_params(scanner: str, data_path: Optional[str] = None) -> Dict[str, Any]
```

Convenience function for Y-90 SPECT reconstruction parameters.

**Parameters:**
- `scanner` (str): Scanner identifier ('ge_670', 'mediso', etc.)
- `data_path` (str, optional): Data path. Uses protocol default if None.

**Returns:**
- `Dict[str, Any]`: Reconstruction parameters

**Supported Scanners:**
- `'ge_670'`, `'ge_discovery_670'` → GE Discovery 670
- `'mediso'`, `'mediso_anyscan_trio'`, `'anyscan'` → Mediso AnyScan Trio

**Example:**
```python
# Use default data path
params = get_y90_spect_params('mediso')

# Custom data path
params = get_y90_spect_params('mediso', '/my/data')
```

### get_y90_pet_params

```python
def get_y90_pet_params(scanner: str, data_path: Optional[str] = None) -> Dict[str, Any]
```

Convenience function for Y-90 PET reconstruction parameters.

**Parameters:**
- `scanner` (str): Scanner identifier ('ge_690', 'mediso', etc.)
- `data_path` (str, optional): Data path. Uses protocol default if None.

**Returns:**
- `Dict[str, Any]`: Reconstruction parameters

**Supported Scanners:**
- `'ge_690'`, `'ge_discovery_690'` → GE Discovery 690
- `'mediso'`, `'mediso_anyscan_trio'`, `'anyscan'` → Mediso AnyScan Trio

## Utility Functions

### get_default_config_dir

```python
def get_default_config_dir() -> Path
```

Get the path to the default configuration files included with the package.

**Returns:**
- `Path`: Path to default configuration directory

### get_user_config_dir

```python
def get_user_config_dir() -> Path
```

Get the recommended user configuration directory.

**Returns:**
- `Path`: Path to user config directory (`~/.config/sirf_config` on Unix, `%LOCALAPPDATA%/sirf_config` on Windows)

### create_user_config_template

```python
def create_user_config_template(target_dir: Optional[str] = None, force: bool = False) -> Path
```

Create a user configuration template by copying default configs.

**Parameters:**
- `target_dir` (str, optional): Target directory. Defaults to user config dir.
- `force` (bool): Overwrite existing files if True

**Returns:**
- `Path`: Path to created configuration directory

### validate_config_files

```python
def validate_config_files(config_dir: str) -> Dict[str, Any]
```

Validate configuration files in a directory.

**Parameters:**
- `config_dir` (str): Path to configuration directory

**Returns:**
- `Dict[str, Any]`: Validation results with keys:
  - `valid` (bool): Whether all files are valid
  - `errors` (List[str]): List of error messages
  - `warnings` (List[str]): List of warning messages
  - `files_checked` (List[str]): List of files that were checked

### list_available_configs

```python
def list_available_configs() -> Dict[str, List[str]]
```

List all available scanners, radionuclides, and protocols from default configs.

**Returns:**
- `Dict[str, List[str]]`: Dictionary with lists of available configurations

## Data Structures

### Scanner Configuration

```yaml
scanner_id:
  name: "Scanner Name"
  modality: "SPECT" | "PET"
  psf:
    # For SPECT:
    sigma_0: float  # mm
    alpha: float
    full_3d: bool
    # For PET:
    fwhm: [float, float, float]  # mm [z, y, x]
    type: "gaussian"
  bremsstrahlung:  # Optional, for Y-90
    smoothing_fwhm: [float, float, float]  # mm
  default_params:
    num_subsets: int
    num_epochs: int
    # Additional scanner-specific params
```

### Radionuclide Configuration

```yaml
radionuclide_id:
  name: "Radionuclide Name"
  half_life_hours: float
  emission_type: "gamma" | "beta_minus" | "positron"
  bremsstrahlung: bool  # Optional
  energy_spectrum:
    type: "monoenergetic" | "continuous"
    energy_kev: float  # For monoenergetic
    max_energy_kev: float  # For continuous
    mean_energy_kev: float  # For continuous
  reconstruction:
    requires_high_energy_collimator: bool
    typical_smoothing: bool
    scatter_correction: "required" | "recommended" | "optional"
```

### Protocol Configuration

```yaml
protocol_id:
  scanner: "scanner_id"
  radionuclide: "radionuclide_id"
  description: "Protocol description"
  default_data_path: "/path/to/default/data"  # Optional
  reconstruction_params:
    # SPECT parameters:
    resolution_model: [float, float, bool]  # [sigma_0, alpha, full_3d]
    smoothing_kernel: [float, float, float]  # mm
    apply_smoothing: bool
    # PET parameters:
    psf_kernel: [float, float, float]  # mm
    gpu: bool
    # Common parameters:
    num_subsets: int
    num_epochs: int
```

## Return Value Formats

### Reconstruction Parameters Dictionary

The functions return a dictionary with these keys:

**Common Parameters:**
- `data_path` (str): Path to data directory
- `output_path` (str): Path for output files
- `num_subsets` (int): Number of OSEM subsets
- `num_epochs` (int): Number of OSEM epochs

**SPECT-Specific Parameters:**
- `resolution_model` (Tuple[float, float, bool]): [sigma_0, alpha, full_3d]
- `smoothing_kernel` (Tuple[float, float, float], optional): Smoothing FWHM in mm

**PET-Specific Parameters:**
- `psf_kernel` (Tuple[float, float, float]): PSF FWHM in mm [z, y, x]
- `gpu` (bool): Whether to use GPU acceleration

## Error Handling

### Common Exceptions

- **`ValueError`**: Raised when scanner, radionuclide, or protocol not found
- **`FileNotFoundError`**: Raised when configuration files are missing
- **`yaml.YAMLError`**: Raised when configuration files have invalid YAML syntax

### Example Error Handling

```python
try:
    params = get_y90_spect_params('unknown_scanner')
except ValueError as e:
    print(f"Scanner not found: {e}")
    # Handle error or use fallback

try:
    config = ConfigLoader('/invalid/path')
except FileNotFoundError:
    print("Configuration files not found")
    # Use default configurations
    config = ConfigLoader()
```

## Type Hints

The package includes comprehensive type hints for better IDE support and type checking:

```python
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# All functions and methods include proper type annotations
def get_y90_spect_params(scanner: str, data_path: Optional[str] = None) -> Dict[str, Any]:
    ...
```
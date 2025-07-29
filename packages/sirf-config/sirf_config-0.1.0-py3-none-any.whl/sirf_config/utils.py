"""
Utility functions for SIRF configuration management.
"""

import os
import shutil
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
import pkg_resources


def get_default_config_dir() -> Path:
    """
    Get the path to the default configuration files included with the package.
    
    Returns:
        Path to the default configuration directory
    """
    try:
        # Try using importlib.resources (Python 3.9+)
        from importlib import resources
        return resources.files('sirf_config') / 'default_configs'
    except (ImportError, AttributeError):
        # Fallback for older Python versions
        return Path(pkg_resources.resource_filename('sirf_config', 'default_configs'))


def get_user_config_dir() -> Path:
    """
    Get the recommended user configuration directory.
    
    Returns:
        Path to user's config directory (~/.config/sirf_config)
    """
    home = Path.home()
    if os.name == 'nt':  # Windows
        config_dir = home / 'AppData' / 'Local' / 'sirf_config'
    else:  # Unix-like
        config_dir = home / '.config' / 'sirf_config'
    return config_dir


def create_user_config_template(target_dir: Optional[str] = None, force: bool = False) -> Path:
    """
    Create a user configuration template by copying default configs.
    
    Args:
        target_dir: Target directory (defaults to user config dir)
        force: Overwrite existing files if True
    
    Returns:
        Path to created configuration directory
    """
    if target_dir is None:
        target_path = get_user_config_dir()
    else:
        target_path = Path(target_dir)
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Copy default config files
    default_dir = get_default_config_dir()
    config_files = ['scanners.yaml', 'radionuclides.yaml', 'protocols.yaml']
    
    for config_file in config_files:
        source_file = default_dir / config_file
        target_file = target_path / config_file
        
        if target_file.exists() and not force:
            print(f"Skipping {config_file} (already exists). Use force=True to overwrite.")
            continue
            
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"Created {target_file}")
        else:
            print(f"Warning: Default config file {source_file} not found")
    
    return target_path


def validate_config_files(config_dir: str) -> Dict[str, Any]:
    """
    Validate configuration files in a directory.
    
    Args:
        config_dir: Path to configuration directory
    
    Returns:
        Dictionary with validation results
    """
    config_path = Path(config_dir)
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'files_checked': []
    }
    
    required_files = ['scanners.yaml', 'radionuclides.yaml', 'protocols.yaml']
    
    for config_file in required_files:
        file_path = config_path / config_file
        results['files_checked'].append(str(file_path))
        
        if not file_path.exists():
            results['valid'] = False
            results['errors'].append(f"Missing required file: {config_file}")
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                
            # Basic structure validation
            if config_file == 'scanners.yaml':
                _validate_scanners_config(data, results)
            elif config_file == 'radionuclides.yaml':
                _validate_radionuclides_config(data, results)
            elif config_file == 'protocols.yaml':
                _validate_protocols_config(data, results)
                
        except yaml.YAMLError as e:
            results['valid'] = False
            results['errors'].append(f"YAML parsing error in {config_file}: {e}")
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Error reading {config_file}: {e}")
    
    return results


def _validate_scanners_config(data: Dict[str, Any], results: Dict[str, Any]) -> None:
    """Validate scanners configuration structure."""
    if 'scanners' not in data:
        results['errors'].append("scanners.yaml missing 'scanners' key")
        return
    
    for scanner_id, scanner_config in data['scanners'].items():
        if 'name' not in scanner_config:
            results['warnings'].append(f"Scanner {scanner_id} missing 'name'")
        
        if 'modality' not in scanner_config:
            results['errors'].append(f"Scanner {scanner_id} missing 'modality'")
        elif scanner_config['modality'] not in ['PET', 'SPECT']:
            results['errors'].append(f"Scanner {scanner_id} invalid modality: {scanner_config['modality']}")
        
        if 'psf' not in scanner_config:
            results['warnings'].append(f"Scanner {scanner_id} missing 'psf' configuration")


def _validate_radionuclides_config(data: Dict[str, Any], results: Dict[str, Any]) -> None:
    """Validate radionuclides configuration structure."""
    if 'radionuclides' not in data:
        results['errors'].append("radionuclides.yaml missing 'radionuclides' key")
        return
    
    for radio_id, radio_config in data['radionuclides'].items():
        if 'name' not in radio_config:
            results['warnings'].append(f"Radionuclide {radio_id} missing 'name'")
        
        if 'half_life_hours' not in radio_config:
            results['warnings'].append(f"Radionuclide {radio_id} missing 'half_life_hours'")


def _validate_protocols_config(data: Dict[str, Any], results: Dict[str, Any]) -> None:
    """Validate protocols configuration structure."""
    if 'protocols' not in data:
        results['errors'].append("protocols.yaml missing 'protocols' key")
        return
    
    for protocol_id, protocol_config in data['protocols'].items():
        if 'scanner' not in protocol_config:
            results['errors'].append(f"Protocol {protocol_id} missing 'scanner'")
        
        if 'radionuclide' not in protocol_config:
            results['errors'].append(f"Protocol {protocol_id} missing 'radionuclide'")
        
        if 'description' not in protocol_config:
            results['warnings'].append(f"Protocol {protocol_id} missing 'description'")


def list_available_configs() -> Dict[str, List[str]]:
    """
    List all available scanners, radionuclides, and protocols from default configs.
    
    Returns:
        Dictionary with lists of available configurations
    """
    try:
        from .config_loader import ConfigLoader
        
        # Use default configs
        default_dir = get_default_config_dir()
        config = ConfigLoader(str(default_dir))
        
        return {
            'scanners': config.list_scanners(),
            'radionuclides': config.list_radionuclides(), 
            'protocols': config.list_protocols(),
        }
    except Exception as e:
        return {
            'error': f"Could not load default configurations: {e}",
            'scanners': [],
            'radionuclides': [],
            'protocols': [],
        }


def get_example_usage() -> str:
    """
    Get example usage code.
    
    Returns:
        String with example Python code
    """
    return '''
# Basic usage
from sirf_config import ConfigLoader, get_y90_spect_params

# Quick Y-90 SPECT parameters
params = get_y90_spect_params('ge_670', '/path/to/data')

# Full configuration management
config = ConfigLoader()  # Uses default configs
scanners = config.list_scanners()
protocol_params = config.get_reconstruction_params('y90_ge_670_spect')

# Custom config directory
custom_config = ConfigLoader('/path/to/custom/config')

# Create user config template
from sirf_config import create_user_config_template
config_dir = create_user_config_template()
print(f"Config template created at: {config_dir}")
'''


if __name__ == "__main__":
    # Command-line utility
    import argparse
    
    parser = argparse.ArgumentParser(description='SIRF Config Utilities')
    parser.add_argument('--create-template', type=str, 
                       help='Create config template in specified directory')
    parser.add_argument('--validate', type=str,
                       help='Validate config files in directory')
    parser.add_argument('--list-configs', action='store_true',
                       help='List available configurations')
    
    args = parser.parse_args()
    
    if args.create_template:
        config_dir = create_user_config_template(args.create_template)
        print(f"Configuration template created at: {config_dir}")
    
    elif args.validate:
        results = validate_config_files(args.validate)
        print(f"Validation results for {args.validate}:")
        print(f"Valid: {results['valid']}")
        if results['errors']:
            print("Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        if results['warnings']:
            print("Warnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")
    
    elif args.list_configs:
        configs = list_available_configs()
        if 'error' in configs:
            print(f"Error: {configs['error']}")
        else:
            print("Available configurations:")
            print(f"Scanners: {', '.join(configs['scanners'])}")
            print(f"Radionuclides: {', '.join(configs['radionuclides'])}")
            print(f"Protocols: {', '.join(configs['protocols'])}")
    
    else:
        print("SIRF Config package utilities")
        print("Use --help for available options")
        print("\nExample usage:")
        print(get_example_usage())
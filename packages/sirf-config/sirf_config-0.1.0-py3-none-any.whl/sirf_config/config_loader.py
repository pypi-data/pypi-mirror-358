# config_loader.py
"""
Configuration loader for SPECT/PET reconstruction parameters.
Loads scanner, radionuclide, and protocol configurations from YAML files.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Loads and manages scanner/radionuclide configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the config loader.
        
        Args:
            config_dir: Directory containing configuration files.
                       If None, uses package default configurations.
        """
        if config_dir is None:
            # Use package default configurations
            from .utils import get_default_config_dir
            self.config_dir = get_default_config_dir()
        else:
            self.config_dir = Path(config_dir)
        
        self._scanners = {}
        self._radionuclides = {}
        self._protocols = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load all configuration files."""
        # Load scanners
        scanners_file = self.config_dir / "scanners.yaml"
        if scanners_file.exists():
            with open(scanners_file, 'r') as f:
                data = yaml.safe_load(f)
                self._scanners = data.get('scanners', {})
        
        # Load radionuclides
        radionuclides_file = self.config_dir / "radionuclides.yaml"
        if radionuclides_file.exists():
            with open(radionuclides_file, 'r') as f:
                data = yaml.safe_load(f)
                self._radionuclides = data.get('radionuclides', {})
        
        # Load protocols
        protocols_file = self.config_dir / "protocols.yaml"
        if protocols_file.exists():
            with open(protocols_file, 'r') as f:
                data = yaml.safe_load(f)
                self._protocols = data.get('protocols', {})
    
    def get_scanner_config(self, scanner_id: str) -> Dict[str, Any]:
        """Get configuration for a specific scanner."""
        if scanner_id not in self._scanners:
            raise ValueError(f"Scanner '{scanner_id}' not found in configuration")
        return self._scanners[scanner_id]
    
    def get_radionuclide_config(self, radionuclide_id: str) -> Dict[str, Any]:
        """Get configuration for a specific radionuclide."""
        if radionuclide_id not in self._radionuclides:
            raise ValueError(f"Radionuclide '{radionuclide_id}' not found in configuration")
        return self._radionuclides[radionuclide_id]
    
    def get_protocol_config(self, protocol_id: str) -> Dict[str, Any]:
        """Get configuration for a specific protocol."""
        if protocol_id not in self._protocols:
            raise ValueError(f"Protocol '{protocol_id}' not found in configuration")
        
        protocol = self._protocols[protocol_id].copy()
        
        # Merge scanner and radionuclide configs
        scanner_id = protocol.get('scanner')
        radionuclide_id = protocol.get('radionuclide')
        
        if scanner_id:
            scanner_config = self.get_scanner_config(scanner_id)
            protocol['scanner_config'] = scanner_config
        
        if radionuclide_id:
            radionuclide_config = self.get_radionuclide_config(radionuclide_id)
            protocol['radionuclide_config'] = radionuclide_config
        
        return protocol
    
    def list_scanners(self) -> list:
        """List available scanner IDs."""
        return list(self._scanners.keys())
    
    def list_radionuclides(self) -> list:
        """List available radionuclide IDs."""
        return list(self._radionuclides.keys())
    
    def list_protocols(self) -> list:
        """List available protocol IDs."""
        return list(self._protocols.keys())
    
    def get_reconstruction_params(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get reconstruction parameters for a protocol.
        Combines default scanner params with protocol-specific overrides.
        """
        protocol = self.get_protocol_config(protocol_id)
        scanner_config = protocol.get('scanner_config', {})
        
        # Start with scanner defaults
        params = scanner_config.get('default_params', {}).copy()
        
        # Override with protocol-specific params
        protocol_params = protocol.get('reconstruction_params', {})
        params.update(protocol_params)
        
        return params


def create_reconstruction_args(config_loader: ConfigLoader, 
                             protocol_id: str, 
                             data_path: Optional[str] = None,
                             output_path: Optional[str] = None,
                             **overrides) -> Dict[str, Any]:
    """
    Create reconstruction arguments from protocol configuration.
    
    Args:
        config_loader: Initialized ConfigLoader instance
        protocol_id: Protocol identifier
        data_path: Path to data directory (uses protocol default if None)
        output_path: Output path (defaults to data_path)
        **overrides: Additional parameters to override
    
    Returns:
        Dictionary of reconstruction arguments
    """
    params = config_loader.get_reconstruction_params(protocol_id)
    protocol = config_loader.get_protocol_config(protocol_id)
    
    # Use provided data_path or protocol default
    if data_path is None:
        data_path = protocol.get('default_data_path')
        if data_path is None:
            raise ValueError(f"No data_path provided and protocol '{protocol_id}' has no default_data_path")
    
    # Build arguments dictionary
    args = {
        'data_path': data_path,
        'output_path': output_path or data_path,
        'num_subsets': params.get('num_subsets', 12),
        'num_epochs': params.get('num_epochs', 2),
    }
    
    # Add modality-specific parameters
    scanner_config = protocol.get('scanner_config', {})
    modality = scanner_config.get('modality', '').upper()
    
    if modality == 'SPECT':
        # SPECT-specific parameters
        if 'resolution_model' in params:
            args['resolution_model'] = tuple(params['resolution_model'])
        elif 'psf' in scanner_config:
            psf = scanner_config['psf']
            args['resolution_model'] = (
                psf.get('sigma_0', 1.22),
                psf.get('alpha', 0.031),
                psf.get('full_3d', False)
            )
        
        if params.get('apply_smoothing', False) and 'smoothing_kernel' in params:
            args['smoothing_kernel'] = tuple(params['smoothing_kernel'])
            
    elif modality == 'PET':
        # PET-specific parameters
        if 'psf_kernel' in params:
            args['psf_kernel'] = tuple(params['psf_kernel'])
        elif 'psf' in scanner_config:
            args['psf_kernel'] = tuple(scanner_config['psf']['fwhm'])
        
        args['gpu'] = params.get('gpu', True)
    
    # Apply any overrides
    args.update(overrides)
    
    return args


# Example usage functions
def get_y90_spect_params(scanner: str, data_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for Y-90 SPECT reconstruction parameters."""
    config = ConfigLoader()
    
    # Map scanner names to protocol IDs
    protocol_map = {
        'ge_670': 'y90_ge_670_spect',
        'ge_discovery_670': 'y90_ge_670_spect',
        'mediso': 'y90_mediso_spect',
        'mediso_anyscan_trio': 'y90_mediso_spect',
        'anyscan': 'y90_mediso_spect'
    }
    
    protocol_id = protocol_map.get(scanner.lower())
    if not protocol_id:
        raise ValueError(f"Unknown scanner: {scanner}. Available: {list(protocol_map.keys())}")
    
    return create_reconstruction_args(config, protocol_id, data_path)


def get_y90_pet_params(scanner: str, data_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for Y-90 PET reconstruction parameters."""
    config = ConfigLoader()
    
    protocol_map = {
        'ge_690': 'y90_ge_690_pet',
        'ge_discovery_690': 'y90_ge_690_pet',
        'mediso': 'y90_mediso_pet',
        'mediso_anyscan_trio': 'y90_mediso_pet',
        'anyscan': 'y90_mediso_pet'
    }
    
    protocol_id = protocol_map.get(scanner.lower())
    if not protocol_id:
        raise ValueError(f"Unknown scanner: {scanner}. Available: {list(protocol_map.keys())}")
    
    return create_reconstruction_args(config, protocol_id, data_path)


if __name__ == "__main__":
    # Example usage
    config = ConfigLoader()
    
    print("Available scanners:", config.list_scanners())
    print("Available protocols:", config.list_protocols())
    
    # Example: Get Y-90 SPECT parameters for GE Discovery 670
    try:
        params = get_y90_spect_params('ge_670', '/path/to/data')
        print("\nY-90 SPECT on GE 670 parameters:")
        for key, value in params.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
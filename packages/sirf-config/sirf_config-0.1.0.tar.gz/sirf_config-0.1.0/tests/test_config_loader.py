#!/usr/bin/env python3
"""
Tests for the ConfigLoader class.
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

from sirf_config import ConfigLoader, create_reconstruction_args
from sirf_config.utils import create_user_config_template, validate_config_files


@pytest.fixture
def temp_config_dir():
    """Create a temporary configuration directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test configuration files
        config_dir = Path(tmpdir)
        
        # Test scanners.yaml
        scanners_data = {
            'scanners': {
                'test_scanner': {
                    'name': 'Test Scanner',
                    'modality': 'SPECT',
                    'psf': {
                        'sigma_0': 1.5,
                        'alpha': 0.025,
                        'full_3d': False
                    },
                    'default_params': {
                        'num_subsets': 10,
                        'num_epochs': 3
                    }
                }
            }
        }
        
        # Test radionuclides.yaml
        radionuclides_data = {
            'radionuclides': {
                'test_radio': {
                    'name': 'Test Radionuclide',
                    'half_life_hours': 24.0,
                    'emission_type': 'gamma'
                }
            }
        }
        
        # Test protocols.yaml
        protocols_data = {
            'protocols': {
                'test_protocol': {
                    'scanner': 'test_scanner',
                    'radionuclide': 'test_radio',
                    'description': 'Test protocol',
                    'reconstruction_params': {
                        'num_subsets': 12,
                        'num_epochs': 5,
                        'resolution_model': [1.5, 0.025, False]
                    }
                }
            }
        }
        
        # Write test files
        with open(config_dir / 'scanners.yaml', 'w') as f:
            yaml.dump(scanners_data, f)
        
        with open(config_dir / 'radionuclides.yaml', 'w') as f:
            yaml.dump(radionuclides_data, f)
        
        with open(config_dir / 'protocols.yaml', 'w') as f:
            yaml.dump(protocols_data, f)
        
        yield str(config_dir)


class TestConfigLoader:
    """Test cases for ConfigLoader class."""
    
    def test_init_with_custom_config(self, temp_config_dir):
        """Test initialization with custom config directory."""
        config = ConfigLoader(temp_config_dir)
        assert config.config_dir == Path(temp_config_dir)
    
    def test_list_scanners(self, temp_config_dir):
        """Test listing available scanners."""
        config = ConfigLoader(temp_config_dir)
        scanners = config.list_scanners()
        assert 'test_scanner' in scanners
    
    def test_list_radionuclides(self, temp_config_dir):
        """Test listing available radionuclides."""
        config = ConfigLoader(temp_config_dir)
        radionuclides = config.list_radionuclides()
        assert 'test_radio' in radionuclides
    
    def test_list_protocols(self, temp_config_dir):
        """Test listing available protocols."""
        config = ConfigLoader(temp_config_dir)
        protocols = config.list_protocols()
        assert 'test_protocol' in protocols
    
    def test_get_scanner_config(self, temp_config_dir):
        """Test getting scanner configuration."""
        config = ConfigLoader(temp_config_dir)
        scanner_config = config.get_scanner_config('test_scanner')
        
        assert scanner_config['name'] == 'Test Scanner'
        assert scanner_config['modality'] == 'SPECT'
        assert scanner_config['psf']['sigma_0'] == 1.5
    
    def test_get_protocol_config(self, temp_config_dir):
        """Test getting protocol configuration."""
        config = ConfigLoader(temp_config_dir)
        protocol_config = config.get_protocol_config('test_protocol')
        
        assert protocol_config['description'] == 'Test protocol'
        assert protocol_config['scanner'] == 'test_scanner'
        assert protocol_config['scanner_config']['name'] == 'Test Scanner'
    
    def test_get_reconstruction_params(self, temp_config_dir):
        """Test getting reconstruction parameters."""
        config = ConfigLoader(temp_config_dir)
        params = config.get_reconstruction_params('test_protocol')
        
        # Should merge scanner defaults with protocol overrides
        assert params['num_subsets'] == 12  # Protocol override
        assert params['num_epochs'] == 5    # Protocol override
        assert params['resolution_model'] == [1.5, 0.025, False]
    
    def test_scanner_not_found(self, temp_config_dir):
        """Test error when scanner not found."""
        config = ConfigLoader(temp_config_dir)
        with pytest.raises(ValueError, match="Scanner 'nonexistent' not found"):
            config.get_scanner_config('nonexistent')
    
    def test_protocol_not_found(self, temp_config_dir):
        """Test error when protocol not found."""
        config = ConfigLoader(temp_config_dir)
        with pytest.raises(ValueError, match="Protocol 'nonexistent' not found"):
            config.get_protocol_config('nonexistent')


class TestCreateReconstructionArgs:
    """Test cases for create_reconstruction_args function."""
    
    def test_create_reconstruction_args(self, temp_config_dir):
        """Test creating reconstruction arguments from protocol."""
        config = ConfigLoader(temp_config_dir)
        args = create_reconstruction_args(
            config, 'test_protocol', '/test/data', '/test/output'
        )
        
        assert args['data_path'] == '/test/data'
        assert args['output_path'] == '/test/output'
        assert args['num_subsets'] == 12
        assert args['num_epochs'] == 5
        assert args['resolution_model'] == (1.5, 0.025, False)
    
    def test_parameter_overrides(self, temp_config_dir):
        """Test parameter overrides in create_reconstruction_args."""
        config = ConfigLoader(temp_config_dir)
        args = create_reconstruction_args(
            config, 'test_protocol', '/test/data',
            num_epochs=10,  # Override
            custom_param='test'  # Additional parameter
        )
        
        assert args['num_epochs'] == 10  # Overridden
        assert args['custom_param'] == 'test'  # Additional


class TestUtils:
    """Test cases for utility functions."""
    
    def test_create_user_config_template(self):
        """Test creating user config template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = create_user_config_template(tmpdir)
            
            # Check that files were created
            assert (config_dir / 'scanners.yaml').exists()
            assert (config_dir / 'radionuclides.yaml').exists()
            assert (config_dir / 'protocols.yaml').exists()
    
    def test_validate_config_files_valid(self, temp_config_dir):
        """Test validation of valid config files."""
        results = validate_config_files(temp_config_dir)
        
        assert results['valid'] is True
        assert len(results['errors']) == 0
    
    def test_validate_config_files_missing(self):
        """Test validation with missing config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = validate_config_files(tmpdir)
            
            assert results['valid'] is False
            assert len(results['errors']) > 0
            assert any('Missing required file' in error for error in results['errors'])
    
    def test_validate_config_files_invalid_yaml(self):
        """Test validation with invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            
            # Create invalid YAML file
            with open(config_dir / 'scanners.yaml', 'w') as f:
                f.write('invalid: yaml: content: [')
            
            # Create empty but valid files
            with open(config_dir / 'radionuclides.yaml', 'w') as f:
                yaml.dump({'radionuclides': {}}, f)
            with open(config_dir / 'protocols.yaml', 'w') as f:
                yaml.dump({'protocols': {}}, f)
            
            results = validate_config_files(tmpdir)
            
            assert results['valid'] is False
            assert any('YAML parsing error' in error for error in results['errors'])


if __name__ == '__main__':
    pytest.main([__file__])
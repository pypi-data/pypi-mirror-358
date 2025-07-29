#!/usr/bin/env python3
"""
Example usage of the configuration system for SPECT/PET reconstruction.
"""

from sirf_config import ConfigLoader, get_y90_spect_params, get_y90_pet_params

def main():
    # Initialize configuration loader
    config = ConfigLoader('config')
    
    print("=== Available Configurations ===")
    print(f"Scanners: {', '.join(config.list_scanners())}")
    print(f"Radionuclides: {', '.join(config.list_radionuclides())}")
    print(f"Protocols: {', '.join(config.list_protocols())}")
    print()
    
    # Example 1: Using convenience functions for Y-90
    print("=== Example 1: Y-90 SPECT on GE Discovery 670 ===")
    try:
        params = get_y90_spect_params('ge_670', '/path/to/spect/data')
        for key, value in params.items():
            print(f"  {key}: {value}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 2: Using convenience functions for Y-90 PET
    print("=== Example 2: Y-90 PET on Mediso AnyScan Trio ===")
    try:
        params = get_y90_pet_params('mediso', '/path/to/pet/data')
        for key, value in params.items():
            print(f"  {key}: {value}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 3: Direct protocol usage
    print("=== Example 3: Direct Protocol Configuration ===")
    try:
        protocol_config = config.get_protocol_config('y90_mediso_spect')
        print(f"Protocol: {protocol_config['description']}")
        print(f"Scanner: {protocol_config['scanner_config']['name']}")
        print(f"Modality: {protocol_config['scanner_config']['modality']}")
        print("Reconstruction parameters:")
        for key, value in protocol_config['reconstruction_params'].items():
            print(f"  {key}: {value}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    
    # Example 4: Command line usage examples
    print("=== Command Line Usage Examples ===")
    print("SPECT reconstruction using scanner shorthand:")
    print("  python spect_reconstruct.py --scanner ge_670 --data_path /path/to/data")
    print()
    print("SPECT reconstruction using specific protocol:")
    print("  python spect_reconstruct.py --protocol y90_mediso_spect --data_path /path/to/data")
    print()
    print("PET reconstruction with overrides:")
    print("  python pet_reconstruct.py --scanner mediso --data_path /path/to/data --rdp --num_epochs 15")
    print()
    print("Manual parameters (backward compatibility):")
    print("  python spect_reconstruct.py --data_path /path/to/data \\")
    print("    --resolution_model '(1.22, 0.031, False)' \\")
    print("    --smoothing_kernel '(6.7, 6.7, 6.7)' \\")
    print("    --num_subsets 12 --num_epochs 5")


if __name__ == "__main__":
    main()
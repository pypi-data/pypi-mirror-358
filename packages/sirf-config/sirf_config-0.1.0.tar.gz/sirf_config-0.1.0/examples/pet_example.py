#!/usr/bin/env python3
"""
PET reconstruction example using SIRF Config.

This example demonstrates how to use sirf-config for PET reconstruction
with different scanners and configuration options.
"""

import argparse
import os
from sirf_config import get_y90_pet_params, ConfigLoader, create_reconstruction_args


def example_mediso_pet():
    """Example: Y-90 PET reconstruction on Mediso AnyScan Trio."""
    print("=== Mediso AnyScan Trio PET Example ===")
    
    try:
        # Method 1: Use convenience function with default data path
        print("\n1. Using default data path:")
        params = get_y90_pet_params('mediso')
        print(f"   Data path: {params['data_path']}")
        print(f"   PSF kernel: {params['psf_kernel']}")
        print(f"   Number of subsets: {params['num_subsets']}")
        print(f"   Number of epochs: {params['num_epochs']}")
        print(f"   GPU: {params['gpu']}")
        
        # Method 2: Use convenience function with custom data path
        print("\n2. Using custom data path:")
        custom_params = get_y90_pet_params('mediso', '/custom/pet/data')
        print(f"   Data path: {custom_params['data_path']}")
        print(f"   PSF kernel: {custom_params['psf_kernel']}")
        
    except Exception as e:
        print(f"   Error: {e}")


def example_ge_pet():
    """Example: Y-90 PET reconstruction on GE Discovery 690."""
    print("\n=== GE Discovery 690 PET Example ===")
    
    try:
        # Using protocol directly
        config = ConfigLoader()
        params = create_reconstruction_args(
            config, 'y90_ge_690_pet', 
            data_path=None,  # Use default
            output_path='/custom/output'
        )
        
        print(f"   Data path: {params['data_path']}")
        print(f"   Output path: {params['output_path']}")
        print(f"   PSF kernel: {params['psf_kernel']}")
        print(f"   Number of subsets: {params['num_subsets']}")
        print(f"   Number of epochs: {params['num_epochs']}")
        
    except Exception as e:
        print(f"   Error: {e}")


def example_custom_parameters():
    """Example: Custom parameter overrides."""
    print("\n=== Custom Parameter Overrides ===")
    
    try:
        # Override specific parameters
        config = ConfigLoader()
        params = create_reconstruction_args(
            config, 'y90_mediso_pet',
            data_path='/my/custom/data',
            output_path='/my/custom/output',
            num_epochs=15,  # Override default
            psf_kernel=(6.0, 6.0, 6.0),  # Override scanner PSF
            gpu=False,  # Force CPU
            custom_param='test'  # Add custom parameter
        )
        
        print("   Modified parameters:")
        for key, value in params.items():
            print(f"     {key}: {value}")
            
    except Exception as e:
        print(f"   Error: {e}")


def example_sirf_integration():
    """Example: Integration with SIRF PET reconstruction."""
    print("\n=== SIRF Integration Example ===")
    
    print("""
SIRF PET reconstruction integration:

```python
from sirf_config import get_y90_pet_params
from sirf.STIR import *

# Get configuration
params = get_y90_pet_params('mediso')

# Set up acquisition data
AcquisitionData.set_storage_scheme('memory')
acq_data = AcquisitionData(os.path.join(params['data_path'], 'prompts.hs'))
additive = AcquisitionData(os.path.join(params['data_path'], 'additive_term.hs'))
mult_factors = AcquisitionData(os.path.join(params['data_path'], 'mult_factors.hs'))
template = ImageData(os.path.join(params['data_path'], 'template_image.hv'))

# Set up acquisition model
if params['gpu']:
    acq_model = AcquisitionModelUsingParallelproj()
else:
    acq_model = AcquisitionModelUsingRayTracingMatrix()
    acq_model.set_num_tangential_LORs(10)

# Apply PSF
if 'psf_kernel' in params:
    gauss = SeparableGaussianImageFilter()
    gauss.set_fwhms(params['psf_kernel'])
    acq_model.set_image_data_processor(gauss)

# Set up sensitivity and additive term
asm = AcquisitionSensitivityModel(mult_factors)
acq_model.set_acquisition_sensitivity(asm)
acq_model.set_additive_term(additive)

# Create reconstructor
recon = OSMAPOSLReconstructor()
obj_fun = make_Poisson_loglikelihood(acq_data=acq_data, acq_model=acq_model)
recon.set_objective_function(obj_fun)
recon.set_num_subsets(params['num_subsets'])
recon.set_num_subiterations(params['num_subsets'] * params['num_epochs'])
recon.set_up(template)

# Run reconstruction
recon.reconstruct(template)
result = recon.get_output()

# Save result
output_file = os.path.join(params['output_path'], 'recon.hv')
result.write(output_file)
```
""")


def example_command_line_usage():
    """Example: Command line usage patterns."""
    print("\n=== Command Line Usage Examples ===")
    
    print("""
Command line examples for PET reconstruction:

1. Simple reconstruction with defaults:
   python pet_reconstruct.py --scanner mediso

2. Override data path:
   python pet_reconstruct.py --scanner mediso --data_path /custom/data

3. Use specific protocol:
   python pet_reconstruct.py --protocol y90_ge_690_pet

4. Override parameters:
   python pet_reconstruct.py --scanner mediso --num_epochs 15 --rdp

5. Multiple data suffixes:
   python pet_reconstruct.py --scanner ge_690 --suffix both

6. Custom PSF (override config):
   python pet_reconstruct.py --scanner mediso --psf_kernel "(6.0,6.0,6.0)"

7. Force CPU usage:
   python pet_reconstruct.py --scanner mediso --no_gpu
""")


def run_reconstruction_example():
    """Run a mock reconstruction to show the workflow."""
    print("\n=== Mock Reconstruction Workflow ===")
    
    try:
        # Get parameters for Mediso scanner
        params = get_y90_pet_params('mediso')
        
        print(f"1. Configuration loaded for Mediso AnyScan Trio")
        print(f"   Data path: {params['data_path']}")
        print(f"   PSF kernel: {params['psf_kernel']}")
        
        # Check if data path exists (in real usage)
        data_path = params['data_path']
        output_path = params.get('output_path', data_path)
        
        print(f"\n2. Checking paths:")
        print(f"   Data path exists: {os.path.exists(data_path)}")
        print(f"   Output path: {output_path}")
        
        # Mock the reconstruction steps
        print(f"\n3. Mock reconstruction steps:")
        print(f"   - Loading acquisition data from {data_path}")
        print(f"   - Setting up acquisition model with PSF {params['psf_kernel']}")
        print(f"   - Configuring OSEM: {params['num_subsets']} subsets, {params['num_epochs']} epochs")
        print(f"   - GPU acceleration: {params['gpu']}")
        print(f"   - Running reconstruction...")
        print(f"   - Saving result to {output_path}/recon.hv")
        print(f"   ✓ Reconstruction complete!")
        
    except Exception as e:
        print(f"   Error in workflow: {e}")


def main():
    """Run all PET examples."""
    print("SIRF Config - PET Reconstruction Examples")
    print("=" * 50)
    
    example_mediso_pet()
    example_ge_pet()
    example_custom_parameters()
    example_sirf_integration()
    example_command_line_usage()
    run_reconstruction_example()
    
    print("\n" + "=" * 50)
    print("For more information:")
    print("- Run: sirf-config list-configs")
    print("- Run: sirf-config show-config --protocol y90_mediso_pet")
    print("- See: examples/basic_usage.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PET reconstruction examples')
    parser.add_argument('--scanner', type=str, help='Scanner to demonstrate')
    args = parser.parse_args()
    
    if args.scanner:
        print(f"Demonstrating {args.scanner} configuration:")
        try:
            params = get_y90_pet_params(args.scanner)
            for key, value in params.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        main()
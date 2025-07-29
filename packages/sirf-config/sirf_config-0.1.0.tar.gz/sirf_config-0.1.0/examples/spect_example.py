#!/usr/bin/env python3
"""
SPECT reconstruction example using SIRF Config.

This example demonstrates how to use sirf-config for SPECT reconstruction
with different scanners and Y-90 bremsstrahlung imaging.
"""

import argparse
import os
from sirf_config import get_y90_spect_params, ConfigLoader, create_reconstruction_args


def example_mediso_spect():
    """Example: Y-90 SPECT reconstruction on Mediso AnyScan Trio."""
    print("=== Mediso AnyScan Trio SPECT Example ===")
    
    try:
        # Method 1: Use convenience function with default data path
        print("\n1. Using default data path:")
        params = get_y90_spect_params('mediso')
        print(f"   Data path: {params['data_path']}")
        print(f"   Resolution model: {params['resolution_model']}")
        print(f"   Smoothing kernel: {params.get('smoothing_kernel', 'None')}")
        print(f"   Number of subsets: {params['num_subsets']}")
        print(f"   Number of epochs: {params['num_epochs']}")
        
        # Method 2: Use convenience function with custom data path
        print("\n2. Using custom data path:")
        custom_params = get_y90_spect_params('mediso', '/custom/spect/data')
        print(f"   Data path: {custom_params['data_path']}")
        print(f"   Resolution model: {custom_params['resolution_model']}")
        
    except Exception as e:
        print(f"   Error: {e}")


def example_ge_spect():
    """Example: Y-90 SPECT reconstruction on GE Discovery 670."""
    print("\n=== GE Discovery 670 SPECT Example ===")
    
    try:
        # Using protocol directly
        config = ConfigLoader()
        params = create_reconstruction_args(
            config, 'y90_ge_670_spect',
            data_path=None,  # Use default
            output_path='/custom/output'
        )
        
        print(f"   Data path: {params['data_path']}")
        print(f"   Output path: {params['output_path']}")
        print(f"   Resolution model: {params['resolution_model']}")
        print(f"   Smoothing kernel: {params.get('smoothing_kernel', 'None')}")
        print(f"   Number of subsets: {params['num_subsets']}")
        print(f"   Number of epochs: {params['num_epochs']}")
        
    except Exception as e:
        print(f"   Error: {e}")


def example_resolution_models():
    """Example: Compare resolution models between scanners."""
    print("\n=== Resolution Model Comparison ===")
    
    scanners = ['mediso', 'ge_670']
    
    for scanner in scanners:
        try:
            params = get_y90_spect_params(scanner)
            sigma_0, alpha, full_3d = params['resolution_model']
            
            print(f"\n{scanner.upper()} Resolution Model:")
            print(f"   Sigma_0: {sigma_0} mm")
            print(f"   Alpha: {alpha}")
            print(f"   Full 3D: {full_3d}")
            print(f"   Smoothing: {params.get('smoothing_kernel', 'None')}")
            
        except Exception as e:
            print(f"   Error for {scanner}: {e}")


def example_custom_parameters():
    """Example: Custom parameter overrides for Y-90 bremsstrahlung."""
    print("\n=== Custom Y-90 Parameters ===")
    
    try:
        # Override parameters for better Y-90 bremsstrahlung reconstruction
        config = ConfigLoader()
        params = create_reconstruction_args(
            config, 'y90_mediso_spect',
            data_path='/my/custom/data',
            output_path='/my/custom/output',
            num_epochs=10,  # More epochs for bremsstrahlung
            resolution_model=(1.0, 0.025, False),  # Custom resolution
            smoothing_kernel=(8.0, 8.0, 8.0),  # More smoothing
            custom_param='y90_optimized'
        )
        
        print("   Y-90 optimized parameters:")
        for key, value in params.items():
            print(f"     {key}: {value}")
            
    except Exception as e:
        print(f"   Error: {e}")


def example_sirf_integration():
    """Example: Integration with SIRF SPECT reconstruction."""
    print("\n=== SIRF Integration Example ===")
    
    print("""
SIRF SPECT reconstruction integration:

```python
from sirf_config import get_y90_spect_params
from sirf.STIR import *

# Get configuration
params = get_y90_spect_params('mediso')

# Load SPECT data
acq_data = AcquisitionData(os.path.join(params['data_path'], 'peak.hs'))

# Try to load attenuation map
try:
    attn_map = ImageData(os.path.join(params['data_path'], 'umap_zoomed.hv'))
except:
    print("No attenuation map found")
    attn_map = None

# Create initial image
try:
    initial_image = ImageData(os.path.join(params['data_path'], 'initial_image.hv'))
    initial_image = initial_image.maximum(0)
except:
    # Create uniform image from acquisition data
    initial_image = acq_data.create_uniform_image(1)
    # Adjust dimensions for SPECT
    voxel_size = list(initial_image.voxel_sizes())
    voxel_size[0] *= 2
    dims = list(initial_image.dimensions())
    dims[0] = dims[0] // 2 + dims[0] % 2
    dims[1] -= dims[1] % 2
    dims[2] = dims[1]
    
    new_image = ImageData()
    new_image.initialise(tuple(dims), tuple(voxel_size), (0, 0, 0))
    initial_image = new_image

# Set up acquisition model
spect_matrix = SPECTUBMatrix()

# Set attenuation if available
if attn_map:
    spect_matrix.set_attenuation_image(attn_map)

# Set resolution model from config
sigma_0, alpha, full_3d = params['resolution_model']
spect_matrix.set_resolution_model(sigma_0, alpha, full_3d)
spect_matrix.set_keep_all_views_in_cache(True)

# Create acquisition model
acq_model = AcquisitionModelUsingMatrix(spect_matrix)

# Apply Y-90 bremsstrahlung smoothing if configured
if 'smoothing_kernel' in params:
    gauss = SeparableGaussianImageFilter()
    gauss.set_fwhms(params['smoothing_kernel'])
    acq_model.set_image_data_processor(gauss)

# Set up reconstructor
recon = OSMAPOSLReconstructor()
obj_fun = make_Poisson_loglikelihood(acq_data=acq_data, acq_model=acq_model)
recon.set_objective_function(obj_fun)
recon.set_num_subsets(params['num_subsets'])
recon.set_num_subiterations(params['num_subsets'] * params['num_epochs'])
recon.set_up(initial_image)

# Run reconstruction
recon.reconstruct(initial_image)
result = recon.get_current_estimate()

# Apply post-reconstruction smoothing if not already applied
if 'smoothing_kernel' in params:
    post_gauss = SeparableGaussianImageFilter()
    post_gauss.set_fwhms(params['smoothing_kernel'])
    post_gauss.apply(result)

# Save result
output_file = os.path.join(params['output_path'], 'recon.hv')
result.write(output_file)
```
""")


def example_y90_considerations():
    """Example: Special considerations for Y-90 bremsstrahlung imaging."""
    print("\n=== Y-90 Bremsstrahlung Considerations ===")
    
    print("""
Y-90 presents unique challenges for SPECT imaging:

1. **Continuous Energy Spectrum:**
   - Y-90 beta decay produces continuous bremsstrahlung
   - No discrete photopeak like Tc-99m (140 keV)
   - Requires different energy window strategies

2. **High Energy Photons:**
   - Bremsstrahlung up to 2.28 MeV
   - Requires high-energy collimators
   - Increased septal penetration and scatter

3. **Low Count Statistics:**
   - Much lower photon flux than diagnostic isotopes
   - Requires longer acquisition times
   - Benefits from higher smoothing/regularization

4. **Configuration Optimizations:**
""")
    
    try:
        # Show Y-90 specific configurations
        config = ConfigLoader()
        
        print("\n   Mediso Y-90 Configuration:")
        mediso_params = config.get_reconstruction_params('y90_mediso_spect')
        for key, value in mediso_params.items():
            print(f"     {key}: {value}")
        
        print("\n   GE Y-90 Configuration:")
        ge_params = config.get_reconstruction_params('y90_ge_670_spect')
        for key, value in ge_params.items():
            print(f"     {key}: {value}")
            
    except Exception as e:
        print(f"   Error: {e}")


def example_command_line_usage():
    """Example: Command line usage patterns."""
    print("\n=== Command Line Usage Examples ===")
    
    print("""
Command line examples for SPECT reconstruction:

1. Simple reconstruction with defaults:
   python spect_reconstruct.py --scanner mediso

2. Override data path:
   python spect_reconstruct.py --scanner mediso --data_path /custom/data

3. Use specific protocol:
   python spect_reconstruct.py --protocol y90_ge_670_spect

4. Override Y-90 parameters:
   python spect_reconstruct.py --scanner mediso \\
     --num_epochs 10 \\
     --smoothing_kernel "(8.0,8.0,8.0)"

5. Custom resolution model:
   python spect_reconstruct.py --scanner ge_670 \\
     --resolution_model "(1.5,0.025,False)"

6. Manual parameters (backward compatibility):
   python spect_reconstruct.py --data_path /path/to/data \\
     --resolution_model "(1.22,0.031,False)" \\
     --smoothing_kernel "(6.7,6.7,6.7)" \\
     --num_subsets 12 --num_epochs 5
""")


def run_reconstruction_example():
    """Run a mock reconstruction to show the workflow."""
    print("\n=== Mock Y-90 SPECT Reconstruction Workflow ===")
    
    try:
        # Get parameters for Mediso scanner
        params = get_y90_spect_params('mediso')
        
        print(f"1. Configuration loaded for Mediso AnyScan Trio SPECT")
        print(f"   Data path: {params['data_path']}")
        print(f"   Resolution model: {params['resolution_model']}")
        
        # Check if data path exists (in real usage)
        data_path = params['data_path']
        output_path = params.get('output_path', data_path)
        
        print(f"\n2. Checking paths:")
        print(f"   Data path exists: {os.path.exists(data_path)}")
        print(f"   Output path: {output_path}")
        
        # Mock the reconstruction steps
        print(f"\n3. Mock Y-90 reconstruction steps:")
        print(f"   - Loading acquisition data from {data_path}/peak.hs")
        print(f"   - Setting up SPECT matrix with resolution model {params['resolution_model']}")
        print(f"   - Configuring OSEM: {params['num_subsets']} subsets, {params['num_epochs']} epochs")
        
        if 'smoothing_kernel' in params:
            print(f"   - Applying Y-90 bremsstrahlung smoothing: {params['smoothing_kernel']}")
        
        print(f"   - Running iterative reconstruction...")
        print(f"   - Applying post-reconstruction processing...")
        print(f"   - Saving result to {output_path}/recon.hv")
        print(f"   ✓ Y-90 SPECT reconstruction complete!")
        
    except Exception as e:
        print(f"   Error in workflow: {e}")


def main():
    """Run all SPECT examples."""
    print("SIRF Config - SPECT Reconstruction Examples")
    print("=" * 50)
    
    example_mediso_spect()
    example_ge_spect()
    example_resolution_models()
    example_custom_parameters()
    example_sirf_integration()
    example_y90_considerations()
    example_command_line_usage()
    run_reconstruction_example()
    
    print("\n" + "=" * 50)
    print("For more information:")
    print("- Run: sirf-config list-configs")
    print("- Run: sirf-config show-config --protocol y90_mediso_spect")
    print("- See: examples/basic_usage.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SPECT reconstruction examples')
    parser.add_argument('--scanner', type=str, help='Scanner to demonstrate')
    args = parser.parse_args()
    
    if args.scanner:
        print(f"Demonstrating {args.scanner} SPECT configuration:")
        try:
            params = get_y90_spect_params(args.scanner)
            for key, value in params.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        main()
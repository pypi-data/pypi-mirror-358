#!/usr/bin/env python3
"""
Command-line interface for sirf-config package.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .utils import (
    create_user_config_template,
    validate_config_files,
    list_available_configs,
    get_example_usage,
)
from .config_loader import ConfigLoader


def cmd_create_template(args):
    """Create a configuration template."""
    try:
        config_dir = create_user_config_template(args.directory, force=args.force)
        print(f"✓ Configuration template created at: {config_dir}")
        print("\nNext steps:")
        print(f"1. Edit the configuration files in {config_dir}")
        print("2. Use ConfigLoader('/path/to/your/config') in your code")
        return 0
    except Exception as e:
        print(f"✗ Error creating template: {e}")
        return 1


def cmd_validate(args):
    """Validate configuration files."""
    try:
        results = validate_config_files(args.directory)
        
        print(f"Validation results for: {args.directory}")
        print(f"Status: {'✓ VALID' if results['valid'] else '✗ INVALID'}")
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  ✗ {error}")
        
        if results['warnings']:
            print("\nWarnings:")
            for warning in results['warnings']:
                print(f"  ⚠ {warning}")
        
        if results['valid']:
            print("\n✓ All configuration files are valid!")
        
        return 0 if results['valid'] else 1
        
    except Exception as e:
        print(f"✗ Error validating configurations: {e}")
        return 1


def cmd_list_configs(args):
    """List available configurations."""
    try:
        if args.directory:
            config = ConfigLoader(args.directory)
            scanners = config.list_scanners()
            radionuclides = config.list_radionuclides()
            protocols = config.list_protocols()
            print(f"Configurations in: {args.directory}")
        else:
            configs = list_available_configs()
            if 'error' in configs:
                print(f"✗ Error: {configs['error']}")
                return 1
            scanners = configs['scanners']
            radionuclides = configs['radionuclides']
            protocols = configs['protocols']
            print("Default configurations:")
        
        print(f"\nScanners ({len(scanners)}):")
        for scanner in scanners:
            print(f"  • {scanner}")
        
        print(f"\nRadionuclides ({len(radionuclides)}):")
        for radio in radionuclides:
            print(f"  • {radio}")
        
        print(f"\nProtocols ({len(protocols)}):")
        for protocol in protocols:
            print(f"  • {protocol}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error listing configurations: {e}")
        return 1


def cmd_show_config(args):
    """Show details of a specific configuration."""
    try:
        config = ConfigLoader(args.directory) if args.directory else ConfigLoader()
        
        if args.scanner:
            scanner_config = config.get_scanner_config(args.scanner)
            print(f"Scanner: {args.scanner}")
            print(f"Name: {scanner_config.get('name', 'N/A')}")
            print(f"Modality: {scanner_config.get('modality', 'N/A')}")
            print("PSF Configuration:")
            psf = scanner_config.get('psf', {})
            for key, value in psf.items():
                print(f"  {key}: {value}")
            
        elif args.protocol:
            protocol_config = config.get_protocol_config(args.protocol)
            print(f"Protocol: {args.protocol}")
            print(f"Description: {protocol_config.get('description', 'N/A')}")
            print(f"Scanner: {protocol_config.get('scanner', 'N/A')}")
            print(f"Radionuclide: {protocol_config.get('radionuclide', 'N/A')}")
            print("Reconstruction Parameters:")
            params = protocol_config.get('reconstruction_params', {})
            for key, value in params.items():
                print(f"  {key}: {value}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error showing configuration: {e}")
        return 1


def cmd_examples(args):
    """Show usage examples."""
    print("SIRF Config Usage Examples")
    print("=" * 50)
    print(get_example_usage())
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='sirf-config',
        description='SIRF Configuration Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sirf-config create-template ./my_configs
  sirf-config validate ./my_configs
  sirf-config list-configs
  sirf-config show-config --protocol y90_ge_670_spect
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create template command
    template_parser = subparsers.add_parser(
        'create-template',
        help='Create configuration template'
    )
    template_parser.add_argument(
        'directory',
        nargs='?',
        help='Target directory (default: ~/.config/sirf_config)'
    )
    template_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing files'
    )
    template_parser.set_defaults(func=cmd_create_template)
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate configuration files'
    )
    validate_parser.add_argument(
        'directory',
        help='Configuration directory to validate'
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    # List configs command
    list_parser = subparsers.add_parser(
        'list-configs',
        help='List available configurations'
    )
    list_parser.add_argument(
        '--directory',
        help='Custom configuration directory'
    )
    list_parser.set_defaults(func=cmd_list_configs)
    
    # Show config command
    show_parser = subparsers.add_parser(
        'show-config',
        help='Show configuration details'
    )
    show_group = show_parser.add_mutually_exclusive_group(required=True)
    show_group.add_argument('--scanner', help='Show scanner configuration')
    show_group.add_argument('--protocol', help='Show protocol configuration')
    show_parser.add_argument(
        '--directory',
        help='Custom configuration directory'
    )
    show_parser.set_defaults(func=cmd_show_config)
    
    # Examples command
    examples_parser = subparsers.add_parser(
        'examples',
        help='Show usage examples'
    )
    examples_parser.set_defaults(func=cmd_examples)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
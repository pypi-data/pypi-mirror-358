from .core import KMSServer, Activator, config, get_logger
from .core.utils import download_vlmcsd

import argparse,sys

# 获取logger
logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="HEU_KMS_Activator-like KMS activation tool")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Server commands
    server_parser = subparsers.add_parser('server', help='KMS server management')
    server_subparsers = server_parser.add_subparsers(dest='server_command', required=True)
    
    server_start = server_subparsers.add_parser('start', help='Start KMS server')
    server_start.add_argument('-b', '--background', action='store_true', help='Run in background')
    
    server_stop = server_subparsers.add_parser('stop', help='Stop KMS server')
    
    server_status = server_subparsers.add_parser('status', help='Check server status')
    
    server_test = server_subparsers.add_parser('test', help='Test server functionality')
    
    # Activation commands
    activate_parser = subparsers.add_parser('activate', help='Activation commands')
    activate_subparsers = activate_parser.add_subparsers(dest='activate_command', required=True)
    
    activate_windows = activate_subparsers.add_parser('windows', help='Activate Windows')
    
    activate_office = activate_subparsers.add_parser('office', help='Activate Office')
    activate_office.add_argument('-v', '--version', help='Specific Office version to activate')
    
    activate_all = activate_subparsers.add_parser('all', help='Activate Windows and Office')
    
    # Check status
    status_parser = subparsers.add_parser('status', help='Check activation status')
    
    # Configuration
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_command', required=True)
    
    config_set = config_subparsers.add_parser('set', help='Set configuration value')
    config_set.add_argument('key', help='Configuration key')
    config_set.add_argument('value', help='Configuration value')
    
    config_get = config_subparsers.add_parser('get', help='Get configuration value')
    config_get.add_argument('key', help='Configuration key')
    
    config_list = config_subparsers.add_parser('list', help='List all configurations')
    
    # Install vlmcsd
    install_parser = subparsers.add_parser('install', help='Install vlmcsd binary')
    
    args = parser.parse_args()
    
    # Execute commands
    if args.command == 'server':
        server = KMSServer()
        
        if args.server_command == 'start':
            if server.start(background=args.background):
                logger.info("KMS server started successfully")
            else:
                logger.error("Failed to start KMS server")
                sys.exit(1)
        
        elif args.server_command == 'stop':
            if server.stop():
                logger.info("KMS server stopped")
            else:
                logger.error("Failed to stop KMS server")
                sys.exit(1)
        
        elif args.server_command == 'status':
            status = server.status()
            logger.info(f"KMS server status: {status}")
        
        elif args.server_command == 'test':
            if server.test():
                logger.info("KMS server test successful")
            else:
                logger.error("KMS server test failed")
                sys.exit(1)
    
    elif args.command == 'activate':
        activator = Activator()
        
        if args.activate_command == 'windows':
            if activator.activate_windows():
                logger.info("Windows activated successfully")
            else:
                logger.error("Windows activation failed")
                sys.exit(1)
        
        elif args.activate_command == 'office':
            if activator.activate_office(version=args.version):
                logger.info("Office activated successfully")
            else:
                logger.error("Office activation failed")
                sys.exit(1)
        
        elif args.activate_command == 'all':
            win_success = activator.activate_windows()
            office_success = activator.activate_office()
            
            if win_success and office_success:
                logger.info("Windows and Office activated successfully")
            else:
                logger.error("Activation failed for some products")
                sys.exit(1)
    
    elif args.command == 'status':
        activator = Activator()
        status = activator.check_activation_status()
        
        print("\n=== Activation Status ===")
        print(f"Windows: {status['windows']}")
        
        if status['office']:
            print("\nOffice:")
            for version, state in status['office'].items():
                print(f"  {version}: {state}")
        else:
            print("\nNo Office installations found")
    
    elif args.command == 'config':
        if args.config_command == 'set':
            config.set(args.key, args.value)
            logger.info(f"Configuration updated: {args.key} = {args.value}")
        
        elif args.config_command == 'get':
            value = config.get(args.key)
            print(f"{args.key} = {value}")
        
        elif args.config_command == 'list':
            for key, value in config.config.items():
                print(f"{key} = {value}")
    
    elif args.command == 'install':
        if download_vlmcsd():
            logger.info("vlmcsd installed successfully")
        else:
            logger.error("Failed to install vlmcsd")
            sys.exit(1)

if __name__ == "__main__":
    main()
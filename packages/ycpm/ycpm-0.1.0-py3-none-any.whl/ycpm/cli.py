import argparse
import zipfile
import os
import json
import shutil
from colorama import Fore, Style, init
from ycpm import ycpm_version, clyp_version, install

init(autoreset=True)

def print_info():
    from ycpm import clyp_packages_folder
    print(f"{Fore.CYAN}:0 it's ycpm, your Clyp package manager! :3{Style.RESET_ALL}\n{Fore.YELLOW}ycpm version {ycpm_version}{Style.RESET_ALL}\n{Fore.YELLOW}Clyp version {clyp_version}{Style.RESET_ALL}\n{Fore.GREEN}Clyp packages folder: {clyp_packages_folder}{Style.RESET_ALL}")

def uninstall_package(package_name):
    from ycpm import clyp_packages_folder
    package_path = os.path.join(clyp_packages_folder, package_name)
    if not os.path.exists(package_path):
        print(f"{Fore.RED}Package '{package_name}' not found.{Style.RESET_ALL}")
        return
    print(f"{Fore.YELLOW}Uninstalling package '{package_name}'...{Style.RESET_ALL}")
    print(f"{Fore.RED}Are you sure you want to uninstall {package_name}? (y/n){Style.RESET_ALL}")
    confirmation = input().strip().lower()
    if confirmation == 'y':
        try:
            if os.path.isdir(package_path):
                shutil.rmtree(package_path)
            else:
                os.remove(package_path)
            print(f"{Fore.GREEN}Successfully uninstalled {package_name}.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error uninstalling package: {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Uninstallation canceled.{Style.RESET_ALL}")

def create_new_package(package_name):
    if os.path.exists(package_name):
        print(f"{Fore.RED}Directory '{package_name}' already exists.{Style.RESET_ALL}")
        return
    try:
        os.mkdir(package_name)
        with open(os.path.join(package_name, 'ycpm.json'), 'w') as f:
            f.write(json.dumps({
                "name": package_name,
                "file": f"{package_name}.cpak",
                "dependencies": [],
                "author": "Your Name",
            }, indent=4))
        print(f"{Fore.GREEN}Created new package '{package_name}'.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error creating package: {e}{Style.RESET_ALL}")

def build_package():
    if os.path.exists('ycpm.json'):
        with open('ycpm.json', 'r') as f:
            ycpm_data = json.load(f)
            package_name = ycpm_data.get("name")
            package_file = ycpm_data.get("file")
            if package_name and package_file:
                print(f"{Fore.YELLOW}Building package {package_name}...{Style.RESET_ALL}")
                try:
                    with zipfile.ZipFile(f"{package_file}", 'w') as zipf:
                        for root, dirs, files in os.walk(package_name):
                            for file in files:
                                if file != 'ycpm.json':
                                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), '.'))
                    print(f"{Fore.GREEN}Package {package_name} built successfully as {package_file}.{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error building package: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid ycpm.json: missing 'name' or 'file'.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No ycpm.json found.{Style.RESET_ALL}")

def list_packages():
    from ycpm import clyp_packages_folder
    print(f"{Fore.CYAN}Installed packages:{Style.RESET_ALL}")
    if not os.path.exists(clyp_packages_folder):
        print(f"{Fore.RED}No packages folder found.{Style.RESET_ALL}")
        return
    pkgs = os.listdir(clyp_packages_folder)
    if not pkgs:
        print(f"{Fore.YELLOW}No packages installed.{Style.RESET_ALL}")
    else:
        for pkg in pkgs:
            print(f"{Fore.GREEN}- {pkg}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="ycpm - your Clyp package manager!", epilog="Example: ycpm install mypkg")
    parser.add_argument('--version', action='store_true', help='Show ycpm version and exit')
    subparsers = parser.add_subparsers(dest='command', required=False)

    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('source', nargs='?', help='Source (optional)')
    install_parser.add_argument('package', nargs='?', help='Package (optional)')

    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package to uninstall')

    new_parser = subparsers.add_parser('new', help='Create a new package')
    new_parser.add_argument('name', help='Name of the new package')

    build_parser = subparsers.add_parser('build', help='Build the current package')

    list_parser = subparsers.add_parser('list', help='List installed packages')

    info_parser = subparsers.add_parser('info', help='Show ycpm and Clyp info')

    version_parser = subparsers.add_parser('version', help='Show ycpm version')

    args = parser.parse_args()

    if args.version:
        print(f"ycpm version {ycpm_version}")
        return

    if not args.command:
        parser.print_help()
        return

    if args.command == 'install':
        install.install(source=args.source, package=args.package)
    elif args.command == 'uninstall':
        uninstall_package(args.package)
    elif args.command == 'new':
        create_new_package(args.name)
    elif args.command == 'build':
        build_package()
    elif args.command == 'list':
        list_packages()
    elif args.command == 'info':
        print_info()
    elif args.command == 'version':
        print(f"ycpm version {ycpm_version}")

if __name__ == "__main__":
    main()
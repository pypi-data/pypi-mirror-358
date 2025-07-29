import argparse
import subprocess
import sys


def get_package_list(skip_self=True):
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'list', '--not-required', '--format=freeze', '--exclude', 'pip'
        ], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        if skip_self:
            filtered = [line for line in lines if not (line.lower().startswith('pippack==') or line.lower().startswith('setuptools=='))]
            return '\n'.join(filtered)
        return '\n'.join(lines)
    except Exception as e:
        return f"Error: {str(e)}"

def get_all_packages():
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'list', '--format=freeze'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"

def get_outdated_packages():
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'list', '--outdated'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"

def export_requirements(filename='requirements.txt'):
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'list', '--not-required', '--format=freeze', '--exclude', 'pip'
        ], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        filtered = [line for line in lines if not (line.lower().startswith('pippack==') or line.lower().startswith('setuptools=='))]
        with open(filename, 'w') as f:
            f.write('\n'.join(filtered))
        return f"Exported filtered packages to {filename}"
    except Exception as e:
        return f"Error: {str(e)}"

def export_all_requirements(filename='requirements.txt'):
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
        with open(filename, 'w') as f:
            f.write(result.stdout)
        return f"Exported all packages to {filename}"
    except Exception as e:
        return f"Error: {str(e)}"

def show_package_info(package):
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'show', package], capture_output=True, text=True)
        return result.stdout or f"Package '{package}' not found."
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(
        description="pippack: pip package helper",
        epilog="""
Examples:
  pippack                Show top-level installed packages (excluding dependencies, pip, pippack, setuptools)
  pippack all            Show all installed packages (including dependencies)
  pippack outdated       Show outdated packages
  pippack export         Export top-level packages (excluding dependencies, pip, pippack, setuptools) to requirements.txt
  pippack export-all     Export all installed packages to requirements.txt
  pippack show <pkg>     Show details for a specific package
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    subparsers.add_parser('all', help='Show all installed packages (including dependencies)')
    subparsers.add_parser('outdated', help='Show outdated packages (those with newer versions available)')
    subparsers.add_parser('export', help='Export top-level packages (excluding dependencies, pip, pippack, setuptools) to requirements.txt')
    subparsers.add_parser('export-all', help='Export all installed packages to requirements.txt')
    show_parser = subparsers.add_parser('show', help='Show details for a specific package (version, location, dependencies, etc.)')
    show_parser.add_argument('package', help='Package name to show info for')

    args = parser.parse_args()

    if args.command == 'all':
        print(get_all_packages())
    elif args.command == 'outdated':
        print(get_outdated_packages())
    elif args.command == 'export':
        print(export_requirements())
    elif args.command == 'export-all':
        print(export_all_requirements())
    elif args.command == 'show':
        print(show_package_info(args.package))
    else:
        print(get_package_list())

if __name__ == "__main__":
    main()

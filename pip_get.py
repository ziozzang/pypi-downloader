#!python3
import os
import sys
import requests
import re
from urllib.parse import urlparse
from argparse import ArgumentParser
from packaging.version import Version, InvalidVersion

# Parse the package specification to extract the package name and version condition.
def parse_package_spec(input_str: str):
    """
    Example:
      - "flask>2"      -> ("flask", ">2")
      - "flask>=2.0.0" -> ("flask", ">=2.0.0")
      - "flask==1.2.3" -> ("flask", "==1.2.3")
      - "flask"        -> ("flask", None)
    """
    match = re.match(r'^([A-Za-z0-9_\-]+)([><=]+)([0-9A-Za-z\.\-]+)$', input_str)
    if match:
        pkg, op, ver = match.groups()
        return pkg, op + ver  # e.g., ("flask", ">2.0.0")
    else:
        return input_str, None  # No version condition

# Normalize the version string for conditions like '>=2' to '>=2.0.0'
def normalize_version(version):
    """
    Normalize a version condition like '2' to '2.0.0'.
    """
    version_parts = version.split(".")
    while len(version_parts) < 3:
        version_parts.append("0")  # Ensure at least 3 parts
    return ".".join(version_parts)

# Retrieve all available URLs for a package and filter them based on version condition and file extensions
def get_package_urls(package_name, version_condition=None, filters=None, latest=False):
    url = f"https://pypi.org/simple/{package_name}/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Failed to fetch {url}")
        sys.exit(1)

    # Use regex to extract the download URLs
    urls = re.findall(r'href="(https://files.pythonhosted.org/[^"]+)"', response.text)

    # Filter by version condition if specified
    if version_condition:
        filtered_urls = []
        try:
            # Extract version condition operator and version
            condition_op, condition_version_str = re.search(r'([><=]+)([0-9\w\.]+)', version_condition).groups()
            condition_version_str = normalize_version(condition_version_str)
            condition_version = Version(condition_version_str)
        except InvalidVersion:
            print(f"Error: Invalid version format in condition {version_condition}")
            sys.exit(1)

        for link in urls:
            link = link.rsplit("#", 1)[0]  # Remove fragments after '#'
            if any(link.lower().endswith(ext) for ext in ['.tar.gz', '.tgz', '.whl', '.zip']):
                # Extract version from the URL
                version_str = None
                match = re.search(r'-([0-9][^-]+)-', link)
                if match:
                    version_str = match.group(1)
                else:
                    match = re.search(r'-([0-9a-zA-Z\w\.]+)\.[tar|tgz|whl|zip]', link)
                    if match:
                        version_str = match.group(1).rsplit('.', 1)[0]
                if version_str:
                    try:
                        link_version = Version(version_str)
                        # Compare versions according to the condition
                        if condition_op == '>' and link_version > condition_version:
                            filtered_urls.append(link)
                        elif condition_op == '>=' and link_version >= condition_version:
                            filtered_urls.append(link)
                        elif condition_op == '<' and link_version < condition_version:
                            filtered_urls.append(link)
                        elif condition_op == '<=' and link_version <= condition_version:
                            filtered_urls.append(link)
                        elif condition_op == '==' and link_version == condition_version:
                            filtered_urls.append(link)
                    except InvalidVersion:
                        print(f"Error: Invalid version in package '{version_str}' for {link}")
                        continue

        urls = filtered_urls
    else:
        filtered_urls = []
        for url in urls:
            filtered_urls.append(url.rsplit("#",1)[0])
        urls = filtered_urls


    # Further filter URLs based on file name extensions if specified
    if filters:
        filtered_urls = []
        for url in urls:
            file_name = os.path.basename(urlparse(url).path)
            if any(f in file_name for f in filters):
                filtered_urls.append(url)
        urls = filtered_urls

    # If the user requested the latest version, find the one with the highest version
    if latest and urls:
        latest_url = None
        latest_version = None
        for url in urls:
            file_name = os.path.basename(urlparse(url).path)

            version_str = None
            match = re.search(r'-([0-9][^-]+)-', file_name)
            if match:
                version_str = match.group(1)
            else:
                match = re.search(r'-([0-9a-zA-Z\w\.]+)\.[tar|tgz|whl|zip]', file_name)
                version_str = match.group(1).rsplit('.', 1)[0]
            try:
                package_version = Version(version_str)
                if not latest_version or package_version > latest_version:
                        latest_version = package_version
                        latest_url = url
            except InvalidVersion:
                continue
        urls = [latest_url] if latest_url else []

    return urls

# Download a file from a URL and save it to a destination folder
def download_file(url, dest_folder):
    file_name = os.path.basename(urlparse(url).path)
    file_path = os.path.join(dest_folder, file_name)

    if os.path.exists(file_path):
        print(f"File {file_name} already exists. Skipping...")
        return

    print(f"Downloading {file_name}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {file_name} to {dest_folder}")
    else:
        print(f"Error: Failed to download {url}")

# Display file names and versions for the given URLs
def show_package_info(urls):
    for url in urls:
        file_name = os.path.basename(urlparse(url).path)
        print(f"File: {file_name}")

# Main function to parse arguments and manage the download process
def main():
    parser = ArgumentParser(description="Download Python package versions from PyPI")

    # Accept package specification and optional version condition as arguments
    parser.add_argument("package_spec", help="Package name or 'package+operator+version' (e.g., 'flask', 'flask>2', 'flask==2.0.0')")
    parser.add_argument("version_condition", nargs="?", default=None, help="Version condition (e.g., '==1.0.0' or '>=1.0')")
    parser.add_argument("--dest", default=os.getcwd(), help="Directory to save the downloaded packages")
    parser.add_argument("-s", "--show-only", action="store_true", help="Show package file names and versions only, without downloading")
    parser.add_argument("--filter", default=None, help="Comma separated list of strings to filter file names (e.g., 'arm,x86')")
    parser.add_argument("--ext", default="whl,zip,tgz,gz", help="Only download specific file extensions (default: whl, zip, tgz, gz)")
    parser.add_argument("-l", "--latest", action="store_true", help="Download the latest version of the package")

    args = parser.parse_args()

    # Parse the package specification (package name and version condition)
    pkg_name, parsed_condition = parse_package_spec(args.package_spec)

    # Use the specified version condition or the parsed one
    version_condition = args.version_condition if args.version_condition else parsed_condition

    # Process filters (comma-separated list)
    filters = args.filter.split(',') if args.filter else None

    # Fetch the package URLs based on the version condition, filters, and latest flag
    urls = get_package_urls(pkg_name, version_condition, filters, latest=args.latest)

    # Filter by file extensions
    exts = args.ext.split(',')
    urls = [url for url in urls if any(url.lower().endswith(ext) for ext in exts)]

    if args.show_only:
        # Show package information without downloading
        show_package_info(urls)
    else:
        # Download the packages
        for url in urls:
            download_file(url, args.dest)

# Run the main function when the script is executed
if __name__ == "__main__":
    main()

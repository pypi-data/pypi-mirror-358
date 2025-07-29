# windockd/installer.py
import os
import shutil
from pathlib import Path
from zipfile import ZipFile
from importlib.resources import files
import windockd.resources
import click

def extract_zip(zip_path, extract_to):
    """Extract ZIP file with progress indication"""
    click.echo(f"📦 Extracting {Path(zip_path).name} to {extract_to}")
    try:
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        click.echo(f"❌ Failed to extract {zip_path}: {e}", err=True)
        return False

def check_existing_installation(bin_dir):
    """Check if windockd is already installed"""
    containerd_exe = bin_dir / "containerd.exe"
    nerdctl_exe = bin_dir / "nerdctl.exe"
    return containerd_exe.exists() and nerdctl_exe.exists()

def install_dependencies(force=False):
    """Install containerd and nerdctl with improved error handling"""
    BIN_DIR = Path(os.getenv("SystemRoot")) / "System32" / "windockd"
    
    # Check existing installation
    if not force and check_existing_installation(BIN_DIR):
        click.echo("✅ windockd is already installed. Use --force to reinstall.")
        return True
    
    click.echo(f"📁 Installing dependencies to {BIN_DIR}")

    try:
        # Create directory
        BIN_DIR.mkdir(parents=True, exist_ok=True)
        
        # Get resource paths
        containerd_zip = str(files(windockd.resources).joinpath("containerd.zip"))
        nerdctl_zip = str(files(windockd.resources).joinpath("nerdctl.zip"))
        
        # Check if resource files exist
        if not Path(containerd_zip).exists():
            click.echo("❌ containerd.zip not found in resources", err=True)
            return False
        
        if not Path(nerdctl_zip).exists():
            click.echo("❌ nerdctl.zip not found in resources", err=True)
            return False

        # Install components
        click.echo("🔧 Installing containerd...")
        if not extract_zip(containerd_zip, BIN_DIR):
            return False

        click.echo("🔧 Installing nerdctl...")
        if not extract_zip(nerdctl_zip, BIN_DIR):
            return False

        # Create docker.bat shim with better content
        docker_shim = BIN_DIR / "docker.bat"
        shim_content = '''@echo off
REM Docker compatibility shim for nerdctl
setlocal EnableDelayedExpansion

set NERDCTL_PATH=%~dp0nerdctl.exe
if not exist "%NERDCTL_PATH%" (
    echo Error: nerdctl.exe not found
    exit /b 1
)

"%NERDCTL_PATH%" %*
'''
        
        with open(docker_shim, "w") as f:
            f.write(shim_content)

        click.echo("✅ Installation completed successfully!")
        click.echo(f"💡 Add {BIN_DIR} to your PATH for Docker compatibility")
        click.echo("💡 Run 'windockd start' to start the containerd service")
        
        return True
        
    except Exception as e:
        click.echo(f"❌ Installation failed: {e}", err=True)
        return False


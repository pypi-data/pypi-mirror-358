# windockd/utils.py
import os
import subprocess
import platform
import click
from pathlib import Path

def check_prerequisites():
    """Check system prerequisites"""
    click.echo("🔍 Checking prerequisites...")
    
    # Check Windows version
    version = platform.version()
    click.echo(f"💻 Windows Version: {version}")
    
    # Check if Windows containers feature is available
    try:
        result = subprocess.run(
            'dism /online /get-featureinfo /featurename:Containers',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if "State : Enabled" in result.stdout:
            click.echo("✅ Windows Containers feature: Enabled")
        else:
            click.echo("⚠️  Windows Containers feature: Not enabled")
            click.echo("💡 Run: dism /online /enable-feature /featurename:containers /all")
            
    except Exception as e:
        click.echo(f"⚠️  Could not check Windows Containers feature: {e}")
    
    return True

def activate_docker_env():
    """Activate Docker-compatible environment"""
    click.echo("🐳 Activating Docker environment...")
    
    # Set environment variable
    os.environ["DOCKER_HOST"] = "npipe:////./pipe/containerd-containerd"
    
    # Check if PATH contains windockd
    bin_dir = Path(os.getenv("SystemRoot")) / "System32" / "windockd"
    path_env = os.environ.get("PATH", "")
    
    if str(bin_dir) not in path_env:
        click.echo(f"⚠️  {bin_dir} is not in PATH")
        click.echo("💡 Add it to PATH for Docker compatibility")
    else:
        click.echo("✅ windockd is in PATH")
    
    click.echo("🎉 Docker environment activated!")
    click.echo("💡 You can now use 'docker' commands (powered by nerdctl)")

def run_docker_command(args):
    """Run docker command through nerdctl"""
    bin_dir = Path(os.getenv("SystemRoot")) / "System32" / "windockd"
    nerdctl_path = bin_dir / "nerdctl.exe"
    
    if not nerdctl_path.exists():
        click.echo("❌ nerdctl.exe not found. Run 'windockd install' first.", err=True)
        return
    
    try:
        # Run nerdctl with the provided arguments
        cmd = [str(nerdctl_path)] + args
        subprocess.run(cmd, check=False)
    except Exception as e:
        click.echo(f"❌ Error running command: {e}", err=True)
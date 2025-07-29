# windockd/service.py
import os
import subprocess
import click
import ctypes
from pathlib import Path

def is_admin():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_containerd_path():
    """Get the path to containerd.exe"""
    bin_dir = Path(os.getenv("SystemRoot")) / "System32" / "windockd"
    return bin_dir / "containerd.exe"

def is_service_installed():
    """Check if containerd service is installed"""
    try:
        result = subprocess.run(
            "sc query containerd", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0
    except:
        return False

def start_containerd():
    """Start containerd service with improved error handling"""
    containerd_path = get_containerd_path()
    
    if not containerd_path.exists():
        click.echo("❌ containerd.exe not found. Run 'windockd install' first.", err=True)
        return False

    click.echo("🚀 Starting containerd service...")
    
    try:
        # Register service if not already registered
        if not is_service_installed():
            click.echo("📝 Registering containerd service...")
            result = subprocess.run(
                f'"{containerd_path}" --register-service',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                click.echo(f"❌ Failed to register service: {result.stderr}", err=True)
                return False
        
        # Start the service
        result = subprocess.run(
            "net start containerd",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✅ containerd service started successfully!")
            return True
        else:
            if "already been started" in result.stderr:
                click.echo("ℹ️  containerd service is already running")
                return True
            else:
                click.echo(f"❌ Failed to start service: {result.stderr}", err=True)
                return False
                
    except Exception as e:
        click.echo(f"❌ Error starting containerd: {e}", err=True)
        return False

def stop_containerd():
    """Stop containerd service"""
    click.echo("🛑 Stopping containerd service...")
    
    try:
        result = subprocess.run(
            "net stop containerd",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            click.echo("✅ containerd service stopped successfully!")
        elif "is not started" in result.stderr:
            click.echo("ℹ️  containerd service is not running")
        else:
            click.echo(f"❌ Failed to stop service: {result.stderr}", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error stopping containerd: {e}", err=True)

def check_status():
    """Check containerd service status with detailed info"""
    click.echo("🔍 Checking containerd status...")
    
    # Check if binaries exist
    containerd_path = get_containerd_path()
    nerdctl_path = containerd_path.parent / "nerdctl.exe"
    
    click.echo(f"📁 Installation path: {containerd_path.parent}")
    click.echo(f"🔧 containerd.exe: {'✅ Found' if containerd_path.exists() else '❌ Missing'}")
    click.echo(f"🔧 nerdctl.exe: {'✅ Found' if nerdctl_path.exists() else '❌ Missing'}")
    
    # Check service status
    if is_service_installed():
        try:
            result = subprocess.run(
                "sc query containerd",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if "RUNNING" in result.stdout:
                click.echo("🟢 Service Status: RUNNING")
            elif "STOPPED" in result.stdout:
                click.echo("🔴 Service Status: STOPPED")
            else:
                click.echo("🟡 Service Status: UNKNOWN")
                
        except Exception as e:
            click.echo(f"❌ Error checking service: {e}", err=True)
    else:
        click.echo("🔴 Service Status: NOT INSTALLED")


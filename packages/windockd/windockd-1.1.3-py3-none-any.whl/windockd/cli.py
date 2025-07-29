# Enhanced windockd implementation with improvements

# windockd/cli.py
import click
import sys
from windockd.installer import install_dependencies
from windockd.service import start_containerd, stop_containerd, check_status, is_admin
from windockd.utils import activate_docker_env, check_prerequisites

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """windockd: Lightweight Windows Container Runtime CLI
    
    A simple tool to manage containerd on Windows with Docker compatibility.
    """
    pass

@cli.command()
@click.option('--force', is_flag=True, help='Force reinstallation even if already installed')
def install(force):
    """Install required dependencies (containerd, nerdctl)"""
    if not is_admin():
        click.echo("❌ Administrator privileges required for installation", err=True)
        sys.exit(1)
    
    if not check_prerequisites():
        click.echo("❌ Prerequisites check failed", err=True)
        sys.exit(1)
    
    install_dependencies(force=force)

@cli.command()
def start():
    """Start containerd service"""
    if not is_admin():
        click.echo("❌ Administrator privileges required to start service", err=True)
        sys.exit(1)
    
    start_containerd()

@cli.command()
def stop():
    """Stop containerd service"""
    if not is_admin():
        click.echo("❌ Administrator privileges required to stop service", err=True)
        sys.exit(1)
    
    stop_containerd()

@cli.command()
def restart():
    """Restart containerd service"""
    if not is_admin():
        click.echo("❌ Administrator privileges required to restart service", err=True)
        sys.exit(1)
    
    click.echo("🔄 Restarting containerd service...")
    stop_containerd()
    start_containerd()

@cli.command()
def status():
    """Check runtime status"""
    check_status()

@cli.command()
def activate():
    """Activate Docker-compatible environment"""
    activate_docker_env()

@cli.command()
@click.argument('docker_args', nargs=-1)
def docker(docker_args):
    """Run docker commands through nerdctl"""
    from windockd.utils import run_docker_command
    run_docker_command(list(docker_args))

if __name__ == '__main__':
    cli()


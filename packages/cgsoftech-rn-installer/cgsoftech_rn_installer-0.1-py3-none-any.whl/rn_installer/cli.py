import click
import platform
import subprocess
import os
import requests
from rich.console import Console
from rich.progress import track
from plumbum import local
from tqdm import tqdm
from zipfile import ZipFile

# Branding Constants
BRAND_NAME = "CG Softech React Native Installer"
BRAND_TAGLINE = "Official tool by CG Softech Bhilai"
ANDROID_HOME = os.path.expanduser("~/.rn-android")
console = Console()

def print_brand():
    """Display branded header."""
    console.print(f"\n[bold cyan]===== {BRAND_NAME} =====[/]")
    console.print(f"[dim]{BRAND_TAGLINE}[/]\n")

@click.group()
def cli():
    """Automate React Native setup without Android Studio/Expo."""
    print_brand()

@cli.command()
def android():
    """Install Android SDK + Java (no Android Studio)."""
    print_brand()
    console.print("[bold green]🚀 Setting up Android for React Native...[/]")
    check_java()
    install_android_sdk()
    accept_android_licenses()

def check_java():
    try:
        java_version = local["java"]["-version"]()
        console.print(f"[green]✔ Java is installed: {java_version}[/]")
    except:
        console.print("[red]✖ Java not found! Installing JDK...[/]")
        system = platform.system().lower()
        
        # Platform-specific installs
        if system == "darwin":
            success = subprocess.run(["brew", "install", "--cask", "temurin11"]).returncode == 0
        elif system == "windows":
            success = subprocess.run(["choco", "install", "-y", "temurin11"]).returncode == 0
        else:  # Linux
            success = subprocess.run(["sudo", "apt", "install", "-y", "openjdk-11-jdk"]).returncode == 0
        
        if success:
            console.print("[green]✔ Installed JDK successfully![/]")
        else:
            console.print("[red]✖ Failed to install Java. Manual install required.[/]")
            raise click.Abort()

def get_android_sdk_url():
    system = platform.system().lower()
    if system == "darwin":
        return "https://dl.google.com/android/repository/commandlinetools-mac-9477386_latest.zip"
    elif system == "windows":
        return "https://dl.google.com/android/repository/commandlinetools-win-9477386_latest.zip"
    else:  # Linux
        return "https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip"

def install_android_sdk():
    ANDROID_SDK_URL = get_android_sdk_url()
    os.makedirs(ANDROID_HOME, exist_ok=True)
    tools_dir = os.path.join(ANDROID_HOME, "cmdline-tools")
    
    if os.path.exists(tools_dir):
        console.print("[yellow]✔ Android SDK already installed.[/]")
        return

    console.print(f"[blue]↓ Downloading Android SDK... [dim]({ANDROID_SDK_URL})[/]")
    sdk_zip = os.path.join(ANDROID_HOME, "sdk-tools.zip")
    
    # Download with progress bar
    response = requests.get(ANDROID_SDK_URL, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    
    with open(sdk_zip, "wb") as f, tqdm(
        desc="[CG Softech] Downloading SDK",
        total=total_size,
        unit="B",
        unit_scale=True,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
            bar.update(len(chunk))

    # Unzip
    with ZipFile(sdk_zip, "r") as zip_ref:
        zip_ref.extractall(ANDROID_HOME)
    
    os.remove(sdk_zip)
    console.print(f"[green]✔ Android SDK installed at: [bold]{ANDROID_HOME}[/][/]")

    # Update environment variables
    shell_profile = "~/.bashrc" if platform.system() != "Windows" else "~/.bash_profile"
    with open(os.path.expanduser(shell_profile), "a") as f:
        f.write(f"\n# Added by {BRAND_NAME}\n")
        f.write(f"export ANDROID_HOME={ANDROID_HOME}\n")
        f.write('export PATH="$PATH:$ANDROID_HOME/cmdline-tools/bin"\n')
    
    console.print("[bold yellow]⚠ Restart your terminal or run `source {shell_profile}`.[/]")

def accept_android_licenses():
    sdkmanager = os.path.join(ANDROID_HOME, "cmdline-tools", "bin", "sdkmanager")
    if not os.path.exists(sdkmanager):
        console.print("[red]✖ sdkmanager not found![/]")
        return
    
    console.print("[dim]Accepting Android licenses...[/]")
    subprocess.run(
        [sdkmanager, "--licenses"],
        input="y\n".encode() * 10,  # Auto-accept all
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    console.print("[green]✔ All Android licenses accepted.[/]")

if __name__ == "__main__":
    cli()
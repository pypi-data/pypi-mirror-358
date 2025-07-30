# rn_installer.py
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

ANDROID_SDK_URL = "https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip"  # Replace with your OS's URL
ANDROID_HOME = os.path.expanduser("~/.rn-android")

console = Console()

@click.group()
def cli():
    """Automate React Native setup without Android Studio/Expo."""
    pass

@cli.command()
def android():
    """Install Android SDK + Java (no Android Studio)."""
    console.print("[bold green]🚀 Setting up Android for React Native...[/]")
    check_java()
    install_android_sdk()
    accept_android_licenses()

def check_java():
    try:
        java_version = local["java"]["-version"]()
        console.print(f"[green]✔ Java is installed: {java_version}[/]")
    except:
        console.print("[red]✖ Java not found! Installing Temurin JDK 11...[/]")
        # For macOS/Linux (use `choco` for Windows)
        if subprocess.run(["brew", "install", "--cask", "temurin11"]).returncode == 0:
            console.print("[green]✔ Installed Temurin JDK 11![/]")
        else:
            console.print("[red]Failed to install Java. Manual install required.[/]")
            raise click.Abort()
    pass
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
        console.print("[yellow]✔ Android SDK already exists.[/]")
        return

    console.print("[blue]↓ Downloading Android SDK...[/]")
    sdk_zip = os.path.join(ANDROID_HOME, "sdk-tools.zip")
    
    # Download with progress bar
    response = requests.get(ANDROID_SDK_URL, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    with open(sdk_zip, "wb") as f, tqdm(
        desc=sdk_zip,
        total=total_size,
        unit="B",
        unit_scale=True,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
            bar.update(len(chunk))

    # Unzip
    with ZipFile(sdk_zip, "r") as zip_ref:
        zip_ref.extractall(ANDROID_HOME)
    
    os.remove(sdk_zip)
    console.print(f"[green]✔ Android SDK installed at: {ANDROID_HOME}[/]")

    # Update environment variables
    with open(os.path.expanduser("~/.bashrc"), "a") as f:
        f.write(f"\nexport ANDROID_HOME={ANDROID_HOME}\n")
        f.write('export PATH="$PATH:$ANDROID_HOME/cmdline-tools/bin"\n')
    
    console.print("[bold]⚠ Restart your terminal or run `source ~/.bashrc`.[/]")
    pass
def accept_android_licenses():
    sdkmanager = os.path.join(ANDROID_HOME, "cmdline-tools", "bin", "sdkmanager")
    if not os.path.exists(sdkmanager):
        console.print("[red]✖ sdkmanager not found![/]")
        return
    
    # Auto-accept all licenses
    licenses = [
        "android-sdk-license",
        "android-sdk-preview-license",
        "intel-android-extra-license"
    ]
    
    for license in licenses:
        subprocess.run(
            [sdkmanager, "--licenses"],
            input=f"y\n".encode(),  # Auto-accept
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    console.print("[green]✔ Accepted all Android licenses.[/]")
    pass
if __name__ == "__main__":
    cli()
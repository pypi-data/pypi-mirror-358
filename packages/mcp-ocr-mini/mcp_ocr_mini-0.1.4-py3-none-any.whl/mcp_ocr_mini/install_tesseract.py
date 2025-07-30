"""Handle Tesseract installation during package setup."""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

def get_package_manager() -> Optional[str]:
    """Detect the system's package manager."""
    system = platform.system().lower()
    
    if system == "darwin":
        # Check if Homebrew is installed (both Intel and Apple Silicon paths)
        homebrew_paths = ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"]
        for brew_path in homebrew_paths:
            if Path(brew_path).exists():
                return "brew"
        # Fallback: check if brew is in PATH
        if subprocess.run(["which", "brew"], check=True, stdout=sys.stderr, stderr=sys.stderr).returncode == 0:
            return "brew"
    elif system == "linux":
        # Check for apt (Debian/Ubuntu)
        if os.path.exists("/usr/bin/apt"):
            return "apt"
        # Check for dnf (Fedora)
        elif os.path.exists("/usr/bin/dnf"):
            return "dnf"
        # Check for pacman (Arch)
        elif os.path.exists("/usr/bin/pacman"):
            return "pacman"
    elif system == "windows":
        # Check if winget is available
        if subprocess.run(["winget", "--version"], check=True, shell=True, stdout=sys.stderr, stderr=sys.stderr).returncode == 0:
            return "winget"
    
    return None

def find_tesseract_executable() -> Optional[str]:
    """Find Tesseract executable path without requiring PATH."""
    system = platform.system().lower()
    
    # Platform-specific search paths
    if system == "windows":
        paths = [
            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
        ]
    elif system == "darwin":
        # Both Intel and Apple Silicon Mac paths
        paths = [
            "/opt/homebrew/bin/tesseract",  # Apple Silicon
            "/usr/local/bin/tesseract",     # Intel Mac
            "/usr/bin/tesseract"            # System installation
        ]
    elif system == "linux":
        paths = [
            "/usr/bin/tesseract", 
            "/usr/local/bin/tesseract"
        ]
    else:
        return None
    
    # Check each path
    for path in paths:
        if Path(path).exists():
            return path
    
    return None

def install_homebrew_if_needed():
    """Install Homebrew if it's not available on Mac."""
    try:
        # Check if Homebrew is already installed
        if get_package_manager() == "brew":
            return True
        
        print("Homebrew not found. Installing Homebrew first...")
        # Install Homebrew
        install_cmd = [
            "/bin/bash", "-c",
            "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ]
        subprocess.run(install_cmd, check=True, stdout=sys.stderr, stderr=sys.stderr)
        
        # Add Homebrew to PATH for current session
        homebrew_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
        for brew_path in homebrew_paths:
            if Path(brew_path).exists():
                current_path = os.environ.get("PATH", "")
                os.environ["PATH"] = f"{brew_path}:{current_path}"
                break
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Homebrew: {e}", file=sys.stderr)
        return False

def install_tesseract():
    """Install Tesseract OCR based on the operating system."""
    system = platform.system().lower()
    pkg_manager = get_package_manager()
    
    try:
        if system == "darwin":
            # Ensure Homebrew is available
            if pkg_manager != "brew":
                if not install_homebrew_if_needed():
                    raise RuntimeError("Homebrew installation failed")
            
            # Install Tesseract via Homebrew
            subprocess.run(["brew", "install", "tesseract"], check=True, stdout=sys.stderr, stderr=sys.stderr)

        elif system == "linux":
            if pkg_manager == "apt":
                subprocess.run(["sudo", "apt-get", "update"], check=True, stdout=sys.stderr, stderr=sys.stderr)
                subprocess.run(["sudo", "apt-get", "install", "-y", "tesseract-ocr"], check=True, stdout=sys.stderr, stderr=sys.stderr)
            elif pkg_manager == "dnf":
                subprocess.run(["sudo", "dnf", "install", "-y", "tesseract"], check=True, stdout=sys.stderr, stderr=sys.stderr)
            elif pkg_manager == "pacman":
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "tesseract"], check=True, stdout=sys.stderr, stderr=sys.stderr)

        elif system == "windows" and pkg_manager == "winget":
            subprocess.run(["winget", "install", "UB-Mannheim.TesseractOCR", 
                           "--accept-source-agreements", "--accept-package-agreements"], 
                          check=True, shell=True, stdout=sys.stderr, stderr=sys.stderr)
                
        print("Tesseract OCR installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing Tesseract: {str(e)}", file=sys.stderr)
        print("Please install Tesseract manually:", file=sys.stderr)
        print("- macOS: Install Homebrew first, then run 'brew install tesseract'", file=sys.stderr)
        print("  Homebrew install: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", file=sys.stderr)
        print("- Ubuntu/Debian: sudo apt-get install tesseract-ocr", file=sys.stderr)
        print("- Fedora: sudo dnf install tesseract", file=sys.stderr)
        print("- Arch: sudo pacman -S tesseract", file=sys.stderr)
        print("- Windows: winget install UB-Mannheim.TesseractOCR", file=sys.stderr)
        print("- Windows (manual): https://github.com/UB-Mannheim/tesseract/wiki", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    install_tesseract()
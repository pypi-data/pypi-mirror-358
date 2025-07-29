# wincontd – Lightweight Windows Container CLI

A lightweight alternative to Docker Desktop for Windows. No WSL2 required.

## ✨ Features

- Runs native Windows containers
- No WSL2 or Docker Desktop needed
- Supports Docker CLI via `nerdctl`
- Easy install & activation

## 🚀 Usage

```powershell
pip install wincontd
wincontd install
wincontd start
wincontd activate
docker run mcr.microsoft.com/windows/nanoserver:ltsc2022 echo "Hello from Windows container!"
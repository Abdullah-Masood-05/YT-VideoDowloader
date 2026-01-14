# YouTube Video Downloader

This project allows you to download YouTube videos at a specified resolution using **`yt-dlp`**.
It relies on **FFmpeg** to merge video and audio streams into a single **MP4** file.

---

## Requirements

* **Python 3.8+**
* **FFmpeg (REQUIRED)**
* **yt-dlp (Python library)**

⚠️ **FFmpeg must be installed before using this script.**
Without FFmpeg, yt-dlp cannot merge video and audio streams.

---

## 1️⃣ Install FFmpeg (Required)

FFmpeg is used internally by yt-dlp for merging and processing media files.

### Windows

#### Winget

```sh
winget install "FFmpeg (Essentials Build)"
```

#### Chocolatey

```sh
choco install ffmpeg
```

---

### macOS

#### Homebrew

```sh
brew install ffmpeg
```

---

### Linux

#### Ubuntu / Debian

```sh
sudo apt update
sudo apt install ffmpeg
```

#### Fedora

```sh
sudo dnf install ffmpeg
```

#### Arch Linux

```sh
sudo pacman -S ffmpeg
```

---

### Verify FFmpeg Installation

```sh
ffmpeg -version
```

If this command works, FFmpeg is correctly installed.

---

## 2️⃣ Set Up a Python Virtual Environment (Recommended)

Using a virtual environment keeps dependencies isolated and avoids conflicts.

### Create the virtual environment

```sh
python -m venv venv
```

---

### Activate the virtual environment

⚠️ **Activation command depends on how Python created the venv**

#### Windows (PowerShell / Git Bash / MSYS)

If your `venv` folder contains **`bin`** (as shown below), use:

```sh
venv\bin\activate
```

If your `venv` folder contains **`Scripts`**, use:

```powershell
.\venv\Scripts\Activate.ps1
```

Your reference output shows:
>
> ```
> venv/
> ├── bin/
> ├── include/
> ├── lib/
> └── pyvenv.cfg
> ```

✔ This means `venv\bin\activate` is the correct command.

---

#### Linux / macOS

```sh
source venv/bin/activate
```

---

### Verify venv is active

Your terminal prompt should change to:

```text
(venv)
```

---

## 3️⃣ Install yt-dlp

Once the virtual environment is activated:

```sh
pip install -U yt-dlp
```

(Optional but recommended)

```sh
python -m pip install --upgrade pip
```

---

## 4️⃣ Usage

1. Ensure **FFmpeg** is installed and accessible.
2. Activate the **virtual environment**.
3. Run the downloader script:

```sh
python Downloader.py
```

4. Replace the YouTube URL in the script with your desired video link.

The downloaded video will be automatically saved as an **MP4 file**.

---

## Notes

* FFmpeg is mandatory for:

  * Merging video + audio
  * Producing MP4 output
* If FFmpeg is missing:

  * Downloads may fail
  * Or video and audio may be saved separately
* `yt-dlp` is actively maintained and frequently updated

---
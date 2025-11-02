# hok/downloader.py
import sys
import os
import stat
import httpx
import zstandard
import hashlib
from pathlib import Path
from typing import Optional
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

EXECUTABLE_URLS = {
    "linux": "https://cdn.jsdelivr.net/gh/SSL-ACTX/cdn_purposes@refs/heads/main/camp-security-linux64.zst",
    "win32": "https://cdn.jsdelivr.net/gh/SSL-ACTX/cdn_purposes@refs/heads/main/camp-security-win64.exe.zst",
    "darwin": "https://cdn.jsdelivr.net/gh/SSL-ACTX/cdn_purposes@refs/heads/main/camp-security-macos64.zst",
}

KNOWN_HASHES = {
    "linux": "5df6e4dd0fa8bcb4dd685f0e75b99f67c263f61b0edf92b0dec3c1e403acb83e",
    "win32": "807805ed4b453c0a603e3ef4fb637fda5af8e0f397d58c8dd64dc1545b8c49e2",
    "darwin": "7caa8dfb70e9d439480e2a73bc2f3d093b9cba77d6ff8449ede707baf4b666b7",
}

def get_platform_executable_name() -> str:
    """Returns the name of the executable for the current platform."""
    if sys.platform == "win32":
        return "camp-security.exe"
    return "camp-security"

def verify_hash(data: bytes, platform_key: str) -> bool:
    """Verifies the SHA-256 hash of the downloaded data against the known good hash."""
    expected_hash = KNOWN_HASHES.get(platform_key)
    if not expected_hash:
        raise RuntimeError(f"Hash not found for platform '{platform_key}'.")

    actual_hash = hashlib.sha256(data).hexdigest()

    if actual_hash == expected_hash:
        print("✅ Hash verification successful.")
        return True
    else:
        print("🚨 CRITICAL: HASH MISMATCH! 🚨")
        print(f"  - Expected: {expected_hash}")
        print(f"  - Got:      {actual_hash}")
        print("  - The downloaded file is corrupt or has been tampered with. Aborting.")
        return False

async def download_and_decompress(url: str, destination: Path, platform_key: str):
    """Downloads a .zst compressed file, verifies its hash, and then decompresses it."""
    print(f"📥 Downloading executable from {url}...")
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, follow_redirects=True, timeout=60) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                compressed_data = bytearray()

                with Progress(
                    "[progress.description]{task.description}", BarColumn(),
                    "[progress.percentage]{task.percentage:>3.0f}%", "|",
                    DownloadColumn(), "|", TransferSpeedColumn(), "|", TimeRemainingColumn(),
                ) as progress:
                    download_task = progress.add_task("[cyan]Downloading...", total=total_size)
                    async for chunk in response.aiter_bytes():
                        compressed_data.extend(chunk)
                        progress.update(download_task, advance=len(chunk))

        # Verify the hash of the downloaded content
        if not verify_hash(compressed_data, platform_key):
            raise SecurityWarning("Downloaded file hash does not match the known good hash. Operation cancelled.")

        print("📦 Decompressing...")
        dctx = zstandard.ZstdDecompressor()
        decompressed_data = dctx.decompress(compressed_data)

        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "wb") as f:
            f.write(decompressed_data)

        if sys.platform != "win32":
            current_permissions = os.stat(destination).st_mode
            os.chmod(destination, current_permissions | stat.S_IXUSR)
            print("🔑 Made file executable.")

    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error occurred while downloading: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        print(f"❌ An error occurred during download/decompression: {e}")
        raise

def get_executable_path() -> Path:
    """Returns the designated path for the camp-security executable."""
    executable_name = get_platform_executable_name()
    return Path(__file__).parent / "bin" / executable_name

def get_short_executable_path() -> str:
    """Returns a shortened, user-friendly path for display."""
    path = get_executable_path()
    try:
        return f"~/{path.relative_to(Path.home())}"
    except ValueError:
        return f".../{'/'.join(path.parts[-3:])}"


async def ensure_executable_exists() -> Path:
    """
    Checks if the executable exists, and if not, downloads and verifies it.
    """
    executable_path = get_executable_path()
    short_path = get_short_executable_path()
    platform_key = sys.platform

    if executable_path.exists():
        print(f"✅ Found executable at: {short_path}")
        return executable_path

    print(f"🔎 Executable not found at {short_path}.")
    url = EXECUTABLE_URLS.get(platform_key)

    if not url:
        raise RuntimeError(f"❌ Unsupported platform: '{platform_key}'. No executable URL available.")

    await download_and_decompress(url, executable_path, platform_key)

    if not executable_path.exists():
        raise RuntimeError(f"❌ Download completed but executable still not found at {executable_path}.")

    print(f"✅ Executable saved to {short_path}")
    return executable_path

#!/usr/bin/env python3

import os
import subprocess
import sys

Import("env")

def generate_uf2(source, target, env):
    """Generate UF2 file from firmware binary for ESP32-S3 TFT Feather"""

    # Get the firmware binary path
    firmware_bin = str(target[0]).replace('.elf', '.bin')
    firmware_uf2 = str(target[0]).replace('.elf', '.uf2')

    # Path to uf2conv.py (should be in project root)
    project_dir = env.subst("$PROJECT_DIR")
    uf2conv_path = os.path.join(project_dir, "uf2conv.py")

    if not os.path.exists(uf2conv_path):
        print("Warning: uf2conv.py not found, skipping UF2 generation")
        return

    if not os.path.exists(firmware_bin):
        print(f"Warning: firmware binary not found at {firmware_bin}")
        return

    try:
        # Convert binary to UF2 format for ESP32-S3
        # Base address 0x10000 is the standard app partition start for ESP32-S3
        cmd = [
            sys.executable, uf2conv_path,
            firmware_bin,
            "--base", "0x10000",
            "--family", "ESP32S3",
            "--output", firmware_uf2
        ]

        print(f"Generating UF2: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ UF2 generated successfully: {firmware_uf2}")
            print(f"📁 File size: {os.path.getsize(firmware_uf2)} bytes")

            # Check if UF2 bootloader drive is mounted
            uf2_paths = [
                "/media/*/FTHRS3BOOT",
                "/media/$USER/FTHRS3BOOT",
                "/Volumes/FTHRS3BOOT"  # macOS
            ]

            for path_pattern in uf2_paths:
                import glob
                matches = glob.glob(path_pattern)
                if matches:
                    uf2_drive = matches[0]
                    try:
                        import shutil
                        dest_file = os.path.join(uf2_drive, "NEW.UF2")
                        shutil.copy2(firmware_uf2, dest_file)
                        print(f"🚀 Automatically flashed to {uf2_drive}")
                        break
                    except Exception as e:
                        print(f"Could not auto-flash to {uf2_drive}: {e}")
            else:
                print("💡 To flash: Double-click RESET button and copy firmware.uf2 to FTHRS3BOOT drive")

        else:
            print(f"❌ UF2 conversion failed:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")

    except Exception as e:
        print(f"❌ Error generating UF2: {e}")

# Add the UF2 generation as a post-action after building the ELF file
env.AddPostAction("$BUILD_DIR/${PROGNAME}.elf", generate_uf2)

print("🔧 UF2 generation script loaded for ESP32-S3 TFT Feather")

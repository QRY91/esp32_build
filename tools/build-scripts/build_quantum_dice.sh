#!/bin/bash

# Quantum Dice App Build Script
# Purpose: Build and deploy Quantum Dice Flipper Zero application
# Part of: DeskHog Build Project - PostHog Application Portfolio
# Author: QRY Labs

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
QUANTUM_DICE_PATH="$PROJECT_ROOT/flipper-zero/quantum-dice"
FIRMWARE_PATH="$HOME/flipper-zero-firmware"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Flipper firmware directory exists
    if [ ! -d "$FIRMWARE_PATH" ]; then
        log_error "Flipper firmware not found at $FIRMWARE_PATH"
        log_info "Please run setup_flipper_dev.sh first"
        exit 1
    fi

    # Check if fbt exists
    if [ ! -f "$FIRMWARE_PATH/fbt" ]; then
        log_error "Flipper Build Tool (fbt) not found"
        exit 1
    fi

    # Check if Quantum Dice app exists
    if [ ! -d "$QUANTUM_DICE_PATH" ]; then
        log_error "Quantum Dice app not found at $QUANTUM_DICE_PATH"
        exit 1
    fi

    # Check if application.fam exists
    if [ ! -f "$QUANTUM_DICE_PATH/application.fam" ]; then
        log_error "application.fam not found in Quantum Dice app"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Copy app to firmware directory
setup_app_in_firmware() {
    log_info "Setting up Quantum Dice app in firmware directory..."

    # Create applications_user directory if it doesn't exist
    mkdir -p "$FIRMWARE_PATH/applications_user"

    APP_TARGET_DIR="$FIRMWARE_PATH/applications_user/quantum_dice"

    # Remove existing app if present
    if [ -d "$APP_TARGET_DIR" ]; then
        log_info "Removing existing Quantum Dice app from firmware directory"
        rm -rf "$APP_TARGET_DIR"
    fi

    # Copy our app to firmware directory
    cp -r "$QUANTUM_DICE_PATH" "$APP_TARGET_DIR"

    log_success "Quantum Dice app copied to firmware directory"
}

# Build the application
build_app() {
    log_info "Building Quantum Dice application..."

    cd "$FIRMWARE_PATH"

    # Build our Quantum Dice app
    log_info "Running fbt build..."
    if ./fbt build APPSRC=applications_user/quantum_dice; then
        log_success "Quantum Dice app built successfully"
    else
        log_error "Failed to build Quantum Dice app"
        exit 1
    fi

    # Check if the .fap file was created
    FAP_FILE="./build/f7-firmware-D/.extapps/quantum_dice.fap"
    if [ -f "$FAP_FILE" ]; then
        log_success "Quantum Dice app package created: $FAP_FILE"

        # Copy FAP file back to project directory for easy access
        cp "$FAP_FILE" "$PROJECT_ROOT/quantum_dice.fap"
        log_info "App package copied to project root: quantum_dice.fap"
    else
        log_warning "Could not locate quantum_dice.fap file at expected location"
    fi
}

# Flash application to connected Flipper Zero
flash_app() {
    log_info "Preparing to flash Quantum Dice app to Flipper Zero..."

    cd "$FIRMWARE_PATH"

    # Check if Flipper Zero is connected
    if ! lsusb | grep -q "0483:5740"; then
        log_warning "Flipper Zero not detected via USB"
        log_info "Please ensure:"
        log_info "1. Flipper Zero is connected via USB"
        log_info "2. Flipper Zero is powered on"
        log_info "3. USB cable supports data transfer"
        read -p "Press Enter when Flipper Zero is ready, or Ctrl+C to cancel..."
    fi

    # Launch the app on connected Flipper
    log_info "Launching Quantum Dice app on Flipper Zero..."
    if ./fbt launch APPSRC=applications_user/quantum_dice; then
        log_success "Quantum Dice app launched on Flipper Zero!"
        log_info "The app should now be running on your Flipper Zero"
        log_info "Press Back button on Flipper to exit the app"
    else
        log_error "Failed to launch app on Flipper Zero"
        log_info "Try manually installing the .fap file via qFlipper or SD card"
    fi
}

# Install app to SD card (alternative method)
install_to_sd() {
    log_info "Installing Quantum Dice app to SD card..."

    # Look for mounted SD card or ask user for path
    SD_PATHS=("/media/$USER/flipper" "/mnt/flipper" "/run/media/$USER/flipper")
    SD_PATH=""

    for path in "${SD_PATHS[@]}"; do
        if [ -d "$path" ]; then
            SD_PATH="$path"
            break
        fi
    done

    if [ -z "$SD_PATH" ]; then
        log_info "SD card not found in common mount points"
        read -p "Enter path to mounted Flipper SD card (or press Enter to skip): " SD_PATH

        if [ -z "$SD_PATH" ] || [ ! -d "$SD_PATH" ]; then
            log_warning "Skipping SD card installation"
            return 0
        fi
    fi

    # Create apps directory if it doesn't exist
    mkdir -p "$SD_PATH/apps/Games"

    # Copy the .fap file
    if [ -f "$PROJECT_ROOT/quantum_dice.fap" ]; then
        cp "$PROJECT_ROOT/quantum_dice.fap" "$SD_PATH/apps/Games/"
        log_success "Quantum Dice app installed to SD card"
        log_info "You can now find the app in Games category on your Flipper Zero"
    else
        log_error "quantum_dice.fap not found. Please build the app first."
    fi
}

# Clean build artifacts
clean_build() {
    log_info "Cleaning build artifacts..."

    cd "$FIRMWARE_PATH"

    # Clean build directory
    if [ -d "./build" ]; then
        rm -rf ./build
        log_info "Build directory cleaned"
    fi

    # Remove app from firmware directory
    APP_TARGET_DIR="$FIRMWARE_PATH/applications_user/quantum_dice"
    if [ -d "$APP_TARGET_DIR" ]; then
        rm -rf "$APP_TARGET_DIR"
        log_info "Quantum Dice app removed from firmware directory"
    fi

    # Remove .fap file from project root
    if [ -f "$PROJECT_ROOT/quantum_dice.fap" ]; then
        rm "$PROJECT_ROOT/quantum_dice.fap"
        log_info "Quantum Dice app package removed from project root"
    fi

    log_success "Clean completed"
}

# Display usage information
show_usage() {
    echo "Quantum Dice App Build Script"
    echo "============================="
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  build     - Build the Quantum Dice app"
    echo "  flash     - Build and flash app to connected Flipper Zero"
    echo "  install   - Build and install app to SD card"
    echo "  clean     - Clean build artifacts"
    echo "  help      - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 build     # Just build the app"
    echo "  $0 flash     # Build and launch on Flipper"
    echo "  $0 install   # Build and copy to SD card"
    echo
    echo "Prerequisites:"
    echo "  - Run setup_flipper_dev.sh first"
    echo "  - Flipper firmware cloned to ~/flipper-zero-firmware"
    echo "  - Quantum Dice app in flipper-zero/quantum-dice/"
}

# Display project info
show_project_info() {
    echo -e "${BLUE}QRY Labs - DeskHog Build Project${NC}"
    echo "================================="
    echo "Building PostHog DeskHog prototype through systematic embedded learning"
    echo
    echo "Current app: Quantum Dice"
    echo "Purpose: Educational dice game with extensible glyph system"
    echo "Next steps: Card glyphs, Roman numerals, and probability visualization"
    echo
}

# Main execution logic
main() {
    show_project_info

    case "${1:-help}" in
        "build")
            check_prerequisites
            setup_app_in_firmware
            build_app
            ;;
        "flash")
            check_prerequisites
            setup_app_in_firmware
            build_app
            flash_app
            ;;
        "install")
            check_prerequisites
            setup_app_in_firmware
            build_app
            install_to_sd
            ;;
        "clean")
            clean_build
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

#!/bin/bash

# QRY Hello App Build Script
# Purpose: Build and deploy QRY Hello Flipper Zero application
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
QRY_HELLO_PATH="$PROJECT_ROOT/flipper-zero/qry-hello"
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

    # Check if QRY Hello app exists
    if [ ! -d "$QRY_HELLO_PATH" ]; then
        log_error "QRY Hello app not found at $QRY_HELLO_PATH"
        exit 1
    fi

    # Check if application.fam exists
    if [ ! -f "$QRY_HELLO_PATH/application.fam" ]; then
        log_error "application.fam not found in QRY Hello app"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Copy app to firmware directory
setup_app_in_firmware() {
    log_info "Setting up QRY Hello app in firmware directory..."

    # Create applications_user directory if it doesn't exist
    mkdir -p "$FIRMWARE_PATH/applications_user"

    APP_TARGET_DIR="$FIRMWARE_PATH/applications_user/qry_hello"

    # Remove existing app if present
    if [ -d "$APP_TARGET_DIR" ]; then
        log_info "Removing existing QRY Hello app from firmware directory"
        rm -rf "$APP_TARGET_DIR"
    fi

    # Copy our app to firmware directory
    cp -r "$QRY_HELLO_PATH" "$APP_TARGET_DIR"

    log_success "QRY Hello app copied to firmware directory"
}

# Build the application
build_app() {
    log_info "Building QRY Hello application..."

    cd "$FIRMWARE_PATH"

    # Build our QRY Hello app
    log_info "Running fbt build..."
    if ./fbt build APPSRC=applications_user/qry_hello; then
        log_success "QRY Hello app built successfully"
    else
        log_error "Failed to build QRY Hello app"
        exit 1
    fi

    # Check if the .fap file was created
    FAP_FILE="./build/f7-firmware-D/.extapps/qry_hello.fap"
    if [ -f "$FAP_FILE" ]; then
        log_success "QRY Hello app package created: $FAP_FILE"

        # Copy FAP file back to project directory for easy access
        cp "$FAP_FILE" "$PROJECT_ROOT/qry_hello.fap"
        log_info "App package copied to project root: qry_hello.fap"
    else
        log_warning "Could not locate qry_hello.fap file at expected location"
    fi
}

# Flash application to connected Flipper Zero
flash_app() {
    log_info "Preparing to flash QRY Hello app to Flipper Zero..."

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
    log_info "Launching QRY Hello app on Flipper Zero..."
    if ./fbt launch APPSRC=applications_user/qry_hello; then
        log_success "QRY Hello app launched on Flipper Zero!"
        log_info "The app should now be running on your Flipper Zero"
        log_info "Press Back button on Flipper to exit the app"
    else
        log_error "Failed to launch app on Flipper Zero"
        log_info "Try manually installing the .fap file via qFlipper or SD card"
    fi
}

# Install app to SD card (alternative method)
install_to_sd() {
    log_info "Installing QRY Hello app to SD card..."

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
    if [ -f "$PROJECT_ROOT/qry_hello.fap" ]; then
        cp "$PROJECT_ROOT/qry_hello.fap" "$SD_PATH/apps/Games/"
        log_success "QRY Hello app installed to SD card"
        log_info "You can now find the app in Games category on your Flipper Zero"
    else
        log_error "qry_hello.fap not found. Please build the app first."
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
    APP_TARGET_DIR="$FIRMWARE_PATH/applications_user/qry_hello"
    if [ -d "$APP_TARGET_DIR" ]; then
        rm -rf "$APP_TARGET_DIR"
        log_info "QRY Hello app removed from firmware directory"
    fi

    # Remove .fap file from project root
    if [ -f "$PROJECT_ROOT/qry_hello.fap" ]; then
        rm "$PROJECT_ROOT/qry_hello.fap"
        log_info "QRY Hello app package removed from project root"
    fi

    log_success "Clean completed"
}

# Display usage information
show_usage() {
    echo "QRY Hello App Build Script"
    echo "========================="
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  build     - Build the QRY Hello app"
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
    echo "  - QRY Hello app in flipper-zero/qry-hello/"
}

# Display project info
show_project_info() {
    echo -e "${BLUE}QRY Labs - DeskHog Build Project${NC}"
    echo "================================="
    echo "Building PostHog DeskHog prototype through systematic embedded learning"
    echo
    echo "Current app: QRY Hello"
    echo "Purpose: Basic Flipper Zero development workflow validation"
    echo "Next steps: Hardware integration and game development"
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

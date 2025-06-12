#!/bin/bash

# Flipper Zero Development Environment Setup Script
# Purpose: Automated toolchain installation for QRY DeskHog prototyping
# Target: PopOS/Ubuntu systems
# Author: QRY Labs - DeskHog Build Project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running on supported system
check_system() {
    log_info "Checking system compatibility..."

    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_error "This script is designed for Linux systems (PopOS/Ubuntu)"
        exit 1
    fi

    # Check for Ubuntu/PopOS
    if ! grep -q "Ubuntu\|Pop" /etc/os-release 2>/dev/null; then
        log_warning "This script is optimized for Ubuntu/PopOS. Other distros may require modifications."
    fi

    log_success "System check passed"
}

# Install system dependencies
install_dependencies() {
    log_info "Installing system dependencies..."

    # Update package lists
    sudo apt update

    # Install core development tools
    sudo apt install -y \
        git \
        curl \
        wget \
        python3 \
        python3-pip \
        python3-venv \
        build-essential \
        clang-format \
        clang-tidy \
        cmake \
        ninja-build \
        libusb-1.0-0-dev \
        libudev-dev \
        pkg-config \
        gcc-arm-none-eabi

    # Install additional tools for development
    sudo apt install -y \
        screen \
        minicom \
        dfu-util \
        openocd

    log_success "System dependencies installed"
}

# Install udev rules for Flipper Zero
install_udev_rules() {
    log_info "Installing udev rules for Flipper Zero..."

    # Create udev rule for Flipper Zero
    sudo tee /etc/udev/rules.d/42-flipperzero.rules > /dev/null <<EOF
# Flipper Zero DFU
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="df11", MODE="0666", GROUP="dialout"
# Flipper Zero Serial
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666", GROUP="dialout"
# Flipper Zero Virtual COM Port
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="5740", MODE="0666", GROUP="dialout"
EOF

    # Add user to dialout group
    sudo usermod -a -G dialout $USER

    # Reload udev rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger

    log_success "Udev rules installed. You may need to log out and back in for group changes to take effect."
}

# Setup Flipper Zero firmware repository
setup_flipper_firmware() {
    log_info "Setting up Flipper Zero firmware repository..."

    # Create firmware directory
    FIRMWARE_DIR="$HOME/flipper-firmware"

    if [ -d "$FIRMWARE_DIR" ]; then
        log_warning "Firmware directory already exists at $FIRMWARE_DIR"
        read -p "Do you want to remove it and start fresh? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$FIRMWARE_DIR"
        else
            log_info "Skipping firmware repository setup"
            return 0
        fi
    fi

    # Clone firmware repository
    log_info "Cloning Flipper Zero firmware repository..."
    git clone --recursive https://github.com/flipperdevices/flipperzero-firmware.git "$FIRMWARE_DIR"

    cd "$FIRMWARE_DIR"

    # Initial toolchain setup
    log_info "Running initial firmware build test (this may take several minutes)..."
    ./fbt

    log_success "Flipper Zero firmware repository setup complete"
}

# Setup Python virtual environment for development
setup_python_env() {
    log_info "Setting up Python development environment..."

    VENV_DIR="$HOME/.flipper-venv"

    # Create virtual environment
    python3 -m venv "$VENV_DIR"

    # Activate and install required packages
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install pyserial pillow

    # Create activation script
    cat > "$HOME/activate-flipper-env.sh" <<EOF
#!/bin/bash
# Flipper Zero Development Environment Activation
export FLIPPER_FIRMWARE_PATH="$HOME/flipper-firmware"
source "$VENV_DIR/bin/activate"
echo "Flipper Zero development environment activated"
echo "Firmware path: \$FLIPPER_FIRMWARE_PATH"
EOF

    chmod +x "$HOME/activate-flipper-env.sh"

    log_success "Python development environment setup complete"
}

# Test the installation
test_installation() {
    log_info "Testing Flipper Zero toolchain installation..."

    cd "$HOME/flipper-firmware"

    # Test firmware compilation
    log_info "Testing firmware compilation..."
    if ./fbt firmware_cdb; then
        log_success "Firmware compilation test passed"
    else
        log_error "Firmware compilation test failed"
        return 1
    fi

    # Test external app compilation
    log_info "Testing external app compilation..."
    if ./fbt apps; then
        log_success "External app compilation test passed"
    else
        log_error "External app compilation test failed"
        return 1
    fi

    log_success "Installation tests completed successfully"
}

# Create development workspace
create_workspace() {
    log_info "Creating development workspace..."

    WORKSPACE_DIR="$HOME/flipper-workspace"
    mkdir -p "$WORKSPACE_DIR"

    # Create example external app structure
    mkdir -p "$WORKSPACE_DIR/external-apps/hello_world"

    # Create basic app template
    cat > "$WORKSPACE_DIR/external-apps/hello_world/application.fam" <<EOF
App(
    appid="hello_world",
    name="Hello World",
    apptype=FlipperAppType.EXTERNAL,
    entry_point="hello_world_app",
    requires=["gui"],
    stack_size=1 * 1024,
)
EOF

    # Create development helper script
    cat > "$WORKSPACE_DIR/build_and_flash.sh" <<EOF
#!/bin/bash
# Helper script for building and flashing Flipper Zero apps
FIRMWARE_PATH="\$HOME/flipper-firmware"
cd "\$FIRMWARE_PATH"

echo "Building external apps..."
./fbt apps

echo "To flash to Flipper Zero:"
echo "1. Connect Flipper Zero via USB"
echo "2. Put Flipper in DFU mode (Left + Back while powering on)"
echo "3. Run: ./fbt flash"
EOF

    chmod +x "$WORKSPACE_DIR/build_and_flash.sh"

    log_success "Development workspace created at $WORKSPACE_DIR"
}

# Display completion message and next steps
show_completion_message() {
    log_success "Flipper Zero development environment setup complete!"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Log out and back in (or reboot) to apply group changes"
    echo "2. Activate development environment: source ~/activate-flipper-env.sh"
    echo "3. Connect your Flipper Zero and test with: cd ~/flipper-firmware && ./fbt launch"
    echo "4. Start developing in: ~/flipper-workspace/"
    echo
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "• Build firmware: cd ~/flipper-firmware && ./fbt"
    echo "• Build and flash: cd ~/flipper-firmware && ./fbt flash"
    echo "• Build external apps: cd ~/flipper-firmware && ./fbt apps"
    echo "• Launch app on connected Flipper: cd ~/flipper-firmware && ./fbt launch APPSRC=<path-to-app>"
    echo
    echo -e "${BLUE}Documentation:${NC}"
    echo "• Flipper Zero docs: https://docs.flipperzero.one/"
    echo "• Development guide: https://github.com/flipperdevices/flipperzero-firmware/blob/dev/documentation/AppManifests.md"
    echo
    echo -e "${GREEN}Happy hacking with your Flipper Zero! 🐬${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}QRY Labs - Flipper Zero Development Setup${NC}"
    echo "=========================================="
    echo

    check_system
    install_dependencies
    install_udev_rules
    setup_flipper_firmware
    setup_python_env
    test_installation
    create_workspace
    show_completion_message
}

# Run main function
main "$@"

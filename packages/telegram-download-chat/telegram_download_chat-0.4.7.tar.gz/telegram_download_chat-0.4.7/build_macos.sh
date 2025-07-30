#!/bin/bash
# Build script for macOS
# Usage: ./build_macos.sh

# Stop on first error and print commands
set -euo pipefail

# Get the current version from setuptools-scm
VERSION=$(python -c "from setuptools_scm import get_version; print(get_version(root='..'))")
VERSION_MAJOR_MINOR=$(echo "$VERSION" | cut -d. -f1,2)

echo "Building version: $VERSION"

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Ensure we're using the correct Python from the virtual environment
PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python"
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "Error: Python executable not found at $PYTHON_EXEC"
    exit 1
fi

# Install/update dependencies
echo "Installing/updating dependencies..."
"$PYTHON_EXEC" -m pip install --upgrade pip
"$PYTHON_EXEC" -m pip install -e ".[gui]"
"$PYTHON_EXEC" -m pip install pyinstaller Pillow>=10.0.0

# Apply patch for PySide6.QtAsyncio.events.py f-string syntax error
echo "Applying patch for PySide6.QtAsyncio.events.py..."
EVENTS_PY="$SCRIPT_DIR/venv/lib/python3.9/site-packages/PySide6/QtAsyncio/events.py"
if [ -f "$EVENTS_PY" ]; then
    patch -N -r - "$EVENTS_PY" < "$SCRIPT_DIR/patch_qtasyncio_events.patch" || true
else
    echo "Warning: Could not find $EVENTS_PY to apply patch"
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf "$SCRIPT_DIR/dist" "$SCRIPT_DIR/build" "$SCRIPT_DIR/telegram-download-chat.spec"

# Create a temporary directory for the build
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

# Create .icns file from icon.png if it doesn't exist
ICONSET_DIR="$SCRIPT_DIR/telegram-download-chat.iconset"
ICON_SRC="$SCRIPT_DIR/assets/icon.png"
ICONSET_DEST="$SCRIPT_DIR/telegram-download-chat.icns"

if [ ! -f "$ICONSET_DEST" ]; then
    echo "Creating .icns file..."
    mkdir -p "$ICONSET_DIR"
    
    # Create icons of different sizes
    sips -z 16 16     "$ICON_SRC" --out "$ICONSET_DIR/icon_16x16.png" > /dev/null
    sips -z 32 32     "$ICON_SRC" --out "$ICONSET_DIR/icon_16x16@2x.png" > /dev/null
    sips -z 32 32     "$ICON_SRC" --out "$ICONSET_DIR/icon_32x32.png" > /dev/null
    sips -z 64 64     "$ICON_SRC" --out "$ICONSET_DIR/icon_32x32@2x.png" > /dev/null
    sips -z 128 128   "$ICON_SRC" --out "$ICONSET_DIR/icon_128x128.png" > /dev/null
    sips -z 256 256   "$ICON_SRC" --out "$ICONSET_DIR/icon_128x128@2x.png" > /dev/null
    sips -z 256 256   "$ICON_SRC" --out "$ICONSET_DIR/icon_256x256.png" > /dev/null
    sips -z 512 512   "$ICON_SRC" --out "$ICONSET_DIR/icon_256x256@2x.png" > /dev/null
    sips -z 512 512   "$ICON_SRC" --out "$ICONSET_DIR/icon_512x512.png" > /dev/null
    sips -z 1024 1024 "$ICON_SRC" --out "$ICONSET_DIR/icon_512x512@2x.png" > /dev/null
    
    # Create .icns file
    iconutil -c icns "$ICONSET_DIR" -o "$ICONSET_DEST"
    
    # Clean up
    rm -rf "$ICONSET_DIR"
fi

# Create a temporary entitlements file with proper XML declaration and formatting
ENTITLEMENTS_FILE="$SCRIPT_DIR/entitlements.plist"
cat > "$ENTITLEMENTS_FILE" << 'EOL'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
</dict>
</plist>
EOL

# Build the app bundle with PyInstaller
echo "Building macOS app bundle..."
"$PYTHON_EXEC" -m PyInstaller \
    --clean \
    --noconfirm \
    --windowed \
    --name "telegram-download-chat" \
    --icon "$ICONSET_DEST" \
    --hidden-import telegram_download_chat.core \
    --hidden-import telegram_download_chat.paths \
    --hidden-import telegram_download_chat._pyinstaller \
    --add-data "$SCRIPT_DIR/assets/icon.png:assets" \
    --paths "$SCRIPT_DIR/src" \
    --additional-hooks-dir "$SCRIPT_DIR/src/_pyinstaller_hooks" \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR" \
    --osx-bundle-identifier "com.popstas.telegram-download-chat" \
    --osx-entitlements-file "$ENTITLEMENTS_FILE" \
    "$SCRIPT_DIR/launcher.py"

# Clean up the entitlements file
rm -f "$ENTITLEMENTS_FILE"

# Remove any existing quarantine attributes
xattr -cr "$SCRIPT_DIR/dist/telegram-download-chat.app"

# Sign the app with ad-hoc signature and hardened runtime
codesign --force --deep --sign - --timestamp \
    --options runtime \
    --entitlements "$ENTITLEMENTS_FILE" \
    --no-strict \
    "$SCRIPT_DIR/dist/telegram-download-chat.app"

# Verify the signature
codesign -dv --verbose=4 "$SCRIPT_DIR/dist/telegram-download-chat.app"

# Remove quarantine attributes again after signing
xattr -dr com.apple.quarantine "$SCRIPT_DIR/dist/telegram-download-chat.app" 2>/dev/null || true

# Create a nicer app bundle structure
# Use the actual app bundle name generated by PyInstaller (lowercase with hyphens)
APP_PATH="$SCRIPT_DIR/dist/telegram-download-chat.app"
CONTENTS_DIR="$APP_PATH/Contents"

# Create Resources directory if it doesn't exist
mkdir -p "$CONTENTS_DIR/Resources"

# Create Info.plist with version substitution
TMP_PLIST=$(mktemp)
cat > "$TMP_PLIST" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>telegram-download-chat</string>
    <key>CFBundleDisplayName</key>
    <string>telegram-download-chat</string>
    <key>CFBundleIdentifier</key>
    <string>com.popstas.telegram-download-chat</string>
    <key>CFBundleVersion</key>
    <string>__VERSION__</string>
    <key>CFBundleShortVersionString</key>
    <string>__VERSION_MAJOR_MINOR__</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleExecutable</key>
    <string>telegram-download-chat</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>
EOF

# Replace placeholders with actual version values
sed -i.bak "s/__VERSION__/$VERSION/g; s/__VERSION_MAJOR_MINOR__/$VERSION_MAJOR_MINOR/g" "$TMP_PLIST"
mv "$TMP_PLIST" "$CONTENTS_DIR/Info.plist"
rm -f "${TMP_PLIST}.bak"

# Copy icon to Resources
cp "$ICONSET_DEST" "$CONTENTS_DIR/Resources/AppIcon.icns"

# Make sure the executable has the right permissions
chmod +x "$CONTENTS_DIR/MacOS/telegram-download-chat"

# Create DMG
echo "Creating DMG..."
DMG_NAME="telegram-download-chat.dmg"
DMG_TEMP_DIR="$SCRIPT_DIR/dmg_temp"
DMG_APP_DIR="$DMG_TEMP_DIR/telegram-download-chat.app"

# Create a clean directory structure
mkdir -p "$DMG_TEMP_DIR/.background"
cp -R "$APP_PATH" "$DMG_APP_DIR"
ln -s /Applications "$DMG_TEMP_DIR/Applications"

# Calculate DMG size (app size + 20% extra)
APP_SIZE=$(du -sm "$DMG_APP_DIR" | cut -f1)
DMG_SIZE=$((APP_SIZE * 120 / 100))m

# Create temporary DMG
hdiutil create \
    -volname "telegram-download-chat" \
    -srcfolder "$DMG_TEMP_DIR" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size "$DMG_SIZE" \
    "$SCRIPT_DIR/dist/telegram-download-chat-temp.dmg"

# Mount the temporary DMG
MOUNT_POINT="/Volumes/telegram-download-chat"
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "$SCRIPT_DIR/dist/telegram-download-chat-temp.dmg" | \
         egrep '^/dev/' | sed 1q | awk '{print $1}')

# Wait for the volume to be mounted
sleep 5

# Set the window properties
osascript <<EOT
    tell application "Finder"
        tell disk "telegram-download-chat"
            open
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            set the bounds of container window to {400, 100, 900, 400}
            set viewOptions to the icon view options of container window
            set arrangement of viewOptions to not arranged
            set icon size of viewOptions to 80
            delay 2
            set position of item "telegram-download-chat.app" of container window to {120, 100}
            set position of item "Applications" of container window to {380, 100}
            update without registering applications
            delay 5
            close
        end tell
    end tell
EOT

# Make sure everything is written
sync

# Unmount the temporary DMG
hdiutil detach "$DEVICE"

# Convert to compressed image and clean up
rm -f "$SCRIPT_DIR/dist/$DMG_NAME"
hdiutil convert "$SCRIPT_DIR/dist/telegram-download-chat-temp.dmg" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "$SCRIPT_DIR/dist/$DMG_NAME"
rm -f "$SCRIPT_DIR/dist/telegram-download-chat-temp.dmg"

# Clean up
rm -rf "$DMG_TEMP_DIR"

# Sign the DMG with ad-hoc signature (skip if not available)
if command -v codesign &> /dev/null; then
    codesign --force --sign - --timestamp \
        --options runtime \
        --entitlements "$ENTITLEMENTS_FILE" \
        --no-strict \
        "$SCRIPT_DIR/dist/$DMG_NAME" || true
fi

# Set the DMG to not show the "untrusted app" warning
xattr -c "$SCRIPT_DIR/dist/$DMG_NAME" 2>/dev/null || true
xattr -dr com.apple.quarantine "$SCRIPT_DIR/dist/$DMG_NAME" 2>/dev/null || true

# Verify the DMG (skip if not available)
if command -v hdiutil &> /dev/null; then
    hdiutil verify "$SCRIPT_DIR/dist/$DMG_NAME" || true
fi

# Create a verification report for debugging
spctl -a -t exec -vv "$SCRIPT_DIR/dist/telegram-download-chat.app" 2>&1 | tee "$SCRIPT_DIR/dist/code_sign_verify.txt" || true

echo "Build complete!"
echo "App bundle: $APP_PATH"
echo "DMG: $SCRIPT_DIR/dist/$DMG_NAME"

# Deactivate virtual environment
deactivate

exit 0

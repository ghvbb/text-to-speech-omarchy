#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' 

clear
echo -e "${BLUE}${BOLD}======================================${NC}"
echo -e "${CYAN}${BOLD}      APP INSTALLER FOR HYPRLAND      ${NC}"
echo -e "${BLUE}${BOLD}======================================${NC}"
echo ""

echo -e "${YELLOW}📝 What is the name of your Text-To-Speech?${NC}"
read -p "   > " USER_APP_NAME

APP_NAME=${USER_APP_NAME:-"Text-To-Speech"}
SAFE_NAME=$(echo "$APP_NAME" | tr ' ' '-')
SOURCE_DIR=$(pwd)
SOURCE_PATH="$SOURCE_DIR/main.py"
DESKTOP_DIR="$HOME/.local/share/applications"
HYPR_DIR="$HOME/.config/hypr"

if [ ! -f "$SOURCE_PATH" ]; then
    echo -e "\n${BOLD}[!] Error:${NC} main.py not found in $SOURCE_DIR"
    exit 1
fi

echo -e "\n${BLUE}🛠️  Processing...${NC}"

mkdir -p "$DESKTOP_DIR"
mkdir -p "$HYPR_DIR"

DESKTOP_CONTENT="[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=Launched via Hyprland Installer
Exec=python3 $SOURCE_PATH
Path=$SOURCE_DIR
Icon=utilities-terminal
Terminal=false
Categories=Utility;"

echo "$DESKTOP_CONTENT" > "$DESKTOP_DIR/$SAFE_NAME.desktop"
chmod +x "$DESKTOP_DIR/$SAFE_NAME.desktop"
cp "$DESKTOP_DIR/$SAFE_NAME.desktop" "$HYPR_DIR/"

# --- Success UI ---
echo -e "${GREEN}${BOLD}Installation Complete!${NC}"
echo -e "--------------------------------------"
echo -e "${CYAN}App Name:${NC}  $APP_NAME"
echo -e "${CYAN}Entry:${NC}     $DESKTOP_DIR/$SAFE_NAME.desktop"
echo -e "${CYAN}Hypr Config:${NC} $HYPR_DIR/$SAFE_NAME.desktop"
echo -e "--------------------------------------"
echo -e "${YELLOW}💡 Tip: Search for '$APP_NAME' in your app launcher (wofi/rofi).${NC}\n"

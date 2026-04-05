#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

install_gitleaks() {
    if command -v gitleaks &>/dev/null; then
        echo "  gitleaks already installed: $(gitleaks version)"
        return
    fi

    echo "  installing gitleaks..."
    case "$(uname -s)" in
        Darwin)
            brew install gitleaks
            ;;
        MINGW*|MSYS*)
            local dest="$HOME/.local/bin"
            mkdir -p "$dest"
            local version
            version=$(curl -sI "https://github.com/gitleaks/gitleaks/releases/latest" \
                | grep -i '^location:' | sed 's|.*/v||;s/\r//')
            local url="https://github.com/gitleaks/gitleaks/releases/download/v${version}/gitleaks_${version}_windows_x64.zip"
            local tmp
            tmp=$(mktemp -d)
            curl -sL "$url" -o "$tmp/gitleaks.zip"
            unzip -qo "$tmp/gitleaks.zip" gitleaks.exe -d "$dest"
            rm -rf "$tmp"
            echo "  installed gitleaks to $dest/gitleaks.exe"
            ;;
        *)
            echo "  WARNING: unsupported platform for gitleaks install, install manually"
            ;;
    esac
}

link() {
    local src="$1" dst="$2"
    mkdir -p "$(dirname "$dst")"

    if [ -L "$dst" ]; then
        rm "$dst"
    elif [ -e "$dst" ]; then
        echo "  backing up $dst -> ${dst}.bak"
        mv "$dst" "${dst}.bak"
    fi

    ln -s "$src" "$dst"
    echo "  $dst -> $src"
}

echo "Installing dotfiles from $DOTFILES"
echo

# gitleaks
echo "==> gitleaks"
install_gitleaks

# Pre-commit hook
echo "==> pre-commit hook"
link "$DOTFILES/hooks/pre-commit" "$DOTFILES/.git/hooks/pre-commit"

# Daily sync schedule (9:00 AM)
echo "==> sync schedule"
case "$(uname -s)" in
    Darwin)
        local_plist="$HOME/Library/LaunchAgents/com.dotfiles.sync.plist"
        mkdir -p "$(dirname "$local_plist")"
        cat > "$local_plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dotfiles.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>${DOTFILES}/sync.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${HOME}/.dotfiles-sync.log</string>
    <key>StandardErrorPath</key>
    <string>${HOME}/.dotfiles-sync.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PLIST
        # Unload first if already loaded, then load
        launchctl bootout gui/$(id -u) "$local_plist" 2>/dev/null || true
        launchctl bootstrap gui/$(id -u) "$local_plist"
        echo "  launchd job installed: com.dotfiles.sync (daily 09:00)"
        ;;
    MINGW*|MSYS*)
        win_bash=$(cygpath -w "/usr/bin/bash")
        win_script=$(cygpath -w "$DOTFILES/sync.sh")
        # Delete existing task if present, then create
        schtasks.exe //Delete //TN "DotfilesSync" //F 2>/dev/null || true
        schtasks.exe //Create //TN "DotfilesSync" //TR "\"${win_bash}\" -l -c \"${win_script}\"" //SC DAILY //ST 09:00 //F
        echo "  Task Scheduler job installed: DotfilesSync (daily 09:00)"
        ;;
    *)
        echo "  WARNING: unsupported platform for schedule setup, configure manually"
        ;;
esac

# Shell
echo "==> zsh"
link "$DOTFILES/zsh/.zshrc" "$HOME/.zshrc"
if [[ "$(uname)" == "Darwin" ]]; then
    link "$DOTFILES/zsh/.zshrc.local.mac" "$HOME/.zshrc.local"
elif grep -qi microsoft /proc/version 2>/dev/null; then
    link "$DOTFILES/zsh/.zshrc.local.wsl" "$HOME/.zshrc.local"
fi

# Git
echo "==> git"
link "$DOTFILES/git/.gitconfig" "$HOME/.gitconfig"

# SSH
echo "==> ssh"
link "$DOTFILES/ssh/config" "$HOME/.ssh/config"

# Vim
echo "==> vim"
link "$DOTFILES/vim/.vimrc" "$HOME/.vimrc"
link "$DOTFILES/vim/autoload" "$HOME/.vim/autoload"
link "$DOTFILES/vim/colors" "$HOME/.vim/colors"

# Claude Code
echo "==> claude"
link "$DOTFILES/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
link "$DOTFILES/claude/settings.json" "$HOME/.claude/settings.json"
link "$DOTFILES/claude/keybindings.json" "$HOME/.claude/keybindings.json"
link "$DOTFILES/claude/agents/blockhead-ops.md" "$HOME/.claude/agents/blockhead-ops.md"
link "$DOTFILES/claude/agents/buildbot.md" "$HOME/.claude/agents/buildbot.md"

# OpenCode
echo "==> opencode"
link "$DOTFILES/opencode/opencode.json" "$HOME/.config/opencode/opencode.json"

echo
echo "Done. Secrets go in ~/.zshrc.secrets (not tracked by git)."

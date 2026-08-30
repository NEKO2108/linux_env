#!/bin/sh
set -e

# 获取脚本自身的绝对路径（兼容 sh / bash source 执行）
if [ -n "$BASH_VERSION" ]; then
    SCRIPT_PATH="${BASH_SOURCE[0]}"
else
    SCRIPT_PATH="$0"
fi
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" && pwd)

# $1有值用$1，无值默认用脚本所在的绝对目录
TARGET_DIR="${1:-$SCRIPT_DIR}"

cd "${TARGET_DIR}"

# ========== 备份旧 vimrc（带时间戳） ==========
OLD_VIMRC="$HOME/.vimrc"
BACKUP_TIME=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$HOME/.vimrc.bak.${BACKUP_TIME}"

if [ -f "$OLD_VIMRC" ]; then
    cp "$OLD_VIMRC" "$BACKUP_FILE"
    echo ">> 已备份原有 vimrc 到: $BACKUP_FILE"
fi

cat "$TARGET_DIR/vimrcs/basic.vim" > ~/.vimrc

echo "Installed the Basic Vim configuration successfully! Enjoy :-)"

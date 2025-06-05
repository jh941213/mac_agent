#!/bin/bash

# Mac Agent 설치 스크립트
echo "🤖 Mac Agent 설치를 시작합니다..."

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 설치 디렉토리: $SCRIPT_DIR"

# Python 버전 확인
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
echo "🐍 Python 버전: $python_version"

# 설치 방법 선택
echo ""
echo "설치 방법을 선택하세요:"
echo "1) pip install (권장) - 전역 설치 및 의존성 자동 관리"
echo "2) 심볼릭 링크 - 빠른 설치"
echo ""
read -p "선택 (1 또는 2): " choice

case $choice in
    1)
        echo "📦 pip install로 설치 중..."
        pip install -e .
        if [ $? -eq 0 ]; then
            echo "✅ 설치 완료! 이제 어디서든 'mac_agent' 명령을 사용할 수 있습니다."
            echo ""
            echo "사용 예시:"
            echo "  mac_agent \"내일 오후 3시에 회의 일정 추가해줘\""
            echo "  mac_agent --help"
        else
            echo "❌ 설치 실패. pip install에 문제가 있습니다."
            exit 1
        fi
        ;;
    2)
        echo "🔗 심볼릭 링크로 설치 중..."
        
        # ~/.local/bin 디렉토리 생성
        mkdir -p ~/.local/bin
        
        # 심볼릭 링크 생성
        ln -sf "$SCRIPT_DIR/mac_agent" ~/.local/bin/mac_agent
        
        # PATH에 ~/.local/bin 추가 (필요한 경우)
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo "📝 PATH에 ~/.local/bin 추가 중..."
            
            # 사용 중인 셸 확인
            if [ -n "$ZSH_VERSION" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
                echo "~/.zshrc에 PATH 추가됨"
            elif [ -n "$BASH_VERSION" ]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
                echo "~/.bashrc에 PATH 추가됨"
            fi
            
            echo "⚠️  새 터미널을 열거나 다음 명령을 실행하세요:"
            echo "   source ~/.zshrc  (zsh 사용자)"
            echo "   source ~/.bashrc (bash 사용자)"
        fi
        
        echo "✅ 설치 완료! 이제 어디서든 'mac_agent' 명령을 사용할 수 있습니다."
        echo ""
        echo "사용 예시:"
        echo "  mac_agent \"내일 오후 3시에 회의 일정 추가해줘\""
        echo "  mac_agent --help"
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "🎉 Mac Agent 설치가 완료되었습니다!"
echo "📖 자세한 사용법은 README.md를 참고하세요." 
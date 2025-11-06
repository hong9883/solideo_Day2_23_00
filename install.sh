#!/bin/bash

echo "=========================================="
echo "시스템 리소스 모니터링 설치 스크립트"
echo "System Resource Monitoring Installer"
echo "=========================================="
echo ""

# Python 버전 확인
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 버전: $python_version"

# pip 설치 확인
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3가 설치되어 있지 않습니다."
    echo "다음 명령으로 설치하세요:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-pip"
    echo "  Fedora/RHEL: sudo dnf install python3-pip"
    exit 1
fi

echo "✅ pip3 발견"

# tkinter 설치 확인 (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! python3 -c "import tkinter" 2>/dev/null; then
        echo "⚠️  tkinter가 설치되어 있지 않습니다."
        echo "다음 명령으로 설치하세요:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  Fedora/RHEL: sudo dnf install python3-tkinter"
        read -p "계속하시겠습니까? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "✅ tkinter 발견"
    fi
fi

# 의존성 설치
echo ""
echo "📦 의존성 패키지 설치 중..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 설치 완료!"
    echo ""
    echo "실행 방법:"
    echo "  python3 main.py"
    echo ""
    echo "또는:"
    echo "  chmod +x run.sh"
    echo "  ./run.sh"
else
    echo ""
    echo "❌ 설치 중 오류 발생"
    exit 1
fi

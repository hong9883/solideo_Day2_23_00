#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Resource Monitoring Application
실시간 시스템 리소스 모니터링 및 PDF 보고서 생성

Usage:
    python main.py
"""

import tkinter as tk
from monitor.ui import MonitorUI


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("시스템 리소스 실시간 모니터링 시스템")
    print("System Resource Real-time Monitoring")
    print("=" * 50)
    print()

    # Tkinter 루트 윈도우 생성
    root = tk.Tk()

    # UI 인스턴스 생성 및 실행
    app = MonitorUI(root)

    print("UI가 시작되었습니다.")
    print("'시작' 버튼을 클릭하여 모니터링을 시작하세요.")
    print()

    # 이벤트 루프 실행
    app.run()


if __name__ == "__main__":
    main()

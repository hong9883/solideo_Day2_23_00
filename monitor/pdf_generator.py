# -*- coding: utf-8 -*-
"""
PDF Report Generator Module
Generates comprehensive system monitoring reports in PDF format with Korean support
"""

import os
import sys
import tempfile
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager, rc

from monitor.data_collector import SystemMonitor


class PDFReportGenerator:
    """PDF 보고서 생성기 (한글 지원)"""

    def __init__(self, monitor: SystemMonitor):
        self.monitor = monitor
        self.temp_images = []  # 임시 이미지 파일 리스트
        self.korean_font_path = None

        # 한글 폰트 설정
        self._setup_korean_font()
        self._setup_matplotlib_korean_font()

    def _download_nanum_font(self):
        """NanumGothic 폰트 다운로드 (폰트가 없는 경우)"""
        try:
            fonts_dir = Path.home() / '.fonts'
            fonts_dir.mkdir(exist_ok=True)

            font_file = fonts_dir / 'NanumGothic.ttf'

            if not font_file.exists():
                print("한글 폰트를 다운로드 중...")
                url = 'https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf'

                try:
                    urllib.request.urlretrieve(url, str(font_file))
                    print(f"폰트 다운로드 완료: {font_file}")
                    return str(font_file)
                except Exception as e:
                    print(f"폰트 다운로드 실패: {e}")
                    return None
            else:
                return str(font_file)

        except Exception as e:
            print(f"폰트 다운로드 중 오류: {e}")
            return None

    def _setup_korean_font(self):
        """한글 폰트 설정 (PDF용)"""
        try:
            # 시스템에서 한글 폰트 찾기
            font_paths = [
                # Linux - Ubuntu/Debian
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf',
                '/usr/share/fonts/truetype/nanum-gothic/NanumGothic.ttf',

                # Linux - Fedora/RHEL
                '/usr/share/fonts/nhn-nanum/NanumGothic.ttf',

                # macOS
                '/System/Library/Fonts/AppleSDGothicNeo.ttc',
                '/Library/Fonts/AppleGothic.ttf',

                # Windows
                'C:\\Windows\\Fonts\\malgun.ttf',  # 맑은 고딕
                'C:\\Windows\\Fonts\\gulim.ttc',   # 굴림

                # 사용자 홈 디렉토리
                str(Path.home() / '.fonts' / 'NanumGothic.ttf'),
            ]

            # 폰트 찾기
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Korean', font_path))
                        self.font_name = 'Korean'
                        self.korean_font_path = font_path
                        print(f"✅ PDF 한글 폰트 설정 완료: {font_path}")
                        return
                    except Exception as e:
                        print(f"폰트 로드 실패 ({font_path}): {e}")
                        continue

            # 폰트를 찾지 못한 경우 다운로드 시도
            print("시스템에서 한글 폰트를 찾을 수 없습니다.")
            downloaded_font = self._download_nanum_font()

            if downloaded_font and os.path.exists(downloaded_font):
                try:
                    pdfmetrics.registerFont(TTFont('Korean', downloaded_font))
                    self.font_name = 'Korean'
                    self.korean_font_path = downloaded_font
                    print(f"✅ PDF 한글 폰트 설정 완료 (다운로드): {downloaded_font}")
                    return
                except Exception as e:
                    print(f"다운로드한 폰트 로드 실패: {e}")

            # 최종적으로 폰트를 찾지 못한 경우
            print("⚠️  한글 폰트를 사용할 수 없습니다. 영문 폰트로 대체합니다.")
            print("   한글이 제대로 표시되지 않을 수 있습니다.")
            self.font_name = 'Helvetica'

        except Exception as e:
            print(f"폰트 설정 오류: {e}")
            self.font_name = 'Helvetica'

    def _setup_matplotlib_korean_font(self):
        """Matplotlib 한글 폰트 설정"""
        try:
            # 한글 폰트 찾기
            font_names = [
                'NanumGothic', 'NanumBarunGothic', 'NanumMyeongjo',
                'AppleGothic', 'Apple SD Gothic Neo',
                'Malgun Gothic', 'Gulim',
                'DejaVu Sans'  # 기본 폰트
            ]

            # 시스템에 설치된 폰트 확인
            available_fonts = [f.name for f in font_manager.fontManager.ttflist]

            # 첫 번째로 사용 가능한 폰트 선택
            selected_font = None
            for font_name in font_names:
                if font_name in available_fonts:
                    selected_font = font_name
                    break

            if selected_font:
                rc('font', family=selected_font)
                print(f"✅ Matplotlib 한글 폰트 설정 완료: {selected_font}")
            else:
                # 다운로드한 폰트가 있으면 사용
                if self.korean_font_path and os.path.exists(self.korean_font_path):
                    font_prop = font_manager.FontProperties(fname=self.korean_font_path)
                    plt.rcParams['font.family'] = font_prop.get_name()
                    print(f"✅ Matplotlib 한글 폰트 설정 완료: {self.korean_font_path}")
                else:
                    print("⚠️  Matplotlib에서 한글 폰트를 찾을 수 없습니다.")

            # 마이너스 기호 깨짐 방지
            plt.rcParams['axes.unicode_minus'] = False

        except Exception as e:
            print(f"Matplotlib 폰트 설정 오류: {e}")

    def generate_report(self) -> str:
        """PDF 보고서 생성 및 파일명 반환"""
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_report_{timestamp}.pdf"

        # PDF 문서 생성
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        # 스토리 (페이지 내용)
        story = []

        # 1. 표지
        story.extend(self._create_cover_page())

        # 2. 요약 통계
        story.append(PageBreak())
        story.extend(self._create_summary_statistics())

        # 3. 시계열 그래프
        story.append(PageBreak())
        story.extend(self._create_time_series_graphs())

        # 4. 프로세스 분석 (가능한 경우)
        if self.monitor.top_cpu_processes or self.monitor.top_memory_processes:
            story.append(PageBreak())
            story.extend(self._create_process_analysis())

        # PDF 빌드
        doc.build(story)

        # 임시 이미지 파일 삭제
        self._cleanup_temp_images()

        return filename

    def _create_cover_page(self):
        """표지 페이지 생성"""
        styles = getSampleStyleSheet()

        # 제목 스타일
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            fontName=self.font_name,
            leading=32
        )

        # 부제목 스타일
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            fontName=self.font_name,
            leading=18
        )

        elements = []

        # 제목
        elements.append(Spacer(1, 2 * inch))

        if self.font_name == 'Korean':
            elements.append(Paragraph("시스템 리소스 모니터링 보고서", title_style))
        else:
            elements.append(Paragraph("System Resource Monitoring Report", title_style))

        elements.append(Paragraph("System Resource Monitoring Report", subtitle_style))
        elements.append(Spacer(1, 0.5 * inch))

        # 모니터링 기간
        if self.monitor.timestamps:
            start_time = self.monitor.timestamps[0].strftime("%Y-%m-%d %H:%M:%S")
            end_time = self.monitor.timestamps[-1].strftime("%Y-%m-%d %H:%M:%S")
            duration = len(self.monitor.timestamps)

            if self.font_name == 'Korean':
                period_text = f"""
                <b>모니터링 기간 (Monitoring Period):</b><br/>
                시작: {start_time}<br/>
                종료: {end_time}<br/>
                샘플 수: {duration}개
                """
            else:
                period_text = f"""
                <b>Monitoring Period:</b><br/>
                Start: {start_time}<br/>
                End: {end_time}<br/>
                Samples: {duration}
                """

            elements.append(Paragraph(period_text, subtitle_style))
            elements.append(Spacer(1, 0.3 * inch))

        # 시스템 정보
        sys_info = self.monitor.get_system_info()
        if sys_info:
            if self.font_name == 'Korean':
                info_text = "<b>시스템 정보 (System Information):</b><br/>"
            else:
                info_text = "<b>System Information:</b><br/>"

            for key, value in sys_info.items():
                info_text += f"{key}: {value}<br/>"

            elements.append(Paragraph(info_text, subtitle_style))

        return elements

    def _create_summary_statistics(self):
        """요약 통계 표 생성"""
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontName=self.font_name,
            leading=20
        )

        elements = []

        if self.font_name == 'Korean':
            elements.append(Paragraph("요약 통계 (Summary Statistics)", heading_style))
        else:
            elements.append(Paragraph("Summary Statistics", heading_style))

        elements.append(Spacer(1, 0.2 * inch))

        # 통계 데이터 가져오기
        stats = self.monitor.get_statistics()

        # 표 데이터 (한글/영문 구분)
        if self.font_name == 'Korean':
            headers = ["항목 (Metric)", "평균 (Avg)", "최소 (Min)", "최대 (Max)"]
        else:
            headers = ["Metric", "Average", "Minimum", "Maximum"]

        data = [headers]

        for metric, values in stats.items():
            # 영문 전용 모드일 때는 영어로 변환
            if self.font_name != 'Korean':
                metric = metric.replace('CPU 사용률 (%)', 'CPU Usage (%)')
                metric = metric.replace('메모리 사용률 (%)', 'Memory Usage (%)')
                metric = metric.replace('디스크 읽기 (MB/s)', 'Disk Read (MB/s)')
                metric = metric.replace('디스크 쓰기 (MB/s)', 'Disk Write (MB/s)')
                metric = metric.replace('네트워크 송신 (MB/s)', 'Network Sent (MB/s)')
                metric = metric.replace('네트워크 수신 (MB/s)', 'Network Recv (MB/s)')
                metric = metric.replace('디스크 사용량 (%)', 'Disk Usage (%)')

            data.append([
                metric,
                f"{values['avg']:.2f}",
                f"{values['min']:.2f}",
                f"{values['max']:.2f}"
            ])

        # 표 생성
        table = Table(data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])

        # 표 스타일 (한글 폰트 적용)
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]

        # 한글 폰트가 있으면 적용
        if self.font_name == 'Korean':
            table_style.extend([
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ])
        else:
            table_style.extend([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ])

        table.setStyle(TableStyle(table_style))

        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_time_series_graphs(self):
        """시계열 그래프 생성"""
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontName=self.font_name,
            leading=20
        )

        elements = []

        if self.font_name == 'Korean':
            elements.append(Paragraph("시계열 그래프 (Time Series Graphs)", heading_style))
        else:
            elements.append(Paragraph("Time Series Graphs", heading_style))

        elements.append(Spacer(1, 0.2 * inch))

        if not self.monitor.timestamps:
            elements.append(Paragraph("No data available.", styles['Normal']))
            return elements

        timestamps = list(self.monitor.timestamps)

        # 1. CPU 사용률 그래프
        if self.monitor.cpu_percent:
            img_path = self._create_graph(
                timestamps,
                [list(self.monitor.cpu_percent)],
                ["CPU 사용률" if self.font_name == 'Korean' else "CPU Usage"],
                "CPU 사용률 (CPU Usage)" if self.font_name == 'Korean' else "CPU Usage (%)",
                "%",
                ["red"]
            )
            elements.append(Image(img_path, width=6 * inch, height=3 * inch))
            elements.append(Spacer(1, 0.2 * inch))

        # 2. 메모리 사용률 그래프
        if self.monitor.memory_percent:
            img_path = self._create_graph(
                timestamps,
                [list(self.monitor.memory_percent)],
                ["메모리 사용률" if self.font_name == 'Korean' else "Memory Usage"],
                "메모리 사용률 (Memory Usage)" if self.font_name == 'Korean' else "Memory Usage (%)",
                "%",
                ["blue"]
            )
            elements.append(Image(img_path, width=6 * inch, height=3 * inch))
            elements.append(Spacer(1, 0.2 * inch))

        # 페이지 넘김
        elements.append(PageBreak())

        # 3. 네트워크 트래픽 그래프
        if self.monitor.net_sent and self.monitor.net_recv:
            labels = ["송신", "수신"] if self.font_name == 'Korean' else ["Sent", "Received"]
            title = "네트워크 트래픽 (Network Traffic)" if self.font_name == 'Korean' else "Network Traffic (MB/s)"

            img_path = self._create_graph(
                timestamps,
                [list(self.monitor.net_sent), list(self.monitor.net_recv)],
                labels,
                title,
                "MB/s",
                ["green", "orange"]
            )
            elements.append(Image(img_path, width=6 * inch, height=3 * inch))
            elements.append(Spacer(1, 0.2 * inch))

        # 4. 디스크 I/O 그래프
        if self.monitor.disk_read and self.monitor.disk_write:
            labels = ["읽기", "쓰기"] if self.font_name == 'Korean' else ["Read", "Write"]
            title = "디스크 I/O (Disk I/O)" if self.font_name == 'Korean' else "Disk I/O (MB/s)"

            img_path = self._create_graph(
                timestamps,
                [list(self.monitor.disk_read), list(self.monitor.disk_write)],
                labels,
                title,
                "MB/s",
                ["purple", "pink"]
            )
            elements.append(Image(img_path, width=6 * inch, height=3 * inch))
            elements.append(Spacer(1, 0.2 * inch))

        return elements

    def _create_graph(self, timestamps, data_series, labels, title, ylabel, colors_list):
        """그래프 이미지 생성 및 임시 파일 경로 반환 (한글 지원)"""
        fig, ax = plt.subplots(figsize=(10, 5))

        for data, label, color in zip(data_series, labels, colors_list):
            ax.plot(timestamps, data, label=label, color=color, linewidth=2)

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel("시간 (Time)" if self.font_name == 'Korean' else "Time", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', prop={'size': 9})

        # X축 시간 포맷
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
        plt.close(fig)

        self.temp_images.append(temp_file.name)
        return temp_file.name

    def _create_process_analysis(self):
        """프로세스 분석 페이지 생성"""
        styles = getSampleStyleSheet()
        heading_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontName=self.font_name,
            leading=20
        )

        elements = []

        if self.font_name == 'Korean':
            elements.append(Paragraph("프로세스 분석 (Process Analysis)", heading_style))
        else:
            elements.append(Paragraph("Process Analysis", heading_style))

        elements.append(Spacer(1, 0.2 * inch))

        # CPU Top 5
        if self.monitor.top_cpu_processes:
            if self.font_name == 'Korean':
                elements.append(Paragraph("CPU 사용률 Top 5", styles['Heading3']))
            else:
                elements.append(Paragraph("Top 5 CPU Usage", styles['Heading3']))

            elements.append(Spacer(1, 0.1 * inch))

            headers = ["PID", "프로세스 이름", "CPU (%)"] if self.font_name == 'Korean' else ["PID", "Process Name", "CPU (%)"]
            data = [headers]

            for proc in self.monitor.top_cpu_processes:
                data.append([
                    str(proc['pid']),
                    proc['name'][:30],  # 이름 길이 제한
                    f"{proc['cpu_percent']:.2f}"
                ])

            table = Table(data, colWidths=[1 * inch, 4 * inch, 1.5 * inch])

            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]

            if self.font_name == 'Korean':
                table_style.append(('FONTNAME', (0, 0), (-1, -1), self.font_name))
            else:
                table_style.append(('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'))

            table.setStyle(TableStyle(table_style))

            elements.append(table)
            elements.append(Spacer(1, 0.3 * inch))

        # 메모리 Top 5
        if self.monitor.top_memory_processes:
            if self.font_name == 'Korean':
                elements.append(Paragraph("메모리 사용률 Top 5", styles['Heading3']))
            else:
                elements.append(Paragraph("Top 5 Memory Usage", styles['Heading3']))

            elements.append(Spacer(1, 0.1 * inch))

            headers = ["PID", "프로세스 이름", "메모리 (%)"] if self.font_name == 'Korean' else ["PID", "Process Name", "Memory (%)"]
            data = [headers]

            for proc in self.monitor.top_memory_processes:
                data.append([
                    str(proc['pid']),
                    proc['name'][:30],
                    f"{proc['memory_percent']:.2f}"
                ])

            table = Table(data, colWidths=[1 * inch, 4 * inch, 1.5 * inch])

            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]

            if self.font_name == 'Korean':
                table_style.append(('FONTNAME', (0, 0), (-1, -1), self.font_name))
            else:
                table_style.append(('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'))

            table.setStyle(TableStyle(table_style))

            elements.append(table)

        return elements

    def _cleanup_temp_images(self):
        """임시 이미지 파일 삭제"""
        for img_path in self.temp_images:
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception as e:
                print(f"임시 파일 삭제 오류: {e}")

        self.temp_images.clear()

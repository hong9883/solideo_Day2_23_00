# -*- coding: utf-8 -*-
"""
Real-time System Monitoring UI with Tkinter and Matplotlib
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from typing import Optional

from monitor.data_collector import SystemMonitor
from monitor.pdf_generator import PDFReportGenerator


class MonitorUI:
    """시스템 모니터링 실시간 UI"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("시스템 리소스 실시간 모니터링")
        self.root.geometry("1400x900")

        # 모니터 인스턴스
        self.monitor = SystemMonitor(max_samples=300)

        # UI 업데이트 타이머
        self.update_interval = 1000  # 1초
        self.update_job = None

        # 모니터링 시작 시간
        self.start_time: Optional[datetime] = None
        self.monitoring_seconds = 0

        # UI 구성
        self._setup_ui()

    def _setup_ui(self):
        """UI 레이아웃 구성"""
        # 상단: 컨트롤 패널
        self._create_control_panel()

        # 중단: 현재 상태 대시보드
        self._create_dashboard()

        # 하단: 실시간 그래프
        self._create_graphs()

    def _create_control_panel(self):
        """상단 컨트롤 패널 생성"""
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # 시작 버튼
        self.start_btn = ttk.Button(
            control_frame,
            text="시작 (Start)",
            command=self.start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # 중지 버튼
        self.stop_btn = ttk.Button(
            control_frame,
            text="중지 (Stop)",
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # PDF 생성 버튼
        self.pdf_btn = ttk.Button(
            control_frame,
            text="PDF 보고서 생성",
            command=self.generate_pdf,
            state=tk.DISABLED
        )
        self.pdf_btn.pack(side=tk.LEFT, padx=5)

        # 타이머 표시
        self.timer_label = ttk.Label(
            control_frame,
            text="경과 시간: 00:00 / 05:00",
            font=("Arial", 12, "bold")
        )
        self.timer_label.pack(side=tk.LEFT, padx=20)

        # 샘플 수 표시
        self.sample_label = ttk.Label(
            control_frame,
            text="수집 샘플: 0 / 300",
            font=("Arial", 10)
        )
        self.sample_label.pack(side=tk.LEFT, padx=10)

        # 상태 표시
        self.status_label = ttk.Label(
            control_frame,
            text="준비",
            font=("Arial", 10),
            foreground="blue"
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

    def _create_dashboard(self):
        """현재 상태 대시보드 생성"""
        dashboard_frame = ttk.LabelFrame(self.root, text="현재 시스템 상태", padding="10")
        dashboard_frame.pack(fill=tk.X, padx=10, pady=5)

        # 2행 4열 그리드
        metrics = [
            ("CPU 사용률:", "cpu_label", "%"),
            ("메모리 사용률:", "mem_label", "%"),
            ("디스크 읽기:", "disk_r_label", "MB/s"),
            ("디스크 쓰기:", "disk_w_label", "MB/s"),
            ("네트워크 송신:", "net_s_label", "MB/s"),
            ("네트워크 수신:", "net_r_label", "MB/s"),
            ("디스크 사용량:", "disk_u_label", "%"),
            ("메모리 사용:", "mem_used_label", "GB"),
        ]

        self.metric_labels = {}
        for i, (name, var, unit) in enumerate(metrics):
            row = i // 4
            col = (i % 4) * 2

            ttk.Label(dashboard_frame, text=name, font=("Arial", 10, "bold")).grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=5
            )

            label = ttk.Label(dashboard_frame, text=f"0.0 {unit}", font=("Arial", 11))
            label.grid(row=row, column=col + 1, sticky=tk.W, padx=5, pady=5)
            self.metric_labels[var] = (label, unit)

    def _create_graphs(self):
        """실시간 그래프 생성"""
        graph_frame = ttk.Frame(self.root)
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Matplotlib Figure (2x2 그리드)
        self.fig = Figure(figsize=(14, 7), dpi=100)
        self.fig.tight_layout(pad=3.0)

        # 4개의 서브플롯
        self.ax_cpu = self.fig.add_subplot(2, 2, 1)
        self.ax_mem = self.fig.add_subplot(2, 2, 2)
        self.ax_disk = self.fig.add_subplot(2, 2, 3)
        self.ax_net = self.fig.add_subplot(2, 2, 4)

        # 그래프 초기 설정
        self._init_graph(self.ax_cpu, "CPU 사용률 (%)", "red")
        self._init_graph(self.ax_mem, "메모리 사용률 (%)", "blue")
        self._init_graph(self.ax_disk, "디스크 I/O (MB/s)", "purple")
        self._init_graph(self.ax_net, "네트워크 트래픽 (MB/s)", "green")

        # Canvas에 Figure 임베드
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _init_graph(self, ax, title, color):
        """그래프 초기화"""
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlabel("시간", fontsize=8)
        ax.set_ylabel("값", fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', which='major', labelsize=7)

    def start_monitoring(self):
        """모니터링 시작"""
        self.monitor.start_monitoring()
        self.start_time = datetime.now()
        self.monitoring_seconds = 0

        # 버튼 상태 변경
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.pdf_btn.config(state=tk.DISABLED)

        self.status_label.config(text="모니터링 중...", foreground="green")

        # UI 업데이트 시작
        self.update_ui()

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitor.stop_monitoring()

        # UI 업데이트 중지
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None

        # 버튼 상태 변경
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.pdf_btn.config(state=tk.NORMAL)

        self.status_label.config(text="중지됨", foreground="orange")

        messagebox.showinfo("모니터링 중지", f"총 {self.monitor.get_sample_count()}개의 샘플이 수집되었습니다.")

    def update_ui(self):
        """UI 업데이트 (1초마다)"""
        if not self.monitor.is_monitoring():
            # 5분 경과 시 자동 중지
            if self.monitoring_seconds >= 300:
                self.stop_monitoring()
            return

        # 현재 상태 가져오기
        stats = self.monitor.get_current_stats()

        # 대시보드 업데이트
        if stats:
            self.metric_labels["cpu_label"][0].config(text=f"{stats.get('cpu_percent', 0):.1f} %")
            self.metric_labels["mem_label"][0].config(text=f"{stats.get('memory_percent', 0):.1f} %")
            self.metric_labels["disk_r_label"][0].config(text=f"{stats.get('disk_read', 0):.2f} MB/s")
            self.metric_labels["disk_w_label"][0].config(text=f"{stats.get('disk_write', 0):.2f} MB/s")
            self.metric_labels["net_s_label"][0].config(text=f"{stats.get('net_sent', 0):.2f} MB/s")
            self.metric_labels["net_r_label"][0].config(text=f"{stats.get('net_recv', 0):.2f} MB/s")
            self.metric_labels["disk_u_label"][0].config(text=f"{stats.get('disk_usage', 0):.1f} %")
            self.metric_labels["mem_used_label"][0].config(text=f"{stats.get('memory_used', 0):.2f} GB")

        # 타이머 업데이트
        self.monitoring_seconds = (datetime.now() - self.start_time).seconds if self.start_time else 0
        elapsed_min = self.monitoring_seconds // 60
        elapsed_sec = self.monitoring_seconds % 60
        self.timer_label.config(text=f"경과 시간: {elapsed_min:02d}:{elapsed_sec:02d} / 05:00")

        # 샘플 수 업데이트
        sample_count = self.monitor.get_sample_count()
        self.sample_label.config(text=f"수집 샘플: {sample_count} / 300")

        # 그래프 업데이트
        self.update_graphs()

        # 5분 경과 확인
        if self.monitoring_seconds >= 300:
            self.stop_monitoring()
            return

        # 다음 업데이트 예약
        self.update_job = self.root.after(self.update_interval, self.update_ui)

    def update_graphs(self):
        """그래프 업데이트"""
        if not self.monitor.timestamps:
            return

        timestamps = list(self.monitor.timestamps)

        # CPU 그래프
        self.ax_cpu.clear()
        self._init_graph(self.ax_cpu, "CPU 사용률 (%)", "red")
        if self.monitor.cpu_percent:
            self.ax_cpu.plot(timestamps, list(self.monitor.cpu_percent), color='red', linewidth=1.5)
            self.ax_cpu.fill_between(timestamps, list(self.monitor.cpu_percent), alpha=0.3, color='red')
            self.ax_cpu.set_ylim(0, 100)

        # 메모리 그래프
        self.ax_mem.clear()
        self._init_graph(self.ax_mem, "메모리 사용률 (%)", "blue")
        if self.monitor.memory_percent:
            self.ax_mem.plot(timestamps, list(self.monitor.memory_percent), color='blue', linewidth=1.5)
            self.ax_mem.fill_between(timestamps, list(self.monitor.memory_percent), alpha=0.3, color='blue')
            self.ax_mem.set_ylim(0, 100)

        # 디스크 I/O 그래프
        self.ax_disk.clear()
        self._init_graph(self.ax_disk, "디스크 I/O (MB/s)", "purple")
        if self.monitor.disk_read and self.monitor.disk_write:
            self.ax_disk.plot(timestamps, list(self.monitor.disk_read), color='purple', linewidth=1.5, label='읽기')
            self.ax_disk.plot(timestamps, list(self.monitor.disk_write), color='pink', linewidth=1.5, label='쓰기')
            self.ax_disk.legend(loc='upper left', fontsize=7)

        # 네트워크 트래픽 그래프
        self.ax_net.clear()
        self._init_graph(self.ax_net, "네트워크 트래픽 (MB/s)", "green")
        if self.monitor.net_sent and self.monitor.net_recv:
            self.ax_net.plot(timestamps, list(self.monitor.net_sent), color='green', linewidth=1.5, label='송신')
            self.ax_net.plot(timestamps, list(self.monitor.net_recv), color='orange', linewidth=1.5, label='수신')
            self.ax_net.legend(loc='upper left', fontsize=7)

        # X축 시간 포맷
        for ax in [self.ax_cpu, self.ax_mem, self.ax_disk, self.ax_net]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.tick_params(axis='x', rotation=45, labelsize=6)

        self.fig.tight_layout()
        self.canvas.draw()

    def generate_pdf(self):
        """PDF 보고서 생성"""
        if self.monitor.get_sample_count() == 0:
            messagebox.showwarning("경고", "수집된 데이터가 없습니다.")
            return

        try:
            self.status_label.config(text="PDF 생성 중...", foreground="blue")
            self.root.update()

            # PDF 생성기
            generator = PDFReportGenerator(self.monitor)
            filename = generator.generate_report()

            self.status_label.config(text="준비", foreground="blue")
            messagebox.showinfo("PDF 생성 완료", f"보고서가 생성되었습니다:\n{filename}")

        except Exception as e:
            self.status_label.config(text="오류", foreground="red")
            messagebox.showerror("오류", f"PDF 생성 중 오류 발생:\n{str(e)}")

    def run(self):
        """UI 실행"""
        self.root.mainloop()


def main():
    """메인 실행 함수"""
    root = tk.Tk()
    app = MonitorUI(root)
    app.run()


if __name__ == "__main__":
    main()

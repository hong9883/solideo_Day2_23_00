"""
System Resource Data Collector Module
Collects CPU, Memory, Disk I/O, and Network statistics
"""

import psutil
import platform
import time
from datetime import datetime
from collections import deque
from threading import Thread, Event
from typing import Dict, List, Optional


class SystemMonitor:
    """시스템 리소스를 모니터링하고 데이터를 수집하는 클래스"""

    def __init__(self, max_samples: int = 300):
        """
        Args:
            max_samples: 저장할 최대 샘플 수 (기본 300 = 5분 @ 1초 간격)
        """
        self.max_samples = max_samples

        # 데이터 저장용 deque (자동으로 오래된 데이터 제거)
        self.timestamps = deque(maxlen=max_samples)
        self.cpu_percent = deque(maxlen=max_samples)
        self.cpu_per_core = deque(maxlen=max_samples)
        self.memory_percent = deque(maxlen=max_samples)
        self.memory_used = deque(maxlen=max_samples)
        self.memory_available = deque(maxlen=max_samples)
        self.disk_read = deque(maxlen=max_samples)
        self.disk_write = deque(maxlen=max_samples)
        self.net_sent = deque(maxlen=max_samples)
        self.net_recv = deque(maxlen=max_samples)
        self.disk_usage = deque(maxlen=max_samples)

        # GPU 데이터 (사용 가능한 경우)
        self.gpu_usage = deque(maxlen=max_samples)
        self.gpu_temp = deque(maxlen=max_samples)
        self.gpu_available = False

        # 프로세스 Top 5 (주기적으로 업데이트)
        self.top_cpu_processes = []
        self.top_memory_processes = []

        # 스레드 제어
        self.monitoring = False
        self.stop_event = Event()
        self.monitor_thread: Optional[Thread] = None

        # 이전 네트워크/디스크 I/O 값 (속도 계산용)
        self.prev_net_io = None
        self.prev_disk_io = None
        self.prev_time = None

        # GPU 지원 확인
        self._check_gpu_support()

    def _check_gpu_support(self):
        """GPU 모니터링 지원 확인"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                self.gpu_available = True
                print(f"GPU 감지됨: {len(gpus)}개의 GPU 발견")
        except (ImportError, Exception) as e:
            print(f"GPU 모니터링 불가: {e}")
            self.gpu_available = False

    def get_system_info(self) -> Dict[str, str]:
        """시스템 기본 정보 반환"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                "OS": f"{platform.system()} {platform.release()}",
                "CPU 모델": platform.processor() or "Unknown",
                "CPU 코어": f"{psutil.cpu_count(logical=False)} 물리 / {psutil.cpu_count(logical=True)} 논리",
                "CPU 주파수": f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A",
                "총 메모리": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                "총 디스크": f"{psutil.disk_usage('/').total / (1024**3):.2f} GB"
            }
        except Exception as e:
            print(f"시스템 정보 수집 오류: {e}")
            return {}

    def collect_sample(self):
        """1초마다 호출되어 시스템 리소스 데이터를 수집"""
        try:
            current_time = time.time()

            # 타임스탬프
            self.timestamps.append(datetime.now())

            # CPU 사용률
            self.cpu_percent.append(psutil.cpu_percent(interval=0.1))
            self.cpu_per_core.append(psutil.cpu_percent(interval=0.1, percpu=True))

            # 메모리
            mem = psutil.virtual_memory()
            self.memory_percent.append(mem.percent)
            self.memory_used.append(mem.used / (1024**3))  # GB
            self.memory_available.append(mem.available / (1024**3))  # GB

            # 디스크 I/O (속도 계산)
            disk_io = psutil.disk_io_counters()
            if self.prev_disk_io and self.prev_time:
                time_delta = current_time - self.prev_time
                read_speed = (disk_io.read_bytes - self.prev_disk_io.read_bytes) / time_delta / (1024**2)  # MB/s
                write_speed = (disk_io.write_bytes - self.prev_disk_io.write_bytes) / time_delta / (1024**2)  # MB/s
                self.disk_read.append(max(0, read_speed))
                self.disk_write.append(max(0, write_speed))
            else:
                self.disk_read.append(0)
                self.disk_write.append(0)
            self.prev_disk_io = disk_io

            # 네트워크 트래픽 (속도 계산)
            net_io = psutil.net_io_counters()
            if self.prev_net_io and self.prev_time:
                time_delta = current_time - self.prev_time
                sent_speed = (net_io.bytes_sent - self.prev_net_io.bytes_sent) / time_delta / (1024**2)  # MB/s
                recv_speed = (net_io.bytes_recv - self.prev_net_io.bytes_recv) / time_delta / (1024**2)  # MB/s
                self.net_sent.append(max(0, sent_speed))
                self.net_recv.append(max(0, recv_speed))
            else:
                self.net_sent.append(0)
                self.net_recv.append(0)
            self.prev_net_io = net_io

            # 디스크 사용량
            disk_usage = psutil.disk_usage('/')
            self.disk_usage.append(disk_usage.percent)

            # GPU (사용 가능한 경우)
            if self.gpu_available:
                try:
                    import GPUtil
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]  # 첫 번째 GPU
                        self.gpu_usage.append(gpu.load * 100)
                        self.gpu_temp.append(gpu.temperature)
                    else:
                        self.gpu_usage.append(0)
                        self.gpu_temp.append(0)
                except Exception as e:
                    print(f"GPU 데이터 수집 오류: {e}")
                    self.gpu_usage.append(0)
                    self.gpu_temp.append(0)

            # 시간 업데이트
            self.prev_time = current_time

        except Exception as e:
            print(f"데이터 수집 오류: {e}")

    def collect_top_processes(self):
        """CPU 및 메모리 사용량 상위 5개 프로세스 수집"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # CPU 사용량 기준 정렬
            self.top_cpu_processes = sorted(
                processes,
                key=lambda x: x['cpu_percent'] or 0,
                reverse=True
            )[:5]

            # 메모리 사용량 기준 정렬
            self.top_memory_processes = sorted(
                processes,
                key=lambda x: x['memory_percent'] or 0,
                reverse=True
            )[:5]

        except Exception as e:
            print(f"프로세스 정보 수집 오류: {e}")

    def _monitor_loop(self):
        """모니터링 루프 (별도 스레드에서 실행)"""
        sample_count = 0
        while not self.stop_event.is_set() and sample_count < self.max_samples:
            self.collect_sample()

            # 10초마다 프로세스 정보 수집 (성능 고려)
            if sample_count % 10 == 0:
                self.collect_top_processes()

            sample_count += 1
            time.sleep(1)  # 1초 대기

        self.monitoring = False
        print(f"모니터링 완료: {sample_count}개 샘플 수집")

    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring:
            print("이미 모니터링 중입니다.")
            return

        self.monitoring = True
        self.stop_event.clear()

        # 초기값 설정
        self.prev_net_io = psutil.net_io_counters()
        self.prev_disk_io = psutil.disk_io_counters()
        self.prev_time = time.time()

        # 모니터링 스레드 시작
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("모니터링 시작됨")

    def stop_monitoring(self):
        """모니터링 중지"""
        if not self.monitoring:
            print("모니터링이 실행 중이 아닙니다.")
            return

        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.monitoring = False
        print("모니터링 중지됨")

    def get_current_stats(self) -> Dict[str, any]:
        """현재 시스템 상태 반환 (UI 표시용)"""
        if not self.timestamps:
            return {}

        stats = {
            "cpu_percent": self.cpu_percent[-1] if self.cpu_percent else 0,
            "memory_percent": self.memory_percent[-1] if self.memory_percent else 0,
            "memory_used": self.memory_used[-1] if self.memory_used else 0,
            "memory_available": self.memory_available[-1] if self.memory_available else 0,
            "disk_read": self.disk_read[-1] if self.disk_read else 0,
            "disk_write": self.disk_write[-1] if self.disk_write else 0,
            "net_sent": self.net_sent[-1] if self.net_sent else 0,
            "net_recv": self.net_recv[-1] if self.net_recv else 0,
            "disk_usage": self.disk_usage[-1] if self.disk_usage else 0,
        }

        if self.gpu_available and self.gpu_usage:
            stats["gpu_usage"] = self.gpu_usage[-1]
            stats["gpu_temp"] = self.gpu_temp[-1]

        return stats

    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """수집된 데이터의 통계 (평균, 최소, 최대) 반환"""
        def calc_stats(data):
            if not data:
                return {"avg": 0, "min": 0, "max": 0}
            return {
                "avg": sum(data) / len(data),
                "min": min(data),
                "max": max(data)
            }

        return {
            "CPU 사용률 (%)": calc_stats(self.cpu_percent),
            "메모리 사용률 (%)": calc_stats(self.memory_percent),
            "디스크 읽기 (MB/s)": calc_stats(self.disk_read),
            "디스크 쓰기 (MB/s)": calc_stats(self.disk_write),
            "네트워크 송신 (MB/s)": calc_stats(self.net_sent),
            "네트워크 수신 (MB/s)": calc_stats(self.net_recv),
            "디스크 사용량 (%)": calc_stats(self.disk_usage),
        }

    def is_monitoring(self) -> bool:
        """모니터링 중인지 확인"""
        return self.monitoring

    def get_sample_count(self) -> int:
        """수집된 샘플 수 반환"""
        return len(self.timestamps)

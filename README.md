# 시스템 리소스 실시간 모니터링 시스템

Python 기반의 실시간 시스템 리소스 모니터링 및 PDF 보고서 생성 도구

## 📋 기능

### 핵심 기능
- **실시간 모니터링**: 1초 간격으로 시스템 리소스 수집
- **시각화**: Matplotlib 기반 실시간 그래프 (CPU, 메모리, 디스크, 네트워크)
- **PDF 보고서**: 수집된 데이터를 분석하여 PDF 보고서 자동 생성
- **5분 자동 모니터링**: 최대 300개 데이터 포인트 수집

### 모니터링 항목
✅ **필수 항목**
- CPU 사용률 (전체 및 코어별)
- 메모리 사용률 (전체, 사용 가능, 사용 중)
- 디스크 I/O (읽기/쓰기 속도)
- 네트워크 트래픽 (송신/수신 속도)
- 디스크 사용량

⭐ **선택 항목** (환경에 따라)
- GPU 사용률 및 온도 (NVIDIA GPU)
- 프로세스별 리소스 사용 Top 5

## 🚀 설치 및 실행

### 1. 요구사항
- Python 3.7 이상
- pip (Python 패키지 관리자)

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 실행
```bash
python main.py
```

## 📊 사용 방법

### 기본 사용 흐름
1. **시작 버튼 클릭**: 모니터링 시작
2. **실시간 확인**: 그래프와 대시보드에서 실시간 데이터 확인
3. **자동/수동 중지**: 5분 경과 시 자동 중지 또는 중지 버튼 클릭
4. **PDF 생성**: "PDF 보고서 생성" 버튼으로 보고서 생성

### UI 구성
```
┌─────────────────────────────────────────────────────┐
│  [시작] [중지] [PDF생성]   경과시간: 00:00/05:00   │  컨트롤 패널
├─────────────────────────────────────────────────────┤
│  CPU: 45.2%    메모리: 62.1%    디스크R: 12.5MB/s  │
│  네트워크S: 0.5MB/s    네트워크R: 1.2MB/s          │  현재 상태
├─────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐                     │
│  │ CPU 그래프  │  │ 메모리 그래프│                    │
│  └────────────┘  └────────────┘                     │  실시간 그래프
│  ┌────────────┐  ┌────────────┐                     │
│  │ 디스크I/O   │  │ 네트워크    │                    │
│  └────────────┘  └────────────┘                     │
└─────────────────────────────────────────────────────┘
```

## 📄 PDF 보고서

### 생성되는 보고서 구조
1. **표지**
   - 제목 및 모니터링 기간
   - 시스템 정보 (OS, CPU, 메모리)

2. **요약 통계 표**
   - 각 메트릭별 평균/최소/최대값

3. **시계열 그래프**
   - CPU 사용률
   - 메모리 사용률
   - 네트워크 트래픽
   - 디스크 I/O

4. **프로세스 분석**
   - CPU 사용량 Top 5
   - 메모리 사용량 Top 5

### 파일명 형식
```
system_report_YYYYMMDD_HHMMSS.pdf
예: system_report_20240106_153042.pdf
```

## 🛠️ 기술 스택

### 핵심 라이브러리
- **psutil**: 시스템 리소스 정보 수집
- **tkinter**: GUI 프레임워크 (Python 내장)
- **matplotlib**: 그래프 시각화
- **reportlab**: PDF 문서 생성

### 선택 라이브러리
- **GPUtil**: NVIDIA GPU 모니터링
- **py3nvml**: GPU 온도 및 상세 정보

## 📁 프로젝트 구조

```
.
├── main.py                    # 메인 실행 파일
├── requirements.txt           # 의존성 목록
├── README.md                  # 프로젝트 문서
├── LICENSE.md                 # 라이센스
└── monitor/                   # 모니터링 패키지
    ├── __init__.py
    ├── data_collector.py      # 데이터 수집 모듈
    ├── ui.py                  # Tkinter UI 모듈
    └── pdf_generator.py       # PDF 생성 모듈
```

## 🔧 고급 설정

### 모니터링 시간 변경
`data_collector.py`에서 `max_samples` 파라미터 조정:
```python
monitor = SystemMonitor(max_samples=600)  # 10분 (600초)
```

### 업데이트 주기 변경
`ui.py`에서 `update_interval` 조정:
```python
self.update_interval = 2000  # 2초
```

### 한글 폰트 설정

✨ **자동 폰트 지원 (개선됨!)**

이 프로그램은 한글을 완벽하게 지원하며, 다음과 같은 방식으로 작동합니다:

1. **자동 폰트 감지**
   - Linux: NanumGothic, NanumBarunGothic (`/usr/share/fonts/truetype/nanum/`)
   - macOS: AppleSDGothicNeo, AppleGothic
   - Windows: 맑은 고딕, 굴림

2. **자동 폰트 다운로드**
   - 시스템에 한글 폰트가 없으면 자동으로 NanumGothic 폰트를 다운로드합니다
   - 다운로드 위치: `~/.fonts/NanumGothic.ttf`
   - 인터넷 연결이 필요합니다

3. **PDF 및 그래프 모두 한글 지원**
   - PDF 보고서의 모든 텍스트가 한글로 표시됩니다
   - Matplotlib 그래프 레이블도 한글로 표시됩니다

4. **UTF-8 인코딩**
   - 모든 소스 파일이 UTF-8로 인코딩되어 한글이 깨지지 않습니다

수동으로 폰트를 설정하려면 `pdf_generator.py`의 `font_paths` 리스트에 경로 추가:
```python
font_paths = [
    '/your/custom/font/path.ttf',
    ...
]
```

## ⚠️ 주의사항

### 권한
- 일부 시스템 정보는 관리자 권한이 필요할 수 있습니다
- 권한 부족 시 "N/A"로 표시되거나 해당 항목이 생략됩니다

### GPU 모니터링
- NVIDIA GPU가 있고 드라이버가 설치된 경우에만 작동
- GPU가 없으면 자동으로 비활성화됨

### 메모리 사용
- deque 자료구조로 메모리 overflow 방지
- 최대 300개 샘플만 메모리에 유지

## 🐛 문제 해결

### Tkinter 설치 오류 (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

### matplotlib 백엔드 오류
```python
# main.py 상단에 추가
import matplotlib
matplotlib.use('TkAgg')
```

### 한글 폰트 깨짐
```bash
# Ubuntu에서 NanumGothic 설치
sudo apt-get install fonts-nanum
```

## 📝 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다. 자세한 내용은 LICENSE.md를 참조하세요.

## 👥 기여

이슈 리포트, 기능 제안, Pull Request는 언제나 환영합니다!

## 📞 문의

문제가 발생하거나 질문이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ using Python**

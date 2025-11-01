# Seoul Open API Table Collector

이 저장소는 [서울 열린데이터 광장](https://data.seoul.go.kr/)의 Open API를 활용하여
표 형태로 제공되는 데이터를 손쉽게 수집하고, CSV 및 이미지로 내보내는 Python
스크립트를 제공합니다. 이미지 출력 기능을 이용하면 표 데이터를 그대로 캡처한
것과 같은 시각적 자료를 만들 수 있습니다.

## 필수 조건

- Python 3.9 이상
- `pip`가 설치되어 있어야 합니다.

## 설치 및 환경 구성

1. 저장소를 클론하거나 소스 코드를 다운로드합니다.
2. 가상 환경을 사용하는 것을 권장합니다.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
```

3. 필요한 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

## 사용 방법

스크립트는 `data_table_collector.py`로 제공되며, 아래와 같이 실행할 수 있습니다.

```bash
python data_table_collector.py <발급받은_API_KEY> \
    --service ListAirQualityByDistrictService \
    --start 1 \
    --end 100 \
    --csv output/air_quality.csv \
    --image output/air_quality.png \
    --title "자치구별 대기질 정보" \
    --max-rows 20
```

### 주요 인자 설명

- `api_key`: 서울 열린데이터 광장에서 발급받은 인증키입니다.
- `--service`: 호출할 API 서비스 이름입니다. 기본값은
  `ListAirQualityByDistrictService`로 자치구별 대기질 정보를 제공합니다. 다른
  서비스 이름은 [API 목록](https://data.seoul.go.kr/dataList/datasetList.do)에서 확인할 수
  있습니다.
- `--start`, `--end`: 조회할 데이터 범위를 나타내는 인덱스입니다. API 특성상
  양쪽 모두 포함(inclusive)되며, 너무 큰 범위를 한 번에 요청하면 오류가 발생할 수
  있습니다.
- `--csv`: CSV 파일 저장 경로입니다. 기본값은 `output/data.csv`입니다.
- `--image`: 표 이미지를 저장할 경로입니다. 기본값은 `output/data.png`입니다.
- `--title`: 이미지 상단에 표시할 제목입니다. 생략하면 제목이 표시되지 않습니다.
- `--max-rows`: 이미지에 표시할 최대 행 수입니다. 표가 너무 커지는 것을 방지하기
  위해 기본값은 15입니다. 전체 행을 출력하려면 `--max-rows`를 충분히 큰 값으로
  설정하세요.

### 동작 과정

1. `build_request_url` 함수가 API 호출 URL을 생성합니다.
2. `fetch_table` 함수가 데이터를 요청하여 JSON으로 응답을 받은 후,
   `pandas.DataFrame`으로 변환합니다.
3. `save_csv` 함수가 DataFrame을 CSV 파일로 저장합니다.
4. `render_table_image` 함수가 `matplotlib`를 이용해 표 이미지를 생성합니다.

### 한글 폰트 설정

- 스크립트는 시스템에 **맑은 고딕(Malgun Gothic)** 폰트가 설치되어 있으면 자동으로
  사용합니다. Windows에서는 기본 제공되지만, macOS나 Linux에서는 별도로 설치해야
  합니다.
- 폰트가 없으면 일반 산세리프 폰트로 대체되므로 한글이 깨지지는 않지만, 화면상
  가독성이 떨어질 수 있습니다.
- Linux에서 폰트를 설치했다면 다음과 같이 `matplotlib` 폰트 캐시를 삭제하여
  변경 사항을 반영하세요.

  ```bash
  rm -rf ~/.cache/matplotlib
  ```

  이후 스크립트를 다시 실행하면 새로 설치한 폰트가 적용됩니다.

### 참고 사항

- API 호출 시 인증키가 올바르지 않거나 사용량 제한을 초과한 경우 오류가 발생할
  수 있습니다. 오류 메시지를 확인하여 조치하세요.
- 이미지 렌더링은 기본적으로 앞쪽 일부 행만 표시하도록 되어 있습니다. 전체 데이터
  시각화가 필요한 경우 `--max-rows` 값을 조정하거나 CSV 데이터를 사용해 다른
  시각화 도구를 활용하세요.

## 개발 및 확장 아이디어

- 스케줄러(Cron, Airflow 등)와 연동하여 주기적으로 데이터를 수집하도록 확장할 수
  있습니다.
- 여러 서비스를 동시에 호출하여 하나의 통합 보고서를 만드는 기능을 추가할 수
  있습니다.
- SVG 등 고해상도 벡터 포맷으로의 출력 기능도 손쉽게 추가할 수 있습니다.

## 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.

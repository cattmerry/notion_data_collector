# Notion Data Collector
***
노션 페이지 블록내의 데이터베이스 오브젝트들을 가져와 pandas dataframe으로 리턴해주는 패키지입니다.

***
## Requirements
* 환경 : 파이썬 3.10 버전 사용
* 노션 통합 api키가 필요합니다.
  * https://developers.notion.com/docs/getting-started#step-1-create-an-integration
* 가져올 페이지의 share 목록에 api 통합 앱을 추가해야 합니다.
***
## 사용 방법
1. 데이터를 가져올 노션 페이지의 url과 api키를 준비합니다.
2. notion_data_collector.py의 NotionData 클래스에 api키와 페이지 url을 파라메터로 넣어 객체를 만듭니다.
3. 객체의 execute 함수를 call하면 페이지내(하위 페이지 포함)의 모든 데이터베이스 오브젝트들을 pandas dataframe으로 변환하여 제너레이터로 리턴해줍니다.
4. 새로운 페이지의 데이터를 추출하고 싶다면 객체를 새로 생성해야 합니다.
***
## Directory 구조
```
├── config                      config 모음 디렉토리 
│   └── notion_api_config.py    노션 api 메타정보 
├── utils                       메인 기능을 위한 utility 모듈 디렉토리
│   ├── logger.py               본 프로젝트 로깅을 위한 모듈
│   ├── notion_client.py        Notion api 클라이언트 모듈
│   └── notion_data_parser.py   notion data를 파싱하기 위한 모듈
├── notion_data_collector.py    메인 기능을 수행할 모듈
├── test_notion_data.py         간단한 테스트 예제
└── requirements.txt            필요한 파이썬 라이브러리 정의
```
***
## Example
필요 라이브러리를 설치합니다.  
```
pip install -r requirements.txt
```
모듈을 불러옵니다.  
```
from notion_data_collector import NotionData
```
api키와 페이지 url을 파라메터로 넣어 객체를 생성합니다.
```
notiondata = NotionData(
    auth_token=AUTH_TOKEN, # 통합 api key
    url="https://www.notion.so/test-49455890dcd84f038c415a866f71174b" # 노션 페이지 url
)
```
execute함수를 call하여 제너레이터를 생성합니다.
```
df_data = notiondata.execute()
```
반복문을 통해 데이터를 확인합니다.
```
for data in df_data:
    print(data)
```

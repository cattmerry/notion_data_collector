import requests
from config.notion_api_config import NotionApi
from utils.logger import logger_setting


class NotionClient:

    def __init__(self,
                 auth_token: str,
                 notion_version: str = "2022-02-22"):
        """
        Notion api 클라이언트
        :param auth_token: api 키
        :param notion_version: notion 버전
        """
        self._api_url = "https://api.notion.com"
        self._header = {
            "Accept": "application/json",
            "Notion-Version": notion_version,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        self._config = NotionApi
        self._logging = logger_setting("INFO")
        self._response = None

    def _call(self,
              method: str,
              endpoint: str,
              payload: dict,
              depth: int = 1) -> dict:
        """
        실제로 API Call을 수행하기 위한 Request 요청에 대한 험수
        next cursor가 존재시 재귀 실행하여 response의 results에 추가한다. next cursor가 없을때까지 반복 실행.
        API call 실패 시 Exception을 반환한다.
        database query api에서 404 status 리턴시 예외처리
        :param method: request method
        :param endpoint: 엔드포인트
        :param payload: 페이로드 혹은 파라메터
        :param depth: 재귀 뎁스, 최초 실행을 감지하기 위해 사용
        :return: response 객체
        """
        if method == "GET":
            response = requests.request(method, endpoint, params=payload, headers=self._header)
        elif method == "POST":
            response = requests.request(method, endpoint, json=payload, headers=self._header)
        else:
            raise Exception("정의되지 않은 메서드")

        self._logging.info(
            f"Request URL Information {'=' * 100}\n"
            f"Endpoint   == {endpoint}\n"
            f"payload     == {payload}\n"
            f"{'=' * 159}"
        )

        if response.status_code == 404:
            if endpoint.split("/")[-1] == "query":
                self._logging.info(
                    f"Notion API call failed: {response.text}\n"
                    "이 데이터베이스는 지정 페이지에 속하지 않은 데이터베이스이면서 view로 지정된 데이터베이스입니다.\n"
                    "이 데이터베이스의 로드를 넘깁니다."
                )
                raise Exception(response.text, "pass")
            raise Exception(f"Notion API call failed: {response.text}")
        if response.status_code != 200:
            raise Exception(f"Notion API call failed: {response.text}")

        if depth == 1:  # 최초 실행인 경우
            self._response = response.json()
        next_cursor = response.json().get("next_cursor")
        if next_cursor is not None:
            self._logging.info(f"{depth}번째 cursor ::{next_cursor}")
            if depth != 1:  # 최초 실행이 아닐 경우
                self._response["results"].append(response.json()["results"])
            payload["start_cursor"] = next_cursor
            self._call(
                method=method,
                endpoint=endpoint,
                payload=payload,
                depth=depth+1
            )
        else:
            return self._response

    def call_search(self,
                    url: str) -> dict:
        """
        notion search api call 하기 위한 함수
        https://developers.notion.com/reference/post-search
        :param url: notion 페이지 url
        :return: 딕셔너리 결과
        """
        self._response = None
        payload = self._config.Search.payload
        payload["query"] = url
        endpoint = self._api_url + self._config.Search.endpoint
        response = self._call(
            method=self._config.Search.method,
            endpoint=endpoint,
            payload=payload
        )

        return response

    def call_block_children(self,
                            block_id: str) -> dict:
        """
        notion Retrieve block children api call 하기 위한 함수
        https://developers.notion.com/reference/get-block-children
        :param block_id: block id, 페이지 id
        :return: 딕셔너리 결과
        """
        self._response = None
        endpoint = self._api_url + self._config.Block.RetrieveBlockChildren.endpoint.format(block_id=block_id)
        response = self._call(
            method=self._config.Block.RetrieveBlockChildren.method,
            endpoint=endpoint,
            payload=self._config.Block.RetrieveBlockChildren.payload
        )

        return response

    def call_query_database(self,
                            database_id: str) -> dict:
        """
        notion Query a database api call 하기 위한 함수
        https://developers.notion.com/reference/post-database-query
        :param database_id: databse id
        :return: 딕셔너리 결과
        """
        self._response = None
        endpoint = self._api_url + self._config.Database.Query.endpoint.format(database_id=database_id)

        response = self._call(
                method=self._config.Database.Query.method,
                endpoint=endpoint,
                payload=self._config.Database.Query.payload
            )

        return response

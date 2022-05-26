import pandas as pd
from utils.notion_client import NotionClient
from utils.logger import logger_setting
from utils.notion_data_parser import NotionDataParser
from typing import List


class NotionData:

    def __init__(self,
                 auth_token: str,
                 url: str):
        """
        api 키와 특정 노션 페이지의 url을 받아 페이지내의 모든 데이터베이스 오브젝트를 pandas dataframe으로 리턴하기 위한 클래스
        사용자의 공유스페이스 통합 api 키를 사용해야함
        참고사항
        -다른 블록(페이지)의 데이터베이스 오브젝트를 가져오고 싶다면 해당 페이지의 url을 넣어 새로운 객체를 생성할 것
        -본 클래스를 객체화하여 사용하는 도중 데이터베이스의 추가나 업데이트가 있을 경우 _init_data 함수를 한번 실행하고 사용할 것
        :param auth_token: 사용자의 공유스페이스 통합 api 키
        :param url: 데이터베이스를 추출할 노션 페이지 url
        """
        self._client = NotionClient(auth_token=auth_token)
        self._db_id_list = list()
        self._logging = logger_setting("INFO")
        self._url = url
        self._init_data()

    def _init_data(self):
        """
        데이터베이스 추출을 위한 데이터 세팅, 클래스 객체화하면 실행
        """
        page_id = self._extract_page_id()
        self._extract_db_id(page_id=page_id)

    def _extract_page_id(self) -> str:
        """
        url의 페이지 id를 추출한다.
        :return: 추출한 페이지 id
        """
        response = self._client.call_search(url=self._url)
        results = response["results"][0]
        if results["object"] != "page":
            raise Exception("페이지 url이 아닙니다.")
        return response["results"][0]["id"]

    def _extract_db_id(self,
                       page_id: str) -> List[str]:
        """
        페이지내의 모든 데이터베이스 오브젝트의 id를 추출한다.
        하위 페이지까지 탐색을 위해 재귀 실행
        :param page_id: 페이지 id
        :return: 추출된 데이터베이스 id 리스트
        """
        response = self._client.call_block_children(block_id=page_id)
        results = response["results"]

        for data in results:
            if data["type"] == "child_database":
                self._db_id_list.append(data["id"])
            if data["type"] == "child_page":
                self._extract_db_id(page_id=data["id"])

        return self._db_id_list

    def _extract_db_to_dataframe(self,
                                 database_id: str) -> pd.DataFrame | str:
        """
        데이터베이스 id를 받아 데이터를 추출하고 pandas dataframe으로 변환하여 리턴한다.
        예외사항
        -데이터베이스가 지정 페이지에 속하지 않은 데이터베이스이면서 view로 지정된 데이터베이스라면 해당 데이터베이스 id로 쿼리할 수 없음
          -원본 데이터베이스 id와 view로 지정된 데이터베이스 id가 다름. 노션측의 에러로 보여짐.
        -이 경우 해당 데이터베이스의 정보를 exception 정보로 채우고 다음 데이터베이스 로드로 넘어간다.
        :param database_id: 데이터베이스 id
        :return: 변환된 dataframe or exception 메세지
        """
        try:
            response = self._client.call_query_database(database_id=database_id)
        except Exception as e:
            if e.args[1] == "pass":
                return e.args[0]
            raise
        self._logging.info(
            f"database id :: {database_id}\n"
            f"response :: {response}"
        )
        result = NotionDataParser.parse_database(table_data=response["results"])
        return result

    def execute(self) -> pd.DataFrame | str:
        """
        사용자가 사용하는 실행함수
        변환된 dataframe의 제너레이터를 리턴한다.
        예외사항
        -데이터베이스가 지정 페이지에 속하지 않은 데이터베이스이면서 view로 지정된 데이터베이스라면 해당 데이터베이스 id로 쿼리할 수 없음
          -원본 데이터베이스 id와 view로 지정된 데이터베이스 id가 다름. 노션측의 에러로 보여짐.
        -이 경우 해당 데이터베이스의 정보를 exception 정보로 채우고 다음 데이터베이스 로드로 넘어간다.
        :return: 변환된 dataframe or exception 메세지
        """
        for data in self._db_id_list:
            yield self._extract_db_to_dataframe(database_id=data)

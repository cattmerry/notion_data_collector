import pandas as pd
from typing import List


class NotionDataParser:
    """
    notion data를 파싱하기 위한 클래스
    현재 database 오브젝트에 대한 파싱 함수만 구현되어있음
    추후 필요에 따라 파싱해야할 오브젝트가 늘어나면 함수 추가 예정
    """

    @staticmethod
    def parse_database(table_data: List[dict]) -> pd.DataFrame:
        """
        database api response 데이터를 받아 pandas dataframe으로 변환하여 리턴한다.
        database 컬럼들의 타입에 따라 분기 처리
        추후 notion api의 업데이트 혹은 예상치 못한 타입이 추가될 경우를 대비하여 정의되지 않은 타입이 들어올 경우 파싱하지 않고 원본 그대로 입력한다.
        :param table_data: database api response data
        :return: 변환된 dataframe
        """
        parse_list = list()
        for table_raw in table_data:

            parse_dict = dict()
            for raw_key, raw_value in table_raw["properties"].items():
                raw_type: str = raw_value["type"]
                raw_data: dict | list | str = raw_value[raw_type]

                if isinstance(raw_data, list):
                    if len(raw_data) == 0:
                        parse_dict[raw_key] = None
                        continue
                else:
                    if raw_data is None:
                        parse_dict[raw_key] = None
                        continue

                match raw_type:

                    case "select" | "created_by" | "last_edited_by":
                        parse_dict[raw_key] = raw_data["name"]

                    case "email" | "url" | "checkbox" | "number" | "phone_number" | "created_time" | "last_edited_time":
                        parse_dict[raw_key] = raw_data

                    case "multi_select" | "people":
                        temp_list = []
                        for data in raw_data:
                            temp_list.append(data["name"])
                        parse_dict[raw_key] = ",".join(temp_list)

                    case "title" | "rich_text":
                        parse_dict[raw_key] = raw_data[0]["plain_text"]

                    case "formula":
                        parse_dict[raw_key] = raw_data[raw_data['type']]

                    case "relation":
                        temp_list = []
                        for data in raw_data:
                            temp_list.append(data["id"])
                        parse_dict[raw_key] = ",".join(temp_list)

                    case "rollup":
                        temp_list = []
                        for data in raw_data["array"]:
                            rollup_type = data["type"]
                            rollup_data = data[rollup_type]
                            temp_list.append(rollup_data[0]["plain_text"])
                        parse_dict[raw_key] = ",".join(temp_list)

                    case "files":
                        temp_list = []
                        for data in raw_data:
                            temp_list.append(data[f"{data['type']}"]["url"])
                        parse_dict[raw_key] = ",".join(temp_list)

                    case "date":
                        for k, v in raw_data.items():
                            parse_dict[raw_key + "_" + k] = v

                    case _:
                        parse_dict[raw_key] = raw_value

            parse_list.append(parse_dict)

        return pd.DataFrame(parse_list)

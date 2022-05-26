class NotionApi:
    """
    notion api 메타정보 클래스
    사용할 api가 늘어날때마다 추가한다.
    """
    class Search:
        """
        https://developers.notion.com/reference/post-search
        """
        method: str = "POST"
        endpoint: str = "/v1/search"
        payload: dir = {
            'page_size': 100
        }

    class Database:
        """
        https://developers.notion.com/reference/database
        """
        class Query:
            """
            https://developers.notion.com/reference/post-database-query
            """
            method: str = "POST"
            endpoint: str = "/v1/databases/{database_id}/query"
            payload: dir = {
                'page_size': 100
            }

    class Block:
        """
        https://developers.notion.com/reference/block
        """
        class RetrieveBlockChildren:
            """
            https://developers.notion.com/reference/get-block-children
            """
            method: str = "GET"
            endpoint: str = "/v1/blocks/{block_id}/children"
            payload: dir = {
                'page_size': 100
            }

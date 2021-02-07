from ruotvet.http import AIOHTTPClient
from ruotvet.types import Question, Attachment
from typing import List, Optional


class YandexQ:
    def __init__(self):
        self.client = AIOHTTPClient()

    async def get_answers(self, query: str, count: int = 1) -> List[Optional[Question]]:
        output = []
        try:
            response = await self.client.request_json("GET", "https://yandex.ru/znatoki/web-api/aggregate/page/"
                                                             "qSearchRoute", params={"eventName": "qSearchRoute",
                                                                                     "exp_flags": "new_quality",
                                                                                     "text": query})
            for result in response["result"]["questions"]["items"][:count]:
                response = await self.client.request_json("GET", "https://yandex.ru/znatoki/web-api/aggregate/page/"
                                                                 "qQuestionRoute", params={"eventName": "qQuestionRoute",
                                                                                           "exp_flags": "new_quality",
                                                                                           "id": result["id"]})
                if "answer" in response["entities"]:
                    for answer in response["entities"]["answer"]:
                        answer = response["entities"]["answer"][answer]
                        attachment = [Attachment(url=answer["formattedText"].split("src=")[1].split(" srcset=")[0])]\
                            if "src" in answer["formattedText"] else None
                        output.append(Question(url=f"https://yandex.com/q/question/{answer['questionId']}/",
                                               question=response["entities"]["question"][answer["questionId"]]["title"],
                                               answer=answer["plainText"], attachments=attachment))
                        break
            return output
        finally:
            await self.client.close()
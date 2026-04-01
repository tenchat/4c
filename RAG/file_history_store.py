"""
[已弃用] LangChain 兼容的聊天历史存储

请使用 services.chat.history_service.HistoryService 替代。
此文件保留用于兼容旧代码。
"""

from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import  RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
import json, os
from langchain_core.messages import message_to_dict, messages_from_dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from typing import Sequence


class FileChatMessageHistory(BaseChatMessageHistory):


    def __init__(self, session_id: str, storage_path: str ):
        self.storage_path = storage_path
        self.session_id = session_id
        self.file_path = os.path.join(self.storage_path, self.session_id)

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(
                os.path.join(self.storage_path, self.session_id),
                "r",
                encoding="utf-8",
            ) as f:
                messages_data = json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)  # Existing messages
        all_messages.extend(messages)  # Add new messages

        serialized = [message_to_dict(message) for message in all_messages]
        file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f)

    def clear(self) -> None:
        file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)




def get_history(session_id):
    return FileChatMessageHistory(session_id,"./chat_history")


# # 创建一个新链，对原有链增强功能：自动附加历史消息
# conversation_chian = RunnableWithMessageHistory(
#     base_chain,     # 被增强的原有chain
#     get_history,    # 通过会话id获取InMemoryChatMessageHistory类对象
#     input_messages_key="input",           # 表示用户输入在模板中的占位符
#     history_messages_key="chat_history"   # 表示历史信息在模板中的占位符
# )



























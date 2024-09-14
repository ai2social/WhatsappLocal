from typing import Literal


class ChatMessage:
    def __init__(self, who: Literal['ai', 'human'], content: str):
        self.who = who
        self.content = content

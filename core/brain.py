import re
import ollama

from config import MODEL, SYSTEM_PROMPT
from core.web_search import LenoWebSearch
from core.tools import LenoTools


class LenoBrain:
    def __init__(self):
        self.conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        self.current_guest_name = None
        self.guest_name_requested = False

        self.web = LenoWebSearch()
        self.tools = LenoTools(self.web)

    def detect_tool(self, message):
        text = message.lower().strip()

        # ACTIONS
        action_phrases = [
            "send a message",
            "send message",
            "send a text",
            "send text",
            "message my friend",
            "text my friend",
            "send my location",
            "share my location",
            "send location",
            "share location",
            "whatsapp",
            "call my friend",
            "call my mom",
            "call my dad",
            "call someone",
            "set an alarm",
            "set a reminder",
            "turn on",
            "turn off",
            "open chrome",
            "open browser"
        ]

        if any(phrase in text for phrase in action_phrases):
            return "action", message

        # CALCULATOR
        math_phrases = [
            "multiplied by",
            "times",
            "plus",
            "minus",
            "divided by",
            "divide by",
            "modulo",
            "mod",
            "squared",
            "cubed"
        ]

        if (
            any(phrase in text for phrase in math_phrases)
            and re.search(r"\d", text)
        ):
            expression = text

            replacements = [
                ("multiplied by", "*"),
                ("divided by", "/"),
                ("divide by", "/"),
                ("times", "*"),
                ("plus", "+"),
                ("minus", "-"),
                ("modulo", "%"),
                ("mod", "%")
            ]

            for word, symbol in replacements:
                expression = re.sub(
                    rf"\b{re.escape(word)}\b",
                    symbol,
                    expression,
                    flags=re.IGNORECASE
                )

            expression = re.sub(
                r"\b(what is|what's|how much is|calculate|please|can you tell me)\b",
                "",
                expression,
                flags=re.IGNORECASE
            )

            return "calculator", expression.strip()

        if re.fullmatch(
            r"[\d\s+\-*/%().^]+",
            text
        ):
            return "calculator", text.replace("^", "**")

        # TIME / DATE
        time_phrases = [
            "what time is it",
            "what's the time",
            "what is the time",
            "current time",
            "time now",
            "tell me the time",
            "what date is it",
            "today's date",
            "current date",
            "what day is it"
        ]

        if any(phrase in text for phrase in time_phrases):
            return "time", ""

        # WEB SEARCH
        web_phrases = [
            "latest",
            "recent",
            "breaking news",
            "news",
            "today",
            "yesterday",
            "tomorrow",
            "right now",
            "this week",
            "this month",
            "this year",
            "current",
            "current news",
            "current information",
            "current status",
            "current price",
            "stock price",
            "weather",
            "update",
            "updates",
            "who is the",
            "who is currently",
            "who is the current",
            "chief minister",
            "prime minister",
            "president of",
            "speaker of",
            "minister of",
            "government of",
            "election",
            "elections",
            "politics",
            "political",
            "latest information",
            "2026"
        ]

        if any(phrase in text for phrase in web_phrases):
            return "web_search", message

        return None, None

    def think(
        self,
        user_message,
        person_name=None,
        is_boss=False,
        vision_context=""
    ):
        if is_boss:
            self.current_guest_name = None
            self.guest_name_requested = False

            identity = (
                "The person speaking is the owner. "
                "You may naturally call them Boss."
            )

        elif person_name:
            self.current_guest_name = person_name

            identity = (
                f"The person speaking is {person_name}. "
                "Address them naturally by their name when appropriate."
            )

        else:
            identity = (
                "The person speaking is an unidentified guest. "
                "Never call them Boss."
            )

        tool_name, tool_argument = self.detect_tool(
            user_message
        )

        tool_context = ""

        if tool_name:
            print(
                f"\n🧰 LENO tool selected: {tool_name}"
            )

            tool_result = self.tools.execute(
                tool_name,
                tool_argument
            )

            tool_context = (
                "\n\nTOOL RESULT:\n"
                + str(tool_result)
                + "\n\n"
                "Use the tool result accurately. "
                "Do not claim an action was completed "
                "unless the tool confirms completion."
            )

        context = (
            "CURRENT PERSON:\n"
            + identity
            + "\n\nVISUAL CONTEXT:\n"
            + (
                vision_context
                if vision_context
                else "No visual information available."
            )
            + tool_context
            + "\n\nUSER MESSAGE:\n"
            + user_message
        )

        self.conversation.append(
            {
                "role": "user",
                "content": context
            }
        )

        response = ollama.chat(
            model=MODEL,
            messages=self.conversation
        )

        answer = response["message"]["content"].strip()

        if not is_boss and not self.current_guest_name:
            name = self.extract_name(user_message)

            if name:
                self.current_guest_name = name
                self.guest_name_requested = True

        self.conversation.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    def extract_name(self, text):
        patterns = [
            r"\bmy name is ([A-Za-z][A-Za-z'-]{1,30})\b",
            r"\bi am ([A-Za-z][A-Za-z'-]{1,30})\b",
            r"\bi'm ([A-Za-z][A-Za-z'-]{1,30})\b",
            r"\bcall me ([A-Za-z][A-Za-z'-]{1,30})\b"
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(1).strip().title()

        return None

    def get_guest_name(self):
        return self.current_guest_name

    def reset_conversation(self):
        self.conversation = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        self.current_guest_name = None
        self.guest_name_requested = False

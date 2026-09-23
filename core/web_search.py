from ddgs import DDGS


class LenoWebSearch:
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query, max_results=5):
        try:
            results = self.ddgs.text(
                query,
                max_results=max_results
            )

            if not results:
                return "No useful web results were found."

            formatted = []

            for index, result in enumerate(results, start=1):
                title = result.get("title", "")
                body = result.get("body", "")
                href = result.get("href", "")

                formatted.append(
                    f"{index}. {title}\n"
                    f"Summary: {body}\n"
                    f"Source: {href}"
                )

            return "\n\n".join(formatted)

        except Exception as error:
            print(f"❌ Web search error: {error}")
            return "Web search is currently unavailable."

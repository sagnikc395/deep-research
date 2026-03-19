from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Digits
from research.coordinator import run_deep_research


# class ClockApp(App):
#     CSS = """
#     Screen {align: center middle;}
#     Digits {width: auto;}
# """

#     def compose(self) -> ComposeResult:
#         yield Digits("")

#     def on_ready(self):
#         self.update_clock()
#         self.set_interval(1, self.update_clock)

#     def update_clock(self):
#         clock = datetime.now().time()
#         self.query_one(Digits).update(f"{clock:%T}")


def main():
    print("Hello from deep-research!")
    # app = ClockApp()
    # app.run()
    load_dotenv()
    query = input("Enter your research query:")
    result = run_deep_research(query=query)
    with open("results.md", "w") as f:
        f.write(result)
    print("Research result saved to research_result.md")


if __name__ == "__main__":
    main()

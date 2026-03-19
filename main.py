from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Digits


class ClockApp(App):
    CSS = """
    Screen {align: center middle;}
    Digits {width: auto;}
"""

    def compose(self) -> ComposeResult:
        yield Digits("")

    def on_ready(self):
        self.update_clock()
        self.set_interval(1, self.update_clock)

    def update_clock(self):
        clock = datetime.now().time()
        self.query_one(Digits).update(f"{clock:%T}")


def main():
    print("Hello from deep-research!")
    app = ClockApp()
    app.run()


if __name__ == "__main__":
    main()

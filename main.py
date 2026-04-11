from dotenv import load_dotenv

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, Footer, Input, RichLog, Static

from research.coordinator import run_deep_research

load_dotenv()


class DeepResearchApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #banner {
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        background: $surface;
    }

    #query-bar {
        height: 3;
        dock: bottom;
        padding: 0 1;
    }

    #query-input {
        width: 1fr;
    }

    #log {
        height: 1fr;
        border: round $primary;
        padding: 0 1;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("research v0.2", id="banner")
        yield RichLog(highlight=True, markup=True, id="log")
        yield Horizontal(
            Input(
                placeholder="Enter your research query and press Enter...",
                id="query-input",
            ),
            id="query-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#query-input", Input).focus()
        self.log_widget = self.query_one("#log", RichLog)
        self.log_widget.write("[bold]Welcome to deep-research![/bold]")
        self.log_widget.write("Type your research query below and press Enter.\n")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return

        event.input.value = ""
        event.input.disabled = True

        self.log_widget.write(f"\n[bold cyan]Query:[/bold cyan] {query}")
        self.log_widget.write("[dim]Starting research...[/dim]\n")

        self.run_worker(lambda: self._do_research(query), name="research", thread=True)

    def _log(self, message: str) -> None:
        self.call_from_thread(self.log_widget.write, message)

    def _do_research(self, query: str) -> None:
        """Sync worker — runs in a plain OS thread (no event loop)."""
        try:
            result = run_deep_research(query=query, log=self._log)

            with open("results.md", "w") as f:
                f.write(result)

            self.call_from_thread(
                self.log_widget.write,
                "\n[bold green]Research complete! Saved to results.md[/bold green]",
            )
        except Exception as e:
            self.call_from_thread(
                self.log_widget.write,
                f"\n[bold red]Error: {e}[/bold red]",
            )
        finally:
            input_widget = self.query_one("#query-input", Input)
            self.call_from_thread(setattr, input_widget, "disabled", False)
            self.call_from_thread(input_widget.focus)


def main():
    app = DeepResearchApp()
    app.run()


if __name__ == "__main__":
    main()

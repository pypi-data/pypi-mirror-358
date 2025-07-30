import argparse
import os
from datetime import date
from decimal import Decimal

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.events import Key
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
)

from moomoolah.state import (
    EntryType,
    FinancialEntry,
    FinancialState,
    Recurrence,
    RecurrenceType,
)
from moomoolah.widgets import ConfirmationModal


class EntryTypeModal(ModalScreen[EntryType]):
    """Modal to choose between adding an expense or income."""

    BINDINGS = [("escape", "app.pop_screen", "Cancel")]
    CSS = """
    EntryTypeModal {
      align: center middle;
    }

    EntryTypeModal Container {
      width: 50;
      height: 10;
      outline: solid $primary;
      padding: 2;
    }
    EntryTypeModal Horizontal {
        margin-top: 1;
        align: center middle;
    }
    EntryTypeModal Button {
        margin-right: 2;
    }
    """

    def compose(self) -> ComposeResult:
        from textual.containers import Container, Horizontal

        with Container():
            yield Label("What would you like to add?")
            with Horizontal():
                yield Button("Expense", id="add_expense", variant="error")
                yield Button("Income", id="add_income", variant="success")

    @on(Button.Pressed, "#add_expense")
    def on_add_expense(self) -> None:
        self.dismiss(EntryType.EXPENSE)

    @on(Button.Pressed, "#add_income")
    def on_add_income(self) -> None:
        self.dismiss(EntryType.INCOME)

    def on_key(self, event: Key) -> None:
        if event.key == "left":
            self.focus_previous()
            event.prevent_default()
        elif event.key == "right":
            self.focus_next()
            event.prevent_default()


class UpdateEntryModal(ModalScreen):
    SUB_TITLE = "Update entry"
    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def __init__(
        self, entry: FinancialEntry, modal_title="Update Entry", *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.entry = entry
        self.modal_title = modal_title

    def compose(self) -> ComposeResult:
        yield Label("", classes="modal-title-before")
        yield Label(self.modal_title, classes="modal-title")
        with Grid(id="update-entry-form"):
            yield Label("Description:")
            yield Input(value=self.entry.description, id="entry_description")

            yield Label("Amount:")
            yield Input(value=str(self.entry.amount), id="entry_amount")

            yield Label("Category:")
            yield Input(value=str(self.entry.category), id="entry_category")

            yield Label("Recurrence:")
            with RadioSet(id="entry_recurrence"):
                for rt in RecurrenceType:
                    yield RadioButton(
                        rt.name,
                        value=rt == self.entry.recurrence.type,
                    )

            yield Label("Start date:")
            yield Input(
                value=str(self.entry.recurrence.start_date), id="entry_start_date"
            )

            # TODO: only show this if recurrence is MONTHLY
            yield Label("Every X months?")
            yield Input(value=str(self.entry.recurrence.every), id="entry_every")

            yield Label("End Date:")
            end_date_value = (
                str(self.entry.recurrence.end_date)
                if self.entry.recurrence.end_date
                else ""
            )
            yield Input(value=end_date_value, id="end_date")

            yield Button("Save", id="entry_save", variant="primary")
            yield Button("Cancel", id="entry_cancel")

    def _get_values(self):
        def get_date_or_none(value):
            return date.fromisoformat(value) if value else None

        return {
            "description": self.query_one("#entry_description", Input).value,
            "amount": Decimal(self.query_one("#entry_amount", Input).value),
            "category": self.query_one("#entry_category", Input).value,
            "recurrence_type": RecurrenceType[
                str(
                    self.query_one("#entry_recurrence", RadioSet).pressed_button.label
                ).upper()
            ],
            "start_date": date.fromisoformat(
                self.query_one("#entry_start_date", Input).value
            ),
            "every": int(self.query_one("#entry_every", Input).value),
            "end_date": get_date_or_none(self.query_one("#end_date", Input).value),
        }

    @on(Button.Pressed, "#entry_save")
    def on_save(self, _) -> None:
        values = self._get_values()
        entry = FinancialEntry(
            description=values["description"],
            amount=values["amount"],
            category=values["category"],
            type=self.entry.type,
            recurrence=Recurrence(
                type=values["recurrence_type"],
                start_date=values["start_date"],
                every=values["every"],
            ),
        )
        self.dismiss(entry)

    @on(Button.Pressed, "#entry_cancel")
    def on_cancel(self, _) -> None:
        self.dismiss(None)

    def on_key(self, event: Key) -> None:
        """Handle key events, specifically ENTER to save."""
        if event.key == "enter":
            # Only handle ENTER if the focused widget is not a button
            # This prevents double-triggering when the Save button has focus
            focused_widget = self.app.focused
            if focused_widget and focused_widget.id != "entry_save":
                event.prevent_default()
                event.stop()
                self.on_save(None)


class ManageEntriesScreen(Screen[list[FinancialEntry]]):
    BINDINGS = [
        ("backspace", "back", "Back"),
        ("escape", "back", "Back"),
        ("insert", "add_entry", "Add Entry"),
        ("delete", "delete_entry", "Delete Entry"),
    ]

    def __init__(
        self, entry_type: EntryType, entries: list[FinancialEntry], *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.sub_title: str = (
            "Managing Expenses"
            if entry_type == EntryType.EXPENSE
            else "Managing Income"
        )
        self.entry_type = entry_type
        self.entries = entries

    def action_back(self) -> None:
        self.dismiss(self.entries)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        yield Label(self.sub_title, classes=f"entries-label-{self.entry_type}")
        yield DataTable(id="entries_table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#entries_table", DataTable)
        table.add_columns("Description", "Amount", "Recurrence", "Category")
        self._sync_table()

    def _sync_table(self) -> None:
        table = self.query_one("#entries_table", DataTable)
        self._sync_table_entries(table, self.entries)

    def _sync_table_entries(
        self, table: DataTable, entries: list[FinancialEntry]
    ) -> None:
        table.clear()

        if not entries:
            table.add_row(Text("No entries yet", style="italic"))
            return

        for entry in entries:
            table.add_row(
                entry.description,
                Text(f"€{entry.amount}", style="bold", justify="right"),
                entry.recurrence.description,
                entry.category,
            )

    @work
    async def action_add_entry(self) -> None:
        modal_title = (
            "Add Expense" if self.entry_type == EntryType.EXPENSE else "Add Income"
        )
        screen = UpdateEntryModal(FinancialEntry(type=self.entry_type), modal_title)
        result = await self.app.push_screen_wait(screen)
        if result:
            self.entries.append(result)
            self.app.mark_unsaved_changes()
            self._sync_table()
            if self.entry_type == EntryType.EXPENSE:
                self.notify(
                    f"Added expense {result.description}", title="Expense added"
                )
            else:
                self.notify(f"Added income {result.description}", title="Income added")

    @work
    async def action_delete_entry(self) -> None:
        if not self.entries:
            return

        table = self.query_one("#entries_table", DataTable)
        entry = self.entries[table.cursor_row]
        screen = ConfirmationModal(
            f"Are you sure you want to delete '{entry.description}'?"
        )
        result = await self.app.push_screen_wait(screen)
        if result:
            self.entries.pop(table.cursor_row)
            self.app.mark_unsaved_changes()
            self._sync_table()
            self.notify("Entry deleted", title="Entry deleted")

    @work
    @on(DataTable.RowSelected, "#entries_table")
    async def on_row_selected(self, event: DataTable.RowSelected) -> None:
        # Guard against empty entries list (when only placeholder row exists)
        if not self.entries:
            return

        entry = self.entries[event.cursor_row]
        new_entry = await self.app.push_screen_wait(
            UpdateEntryModal(entry, f"Update {self.entry_type} Entry")
        )
        if new_entry:
            self.entries[event.cursor_row] = new_entry
            self.app.mark_unsaved_changes()
            self._sync_table()
            self.notify(
                f"Updated entry '{new_entry.description}'", title="Entry updated"
            )


class MainScreen(Screen):
    def __init__(self, state: FinancialState, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = state

    BINDINGS = [
        ("e", "manage_expenses", "Manage Expenses"),
        ("i", "manage_income", "Manage Income"),
        ("insert", "add_entry", "Add Entry"),
    ]

    @work
    async def action_manage_expenses(self) -> None:
        screen = ManageEntriesScreen(EntryType.EXPENSE, self.state.expense_entries)
        await self.app.push_screen_wait(screen)
        self._sync_table()

    @work
    async def action_manage_income(self) -> None:
        screen = ManageEntriesScreen(EntryType.INCOME, self.state.income_entries)
        await self.app.push_screen_wait(screen)
        self._sync_table()

    @work
    async def action_add_entry(self) -> None:
        """Show modal to choose entry type, then add the entry."""
        # First, ask user what type of entry they want to add
        entry_type = await self.app.push_screen_wait(EntryTypeModal())
        if entry_type is None:
            return  # User cancelled

        # Show the appropriate entry modal
        modal_title = "Add Expense" if entry_type == EntryType.EXPENSE else "Add Income"
        new_entry = await self.app.push_screen_wait(
            UpdateEntryModal(FinancialEntry(type=entry_type), modal_title)
        )

        if new_entry:
            # Add entry to the appropriate list
            if entry_type == EntryType.EXPENSE:
                self.state.expense_entries.append(new_entry)
                self.notify(
                    f"Added expense {new_entry.description}", title="Expense added"
                )
            else:
                self.state.income_entries.append(new_entry)
                self.notify(
                    f"Added income {new_entry.description}", title="Income added"
                )

            # Mark changes as unsaved
            self.app.mark_unsaved_changes()

            # Refresh the forecast table
            self._sync_table()

    def compose(self) -> ComposeResult:
        # TODO: if state has no entries, invite user to create a new one
        # TODO: if state has entries, display the forecast for the next months,
        #       with option to manage entries
        yield Header()
        yield Label("FORECAST FOR NEXT 12 MONTHS", classes="forecast-title")
        yield DataTable(id="forecast_table", cursor_type="none")
        yield Label("PREVIOUS 3 MONTHS", classes="history-title")
        yield DataTable(id="history_table", cursor_type="none")
        yield Footer()

    def on_mount(self) -> None:
        forecast_table = self.query_one("#forecast_table", DataTable)
        forecast_table.add_columns("Month", "Expenses", "Income", "Balance")

        history_table = self.query_one("#history_table", DataTable)
        history_table.add_columns("Month", "Expenses", "Income", "Balance")

        self._sync_table()

    def _sync_table(self) -> None:
        # Update forecast table
        forecast_table = self.query_one("#forecast_table", DataTable)
        forecast_table.clear()
        for month, forecast in self.state.get_forecast_for_next_n_months(12).items():
            balance_style = (
                "red bold" if forecast.balance < Decimal("0") else "blue bold"
            )
            forecast_table.add_row(
                month.strftime("%B %Y"),
                Text(f"€{forecast.total_expenses}", style="bold", justify="right"),
                Text(f"€{forecast.total_income}", style="bold", justify="right"),
                Text(f"€{forecast.balance}", style=balance_style, justify="right"),
            )

        # Update history table
        history_table = self.query_one("#history_table", DataTable)
        history_table.clear()
        # Get history in reverse chronological order (most recent first)
        history_data = list(self.state.get_forecast_for_previous_n_months(3).items())
        history_data.reverse()

        for month, forecast in history_data:
            balance_style = (
                "red bold" if forecast.balance < Decimal("0") else "blue bold"
            )
            history_table.add_row(
                month.strftime("%B %Y"),
                Text(f"€{forecast.total_expenses}", style="bold", justify="right"),
                Text(f"€{forecast.total_income}", style="bold", justify="right"),
                Text(f"€{forecast.balance}", style=balance_style, justify="right"),
            )


class BudgetApp(App):
    TITLE = "MooMoolah - Personal Budget Planner"
    CSS_PATH = "style.css"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "save_state", "Save"),
    ]

    def __init__(self, state_file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if os.path.exists(state_file):
            self.state = FinancialState.from_json_file(state_file)
        else:
            # if file doesn't exist, create a new one
            self.state = FinancialState()
            self.state.to_json_file(state_file)
            self.notify(
                f"Created file {os.path.basename(state_file)}",
                title="Initialized state",
            )

        self.state_file = state_file
        self.has_unsaved_changes = False

    def mark_unsaved_changes(self) -> None:
        """Mark that there are unsaved changes and update the title."""
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self._update_title()

    def mark_changes_saved(self) -> None:
        """Mark that changes have been saved and update the title."""
        if self.has_unsaved_changes:
            self.has_unsaved_changes = False
            self._update_title()

    def _update_title(self) -> None:
        """Update the app title to show unsaved changes indicator."""
        base_title = "MooMoolah - Personal Budget Planner"
        if self.has_unsaved_changes:
            self.title = f"{base_title} *"
        else:
            self.title = base_title

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Loading...")
        yield Footer()

    def on_mount(self) -> None:
        self.push_screen(MainScreen(self.state))

    def action_save_state(self) -> None:
        # TODO: ask user where to save, if no state file was given
        self.state.to_json_file(self.state_file)
        self.mark_changes_saved()
        self.notify(
            f"Written file {os.path.basename(self.state_file)}", title="Saved state"
        )

    @work
    async def action_quit(self) -> None:
        """Override quit action to check for unsaved changes."""
        if self.has_unsaved_changes:
            screen = ConfirmationModal(
                "You have unsaved changes. Are you sure you want to quit?"
            )
            result = await self.push_screen_wait(screen)
            if result:
                self.exit()
        else:
            self.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "state_file", help="Financial state to load and/or save to", type=str
    )
    args = parser.parse_args()

    app = BudgetApp(state_file=args.state_file)
    app.run()

from argparse import ArgumentParser
from dataclasses import dataclass
from sys import stderr, stdout

from commons import TaskStatus
from tracker import Tracker


@dataclass
class CommandInterface:
    """
    CommandInterface class provides a command-line interface for managing tasks.

    Attributes:
        parser (ArgumentParser): The argument parser for handling command-line arguments.
        tracker (Tracker): The task tracker for managing task operations.

    Methods:
        add_argument(): Configures the command-line arguments for task operations.
        execute(): Executes the appropriate task operation based on the parsed arguments.
    """
    parser: ArgumentParser
    tracker: Tracker

    def __post_init__(self):
        self.add_argument()

    def add_argument(self):
        subparsers = self.parser.add_subparsers(dest="action")
        add_parser = subparsers.add_parser("add", help="Add a new task.")
        add_parser.add_argument(
            "description",
            help="Task description",
            type=str
        )
        update_parser = subparsers.add_parser("update", help="Update a task description.")
        update_parser.add_argument(
            "task_id",
            help="Task ID",
            type=int
        )
        update_parser.add_argument(
            "description",
            help="New task description",
            type=str
        )
        delete_parser = subparsers.add_parser("delete", help="Delete a task.")
        delete_parser.add_argument(
            "task_id",
            help="Task ID",
            type=int,
        )
        list_parser = subparsers.add_parser("list", help="List tasks.")
        list_parser.add_argument(
            "status",
            help="Task status (todo, in-progress, done)",
            type=str,
            choices=[TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value, TaskStatus.DONE.value],
            nargs="?"
        )
        mark_in_progress_parser = subparsers.add_parser("mark-in-progress", help="Mark a task as in-progress.")
        mark_in_progress_parser.add_argument(
            "task_id",
            help="Task ID",
            type=int,
        )
        mark_done_parser = subparsers.add_parser("mark-done", help="Mark a task as done.")
        mark_done_parser.add_argument(
            "task_id",
            help="Task ID",
            type=int
        )

    async def execute(self):
        args = self.parser.parse_args()

        match args.action:
            case "add":
                task = await self.tracker.add_task(args.description)
                stdout.write(f"Task added successfully (ID: {task.id}).\n")
            case "update":
                try:
                    task = await self.tracker.update_task(args.task_id, args.description)
                    stdout.write(f"Task (ID: {task.id}) updated successfully.\n")
                except ValueError:
                    stderr.write(f"Task (ID: {args.task_id}) not found.\n")
            case "delete":
                try:
                    task = await self.tracker.delete_task(args.task_id)
                    stdout.write(f"Task (ID: {task.id}) deleted successfully.\n")
                except ValueError:
                    stderr.write(f"Task (ID: {args.task_id}) not found.\n")
            case "list":
                tasks = await self.tracker.list_tasks(args.status)
                if not tasks:
                    stderr.write("No tasks found.\n")
                    return
                display_tasks = [task.display_details() for task in tasks]
                stdout.writelines(display_tasks)
            case "mark-in-progress":
                try:
                    task = await self.tracker.mark_in_progress(args.task_id)
                    stdout.write(f"Task (ID: {task.id}) marked as in-progress successfully.\n")
                except ValueError:
                    stderr.write(f"Task (ID: {args.task_id}) not found.\n")
            case "mark-done":
                try:
                    task = await self.tracker.mark_done(args.task_id)
                    stdout.write(f"Task (ID: {task.id}) marked as done successfully.\n")
                except ValueError:
                    stderr.write(f"Task (ID: {args.task_id}) not found.\n")
            case _:
                self.parser.print_help()
                exit(1)

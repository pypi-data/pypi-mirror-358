# Falyx CLI Framework — (c) 2025 rtj.dev LLC — MIT Licensed
"""save_file_action.py"""
from pathlib import Path

from rich.tree import Tree

from falyx.action.action_types import FileType
from falyx.action.base_action import BaseAction


class SaveFileAction(BaseAction):
    """ """

    def __init__(
        self,
        name: str,
        file_path: str,
        input_type: str | FileType = "text",
        output_type: str | FileType = "text",
    ):
        """
        SaveFileAction allows saving data to a file.

        Args:
            name (str): Name of the action.
            file_path (str | Path): Path to the file where data will be saved.
            input_type (str | FileType): Type of data being saved (default is "text").
            output_type (str | FileType): Type of data to save to the file (default is "text").
        """
        super().__init__(name=name)
        self.file_path = file_path

    def get_infer_target(self) -> tuple[None, None]:
        return None, None

    async def _run(self, *args, **kwargs):
        raise NotImplementedError(
            "SaveFileAction is not finished yet... Use primitives instead..."
        )

    async def preview(self, parent: Tree | None = None): ...

    def __str__(self) -> str:
        return f"SaveFileAction(file_path={self.file_path})"

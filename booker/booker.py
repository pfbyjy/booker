from pathlib import Path

from booker.database import DBHandler


class Booker:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DBHandler(db_path)
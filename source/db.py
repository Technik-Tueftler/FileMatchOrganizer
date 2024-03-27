from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, select

engine = create_engine("sqlite:///sample.db", echo=False)
session = Session(bind=engine)

class Base(DeclarativeBase):
    pass


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    pattern: Mapped[str] = mapped_column(nullable=False)
    root_path: Mapped[str] = mapped_column(nullable=False)
    match_path: Mapped[str] = mapped_column(nullable=False)
    match_file: Mapped[str] = mapped_column(nullable=False)


    def __repr__(self) -> str:
        return f"<Match Pattern: {self.pattern}>"

Base.metadata.create_all(bind=engine)

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.engine import Base


class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    stars = Column(Integer)
    size = Column(Integer)
    lang = Column(String)
    owner = Column(String)
    # functions = relationship("Function", back_populates="repo", cascade="all, delete, delete-orphan")

    # Meta & stats
    type = Column(String, nullable=True, default=None)
    desc = Column(String, nullable=True, default=None)
    path = Column(String, nullable=True, default=None)
    readme = Column(String, nullable=True, default=None)
    # TODO: Downloaded at


# class File?


class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    names = Column(String)
    repo_id = Column(Integer, ForeignKey("repos.id"))
    file_name = Column(String)
    lang = Column(String)
    order = Column(Integer)
    grammar = Column(String)

    # median similarity
    # mean similarity

    # median body length
    # num body duplicates
    # num single letters
    # casing style?
    # num abbreviations?
    # num dictionary words
    # median levenshtein_distance
    # body term entropy
    # body context coverage
    # get all functions/files (contexts) in which specific word occurs
    # and calculate similarity of those contexts

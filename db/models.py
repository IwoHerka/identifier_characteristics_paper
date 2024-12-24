from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
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
    type = Column(String, nullable=True, default=None)
    desc = Column(String, nullable=True, default=None)
    path = Column(String, nullable=True, default=None)
    readme = Column(String, nullable=True, default=None)

    @staticmethod
    def all(session):
        return session.query(Repo).all()


class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    names = Column(String)
    repo_id = Column(Integer, ForeignKey("repos.id"))
    file_name = Column(String)
    lang = Column(String)
    order = Column(Integer)

    metrics = Column(String, nullable=True, default=None)

    grammar                       = Column(String, nullable=True)
    median_id_semantic_similarity = Column(Float, nullable=True)
    median_id_length              = Column(Float, nullable=True)
    median_id_syllable_count      = Column(Float, nullable=True) 
    median_id_soft_word_count     = Column(Float, nullable=True)
    id_duplicate_percentage       = Column(Float, nullable=True)
    num_single_letter_ids         = Column(Float, nullable=True)
    id_most_common_casing_style   = Column(String, nullable=True)
    id_percent_abbreviations      = Column(Float, nullable=True)
    id_percent_dictionary_words   = Column(Float, nullable=True)
    median_id_lv_dist             = Column(Float, nullable=True)
    num_consistency_violations    = Column(Float, nullable=True)
    num_conciseness_violations    = Column(Float, nullable=True)

    term_entropy = Column(Float, nullable=True)
    # context_coverage = Column(Float, nullable=True)
    # word_concreteness = Column(Float, nullable=True)
    # external_similarity = Column(Float, nullable=True)
    # grammatical_pattern = Column(String, nullable=True)
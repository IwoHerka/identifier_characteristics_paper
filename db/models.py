import random
from collections import defaultdict

from sqlalchemy import (Boolean, Column, Float, ForeignKey, Integer, String,
                        func)
from sqlalchemy.orm import relationship

from db.engine import Base


class ARTRun(Base):
    __tablename__ = "art_runs"

    id = Column(Integer, primary_key=True)

    langs = Column(String)
    domains = Column(String)
    metric = Column(String)
    max_samples = Column(Integer)

    lang_fval = Column(Float)
    lang_p = Column(Float)
    lang_df = Column(Float)

    domain_fval = Column(Float)
    domain_p = Column(Float)
    domain_df = Column(Float)

    interact_fval = Column(Float)
    interact_p = Column(Float)
    interact_df = Column(Float)

    @staticmethod
    def all(session, **kwargs):
        query = session.query(ARTRun)
        for key, value in kwargs.items():
            if hasattr(ARTRun, key):
                query = query.filter(getattr(ARTRun, key) == value)
        return query.all()


class ANOVARun(Base):
    __tablename__ = "anova_runs"

    id = Column(Integer, primary_key=True)
    langs = Column(String)
    domains = Column(String)
    metric = Column(String)
    max_samples = Column(Integer)
    typ = Column(Integer)

    lang_fval = Column(Float)
    lang_p = Column(Float)
    lang_df = Column(Float)
    lang_es = Column(Float)

    domain_fval = Column(Float)
    domain_p = Column(Float)
    domain_df = Column(Float)
    domain_es = Column(Float)

    interact_fval = Column(Float)
    interact_p = Column(Float)
    interact_df = Column(Float)
    interact_es = Column(Float)

    @staticmethod
    def all(session, **kwargs):
        query = session.query(ANOVARun)
        for key, value in kwargs.items():
            if hasattr(ANOVARun, key):
                query = query.filter(getattr(ANOVARun, key) == value)
        return query.all()


class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    stars = Column(Integer)
    size = Column(Integer)
    lang = Column(String)
    owner = Column(String)
    selected = Column(Boolean, default=False)
    domain = Column(String, nullable=True, default=None)
    path = Column(String, nullable=True, default=None)
    readme = Column(String, nullable=True, default=None)
    comment = Column(String, nullable=True, default=None)
    about = Column(String, nullable=True, default=None)

    @staticmethod
    def all(session, **kwargs):
        query = session.query(Repo)
        for key, value in kwargs.items():
            if hasattr(Repo, key):
                query = query.filter(getattr(Repo, key) == value)
        return query.all()

    @staticmethod
    def get_function_grammars(session):
        return (
            session.query(Function.grammar).filter(Function.grammar.isnot(None)).all()
        )

    @staticmethod
    def get_without_functions(session, lang):
        return (
            session.query(Repo)
            .filter(Repo.lang == lang)
            .outerjoin(Function, Repo.id == Function.repo_id)
            .group_by(Repo.id)
            .having(func.count(Function.id).between(0, 10))
            .all()
        )


class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    names = Column(String)
    repo_id = Column(Integer, ForeignKey("repos.id"))
    file_name = Column(String)
    lang = Column(String)
    order = Column(Integer)
    domain = Column(String)
    selected = Column(Boolean, default=False)
    metrics = Column(String, nullable=True, default=None)

    grammar = Column(String, nullable=True)
    grammar_hash = Column(Integer, nullable=True)
    median_id_semantic_similarity = Column(Float, nullable=True)
    median_id_length = Column(Float, nullable=True)
    median_id_syllable_count = Column(Float, nullable=True)
    median_id_soft_word_count = Column(Float, nullable=True)
    id_duplicate_percentage = Column(Float, nullable=True)
    num_single_letter_ids = Column(Float, nullable=True)
    id_most_common_casing_style = Column(String, nullable=True)
    id_percent_abbreviations = Column(Float, nullable=True)
    id_percent_dictionary_words = Column(Float, nullable=True)
    median_id_lv_dist = Column(Float, nullable=True)
    num_consistency_violations = Column(Float, nullable=True)
    num_conciseness_violations = Column(Float, nullable=True)
    median_word_concreteness = Column(Float, nullable=True)
    median_external_similarity = Column(Float, nullable=True)
    term_entropy = Column(Float, nullable=True)
    context_coverage = Column(Float, nullable=True)

    @staticmethod
    def get_all_names(session):
        return (
            session.query(Function.names)
            .filter(Function.domain.isnot(None))
            .filter(Function.domain != "")
            .all()
        )

    @staticmethod
    def filter_by(session, **kwargs):
        query = session.query(Function)
        for key, value in kwargs.items():
            if hasattr(Function, key):
                query = query.filter(getattr(Function, key) == value)
        return query.all()

    @staticmethod
    def get_metrics(session, limit, metric):
        query = session.query(Function)
        query = query.filter(getattr(Function, metric).isnot(None))
        query = query.limit(limit)
        query = query.with_entities(getattr(Function, metric))
        return query.all()

    @staticmethod
    def get_metrics_with_labels(session, langs, limit, metric, domains):
        results = []

        for lang in langs:
            query = session.query(Function)
            query = query.filter(getattr(Function, metric).isnot(None))
            query = query.filter(Function.domain.in_(domains))
            query = query.filter(Function.lang == lang)
            query = query.limit(limit * 4)
            query = query.with_entities(
                getattr(Function, metric), Function.lang, Function.domain
            )
            values = query.all()
            random.shuffle(values)
            results.extend(values[:limit])

        return results

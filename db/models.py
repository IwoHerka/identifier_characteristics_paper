import random

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy import func
from db.engine import Base
from collections import defaultdict


class ARTRun(Base):
    __tablename__ = "art_runs"

    id = Column(Integer, primary_key=True)
    langs = Column(String)
    domains = Column(String)
    metric = Column(String)
    lang_fval = Column(Float)
    domain_fval = Column(Float)
    paradigm_fval = Column(Float)
    interact_fval = Column(Float)


class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    stars = Column(Integer)
    size = Column(Integer)
    lang = Column(String)
    owner = Column(String)
    selected = Column(Boolean, default=False)
    type = Column(String, nullable=True, default=None)
    ntype = Column(String, nullable=True, default=None)
    desc = Column(String, nullable=True, default=None)
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
        return session.query(Function.grammar).filter(Function.grammar.isnot(None)).all()

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

    @staticmethod
    def select(session):
        repos = (
            session.query(Repo)
            .join(Function, Repo.id == Function.repo_id)
            .group_by(Repo.id)
            .filter(Repo.type.notin_(["WEB"]))
            .having(func.count(Function.id).between(500, 2000))
            .all()
        )
        lang_repos = {}
        print(len(repos))

        for repo in repos:
            if repo.lang not in lang_repos:
                lang_repos[repo.lang] = []
            lang_repos[repo.lang].append(repo)

        for lang, repos in lang_repos.items():
            selected_repos = random.sample(repos, min(len(repos), 100))
            print(f"Selected {len(selected_repos)} repos for {lang}")
        #     for repo in selected_repos:
        #         print(repo.name)
        #         repo.selected = True

        # session.commit()
        # session.close()

    @staticmethod
    def print_breakdown(session):
        repos = (
            session.query(Repo.lang, Repo.type, func.count(Function.id).label('function_count'))
            .join(Function, Repo.id == Function.repo_id)
            .group_by(Repo.lang, Repo.type, Repo.id)
            .filter(Repo.type.in_(["WEB", "CLI", "DB", "BUILD", "OTHER", "ML"]))
            .having(func.count(Function.id).between(250, 2000))
            .all()
        )

        lang_type_counts = defaultdict(lambda: defaultdict(int))

        for repo in repos:
            lang_type_counts[repo.lang][repo.type] += 1

        for lang, types in lang_type_counts.items():
            print(f"Language: {lang}")
            for typ, count in types.items():
                print(f"  Type: {typ}, Count: {count}")


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
    median_word_concreteness      = Column(Float, nullable=True)
    median_external_similarity    = Column(Float, nullable=True)

    term_entropy = Column(Float, nullable=True)
    context_coverage = Column(Float, nullable=True)
    # word_concreteness = Column(Float, nullable=True)
    # external_similarity = Column(Float, nullable=True)
    # grammatical_pattern = Column(String, nullable=True)

    @staticmethod
    def get_all_names(session):
        return (
            session.query(Function.names)
                   .filter(Function.domain.isnot(None))
                   .filter(Function.domain != '')
                   .all()
        )

    @staticmethod
    def get_grammars_for_lang(lang, session, limit=100000):
        return session.query(Function.grammar) \
                      .filter(Function.grammar.isnot(None)) \
                      .filter(Function.lang == lang) \
                      .limit(limit) \
                      .all()

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
            query = query.limit(limit*4)
            query = query.with_entities(getattr(Function, metric), Function.lang, Function.domain)
            values = query.all()
            random.shuffle(values)
            results.extend(values[:limit])

        return results
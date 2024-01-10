import json
from collections import defaultdict
import casestyle
import random

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy import func, asc

from db.engine import engine, Base
from db.models import Repo, Function

session = None


def commit():
    session.commit()


def init_session():
    global session
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


def init_local_session():
    return sessionmaker(bind=engine)()


def get_repo(repo_id):
    return session.query(Repo).filter_by(id=repo_id).first()


def add_repo(id, name, stars, size, lang, owner):
    new_repo = Repo(id=id, name=name, stars=stars, size=size, lang=lang, owner=owner)

    try:
        session.add(new_repo)
        session.commit()
    except IntegrityError:
        print(f"IntegrityError for {id}, {owner}/{name}, skipping")
        session.rollback()


def get_repos():
    return session.query(Repo)


def update_repo(repo, path, readme):  # , files, loc, readme):
    repo.path = path
    repo.readme = readme
    session.commit()


def get_functions_for_repo(repo_id, session):
    return session.query(Function).filter_by(repo_id=repo_id).all()


def get_distinct_function_names_without_grammar():
    names_by_lang = (
        session.query(Function.name)
        .filter(Function.selected == True)
        .filter((Function.grammar == None) | (Function.grammar == ""))
        .distinct()
        .all()
    )
    return names_by_lang


def update_function_grammar(session, name, new_grammar):
    session.query(Function).filter(Function.name == name).update(
        {"grammar": new_grammar}
    )


def add_function(session, name, names, repo_id, file_name, lang, order):
    new_fn = Function(
        name=name,
        names=names,
        repo_id=repo_id,
        file_name=file_name,
        lang=lang,
        order=order,
    )

    try:
        session.add(new_fn)
        session.commit()
    except IntegrityError:
        print(f"IntegrityError")
        session.rollback()
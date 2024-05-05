from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from db.engine import engine, Base
from db.models import Repo, Function

session = None


def init_session():
    global session
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


def new_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


def add_repo(id, name, stars, size, lang, owner):
    new_repo = Repo(id=id, name=name, stars=stars, size=size, lang=lang, owner=owner)

    try:
        session.add(new_repo)
        session.commit()
    except IntegrityError:
        print(f'IntegrityError for {id}, {owner}/{name}, skipping')
        session.rollback()


def get_repos(lang=None):
    if lang:
        return session.query(Repo).filter(Repo.lang==lang)
    else:
        return session.query(Repo).all()


def get_repos_with_no_functions(lang):
    repos_with_no_functions = session.query(Repo).\
        filter(Repo.lang==lang).\
        outerjoin(Function, Repo.id == Function.repo_id).\
        filter(Function.id == None).\
        all()

    return repos_with_no_functions


def update_repo(repo, path, readme):#, files, loc, readme):
    repo.path = path
    repo.readme = readme
    session.commit()


def get_functions():
    return session.query(Function).all()


def get_grammar_by_name(name):
    return session.query(Function).filter(Function.name == name, Function.grammar.isnot(None)).first()


def get_unique_function_names():
    # Query to select distinct names from the Function table
    names = session.query(Function.name).distinct().all()
    
    # Convert list of tuples to a set of names
    unique_names = {name[0] for name in names}

    return unique_names


def update_function_grammar(name, new_grammar):
    session.query(Function).filter(Function.name == name).update({'grammar': new_grammar})
    session.commit()


def add_function(session, name, names, repo_id, file_name, lang, order):
    new_fn = Function(
        name=name,
        names=names,
        repo_id=repo_id,
        file_name=file_name,
        lang=lang,
        order=order
    )

    try:
        session.add(new_fn)
        session.commit()
    except IntegrityError:
        print(f'IntegrityError')
        session.rollback()

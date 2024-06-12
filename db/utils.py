from collections import defaultdict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy import func, asc

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


def get_lang_to_repo_ids_map():
    lang_to_repo_ids = defaultdict(list)
    results = session.query(Repo.lang, Repo.id).all()

    for lang, repo_id in results:
        lang_to_repo_ids[lang].append(repo_id)

    return lang_to_repo_ids


def select_functions_for_grammar():
    pass


def update_repo(repo, path, readme):#, files, loc, readme):
    repo.path = path
    repo.readme = readme
    session.commit()


def get_functions():
    return session.query(Function).all()


def get_distinct_function_for_project():
    # Query to select distinct names from the Function table
    names = session.query(Function.name).filter(
    ).distinct().all()
    
    # Convert list of tuples to a set of names
    unique_names = [name[0] for name in names]

    return unique_names


def get_ordered_function_names(repo_id):
    """
    Given a repo_id, return an ordered corpus of names from all project functions,
    ordered by file and order within file.
    """
    functions = session.query(Function) \
        .filter_by(repo_id=repo_id) \
        .order_by(asc(Function.file_name), asc(Function.order)) \
        .all()
    
    names = [f.names for f in functions]
    return " ".join(names)


def get_grammar_by_name(name):
    return session.query(Function).filter(Function.name == name, Function.grammar.isnot(None)).first()


def get_distinct_function_names_without_grammar():
    # Query to select distinct names from the Function table
    names = session.query(Function.name).filter(
        (Function.grammar == None) | (Function.grammar == "")
    ).distinct().all()
    
    # Convert list of tuples to a set of names
    unique_names = [name[0] for name in names]

    return unique_names


def update_function_grammar(session, name, new_grammar):
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


def get_top_function_names():
    # Step A: Identify 500 repos with the largest number of related functions
    # We need a subquery to count functions per repo
    subquery = session.query(
        Function.repo_id,
        func.count('*').label('func_count')
    ).group_by(Function.repo_id).subquery()

    # Now, find the top 500 repos based on function count
    top_repos = session.query(
        subquery.c.repo_id
    ).order_by(subquery.c.func_count.desc()).limit(500)

    # Step B: For each of these repos, fetch 200 function names
    # We will use the `in_` operator to filter on the repo IDs obtained above
    functions = session.query(Function.name).filter(
        Function.repo_id.in_(top_repos)
    ).limit(200 * 500)  # Fetch up to 100,000 function names (200 per repo)

    # Fetch the results and extract function names
    function_names = [func.name for func in functions]

    return function_names

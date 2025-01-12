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
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def new_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


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


def get_repos_by_lang(lang):
    types = ["WEB", "DB", "CLI", "BUILD", "OTHER", "ML"]
    repos_by_type = {typ: session.query(Repo).filter(Repo.lang == lang, Repo.type == typ).all() for typ in types}

    min_count = min(len(repos) for repos in repos_by_type.values())
    
    balanced_repos = []
    for typ in types:
        balanced_repos.extend(repos_by_type[typ][:min_count + 10])
   
    for typ in types:
        print(f"{typ}: {len(repos_by_type[typ][:min_count + 10])} repos")
    return balanced_repos


def get_repos_by_type(lang, typ):
    return session.query(Repo).filter(Repo.lang == lang, Repo.type == typ).all()


def get_lang_to_repo_ids_map():
    lang_to_repo_ids = defaultdict(list)
    results = session.query(Repo.lang, Repo.id).all()

    for lang, repo_id in results:
        lang_to_repo_ids[lang].append(repo_id)

    return lang_to_repo_ids


def select_functions_for_grammar():
    pass


def update_repo(repo, path, readme):  # , files, loc, readme):
    repo.path = path
    repo.readme = readme
    session.commit()


def classify_repo(repo, typ):
    repo.type = typ
    session.commit()


def get_functions():
    return session.query(Function).all()


def get_functions_for_repo(repo_id, session):
    return session.query(Function).filter_by(repo_id=repo_id).all()


def get_by_metric(repo_id, metric, session):
    field = getattr(Function, metric)
    return session.query(field) \
                  .filter_by(repo_id=repo_id) \
                  .filter(field.isnot(None)) \
                  .all()


def get_distinct_function_for_project():
    # Query to select distinct names from the Function table
    names = session.query(Function.name).filter().distinct().all()

    # Convert list of tuples to a set of names
    unique_names = [name[0] for name in names]

    return unique_names


def get_training_text_for_repo(repo_id):
    """
    Given a repo_id, return an ordered corpus of names from all project functions,
    ordered by file and order within file.
    # TODO: Remove preprended _
    """
    functions = (
        session.query(Function)
        .filter_by(repo_id=repo_id)
        .order_by(asc(Function.file_name), asc(Function.order))
        .all()
    )

    names = []

    for function in functions:
        fn_names = []
        for name in function.names.split(" "):
            fn_names.append(casestyle.camelcase(name).lower())

        names.append(" ".join(fn_names))

    return "\n".join(names)


def get_grammar_by_name(name):
    return (
        session.query(Function)
        .filter(Function.name == name, Function.grammar.isnot(None))
        .first()
    )


def get_distinct_function_names_without_grammar():
    names_by_lang = (
        session.query(Function.name, Function.lang)
        .join(Repo, Repo.id == Function.repo_id)
        .filter(Repo.type == "WEB")
        .filter((Function.grammar == None) | (Function.grammar == ""))
        .distinct()
        .all()
    )

    lang_counts = {}
    balanced_names = []

    for name, lang in names_by_lang:
        if lang not in lang_counts:
            lang_counts[lang] = 0
        if lang_counts[lang] < 10000:
            balanced_names.append(name)
            lang_counts[lang] += 1

    random.shuffle(balanced_names)
    return balanced_names


def update_function_grammar(session, name, new_grammar):
    session.query(Function).filter(Function.name == name).update(
        {"grammar": new_grammar}
    )


def update_function_metrics(function, keys, value):
    # if function.metrics:
    #     metrics = function.metrics
    # else:
    #     metrics = {}

    # if type(keys) is list:
    #     metrics[keys[0]] = {keys[1]: value}
    # else:
    #     metrics[keys] = value

    # function.metrics = json.dumps(metrics)
    session.commit()


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


def get_top_function_names():
    # Step A: Identify 500 repos with the largest number of related functions
    # We need a subquery to count functions per repo
    subquery = (
        session.query(Function.repo_id, func.count("*").label("func_count"))
        .group_by(Function.repo_id)
        .subquery()
    )

    # Now, find the top 500 repos based on function count
    top_repos = (
        session.query(subquery.c.repo_id)
        .order_by(subquery.c.func_count.desc())
        .limit(500)
    )

    # Step B: For each of these repos, fetch 200 function names
    # We will use the `in_` operator to filter on the repo IDs obtained above
    functions = (
        session.query(Function.name)
        .filter(Function.repo_id.in_(top_repos))
        .limit(200 * 500)
    )  # Fetch up to 100,000 function names (200 per repo)

    # Fetch the results and extract function names
    function_names = [func.name for func in functions]

    return function_names


def mark_irrelevant(function, is_relevant):
    function.relevant = is_relevant
    session.commit()
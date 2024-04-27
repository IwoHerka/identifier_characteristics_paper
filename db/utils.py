from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from db.engine import engine, Base
from db.models import Repo

session = None


def init_session():
    global session
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


def add_repo(id, name, stars, size, lang, owner):
    new_repo = Repo(id=id, name=name, stars=stars, size=size, lang=lang, owner=owner)

    try:
        session.add(new_repo)
        session.commit()
    except IntegrityError:
        print(f'IntegrityError for {id}, {owner}/{name}, skipping')
        session.rollback()


def get_repos():
    return session.query(Repo).all()


def update_repo(repo, path, readme):#, files, loc, readme):
    repo.path = path
    # repo.files = files
    # repo.loc = loc
    repo.readme = readme
    session.commit()

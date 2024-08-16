#!/usr/bin/env python3
"""Module for db."""

from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """The db class. """

    def __init__(self) -> None:
        """
        Initialize the DB instance.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        session.
        """
        if self.__session is None:
            new_session = sessionmaker(bind=self._engine)
            self.__session = new_session()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Adds a user to the database.
        """
        try:
            user = User(email=email, hashed_password=hashed_password)
            self._session.add(user)
            self._session.commit()
        except Exception:
            self._session.rollback()
            user = None
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Filters users by provided conditions.
        """
        properties, values = [], []
        for key, val in kwargs.items():
            if hasattr(User, key):
                properties.append(getattr(User, key))
                values.append(val)
            else:
                raise InvalidRequestError()
        res = self._session.query(User).filter(
            tuple_(*properties).in_([tuple(values)])
        ).first()
        if res is None:
            raise NoResultFound()
        return res

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Updates a user's details.
        """
        user = self.find_user_by(id=user_id)
        if user is None:
            return
        new_data = {}
        for key, value in kwargs.items():
            if hasattr(User, key):
                new_data[getattr(User, key)] = value
            else:
                raise ValueError()
        self._session.query(User).filter(User.id == user_id).update(
            new_data,
            synchronize_session=False,
        )
        self._session.commit()

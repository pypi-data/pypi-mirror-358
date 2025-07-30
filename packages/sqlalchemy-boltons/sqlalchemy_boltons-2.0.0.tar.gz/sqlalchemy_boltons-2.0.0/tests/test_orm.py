import sqlalchemy as sa
import sqlalchemy.orm as sao

from sqlalchemy_boltons import orm as _orm

import pytest


Base = sao.declarative_base()


def _make_rel_1(p=None, c=None):
    p = p or Parent1
    c = c or Child1
    return p.id == c.parent_id


def _make_rel_2(p=None, c=None):
    p = p or Parent2
    c = c or Child2
    return (p.ix == c.parent_ix) & (p.iy == c.parent_iy)


class Parent1(Base):
    __tablename__ = "parent1"

    id = sa.Column(sa.Integer, primary_key=True)

    children = sao.relationship("Child1", back_populates="parent")


class Child1(Base):
    __tablename__ = "child1"

    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.ForeignKey("parent1.id"))

    parent = sao.relationship("Parent1", back_populates="children")


class Parent2(Base):
    __tablename__ = "parent2"

    ix = sa.Column(sa.Integer, primary_key=True)
    iy = sa.Column(sa.String, primary_key=True)

    children = sao.relationship("Child2", back_populates="parent", primaryjoin=_make_rel_2)


class Child2(Base):
    __tablename__ = "child2"

    id = sa.Column(sa.Integer, primary_key=True)
    parent_ix = sa.Column(sa.ForeignKey("parent2.ix"))
    parent_iy = sa.Column(sa.ForeignKey("parent2.iy"))

    parent = sao.relationship("Parent2", primaryjoin=_make_rel_2)


_cases = {"1": (Parent1, Child1, _make_rel_1), "2": (Parent2, Child2, _make_rel_2)}


def assert_same_sql(x, y):
    assert str(x) == str(y), "expected equivalent SQL"


@pytest.mark.parametrize("case", _cases.keys())
@pytest.mark.parametrize("alias_parent", [False, True])
@pytest.mark.parametrize("alias_child", [False, True])
def test_join_expr(case, alias_parent, alias_child):
    Parent, Child, make_rel = _cases[case]

    P = sao.aliased(Parent) if alias_parent else Parent
    C = sao.aliased(Child) if alias_child else Child

    assert_same_sql(_orm.join_expr(P, C.parent), make_rel(P, C))

    Rel = _orm.RelationshipComparator

    if alias_parent:
        assert_same_sql(Rel(C.parent) == P, make_rel(P, C))
    else:
        assert_same_sql(_orm.join_expr(None, C.parent), make_rel(P, C))

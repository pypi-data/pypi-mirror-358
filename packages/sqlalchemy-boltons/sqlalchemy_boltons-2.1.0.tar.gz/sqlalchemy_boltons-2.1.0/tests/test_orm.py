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


def _make_rel_3(p=None, c=None):
    p = p or Parent3
    c = c or Parent3
    return p.id == c.parent_id


def _make_rel_4(p=None, c=None):
    p = p or Parent4
    c = c or Parent4
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


class Parent3(Base):
    __tablename__ = "parent3"

    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.ForeignKey("parent3.id"), index=True, nullable=True)

    parent = sao.relationship(
        "Parent3", primaryjoin=_make_rel_3, foreign_keys=parent_id, remote_side=id, backref="children"
    )


class Parent4(Base):
    __tablename__ = "parent4"

    ix = sa.Column(sa.Integer, primary_key=True)
    iy = sa.Column(sa.String, primary_key=True)

    parent_ix = sa.Column(sa.ForeignKey("parent4.ix"), index=True, nullable=True)
    parent_iy = sa.Column(sa.ForeignKey("parent4.iy"), index=True, nullable=True)

    parent = sao.relationship(
        "Parent4",
        primaryjoin=_make_rel_4,
        foreign_keys=[parent_ix, parent_iy],
        remote_side=[ix, iy],
        back_populates="children",
    )
    children = sao.relationship(
        "Parent4",
        primaryjoin=_make_rel_4,
        foreign_keys=[parent_ix, parent_iy],
        remote_side=[parent_ix, parent_iy],
        back_populates="parent",
    )


_parent_child_cases = {
    "simple": (Parent1, Child1, _make_rel_1),
    "simple_multikey": (Parent2, Child2, _make_rel_2),
    "selfref": (Parent3, Parent3, _make_rel_3),
    "selfref_multikey": (Parent4, Parent4, _make_rel_4),
}


def assert_same_sql(x, y):
    assert str(x) == str(y), "expected equivalent SQL"


@pytest.mark.parametrize("alias_parent", [False, True])
@pytest.mark.parametrize("alias_child", [False, True])
@pytest.mark.parametrize("case", _parent_child_cases.keys())
def test_join_expr_parent_child(case, alias_parent, alias_child):
    Parent, Child, make_rel = _parent_child_cases[case]

    P = sao.aliased(Parent) if alias_parent else Parent
    C = sao.aliased(Child) if alias_child else Child

    if (Parent is Child) and not (alias_child and alias_parent):
        pytest.skip(reason="doesn't make sense for a self-referential relationship")

    assert_same_sql(_orm.join_expr(P, C.parent), make_rel(P, C))

    Rel = _orm.RelationshipComparator

    if alias_parent:
        assert_same_sql(_orm.join_expr(C, P.children), make_rel(P, C))
        assert_same_sql(Rel(C.parent) == P, make_rel(P, C))
        assert_same_sql(Rel(P.children) == C, make_rel(P, C))

        assert_same_sql(Rel(C.parent) != P, ~make_rel(P, C))
        assert_same_sql(Rel(P.children) != C, ~make_rel(P, C))
    else:
        assert_same_sql(_orm.join_expr(None, C.parent), make_rel(P, C))


def test_Rel_None():
    Rel = _orm.RelationshipComparator
    P = sao.aliased(Parent1)

    Rel(P.children)  # this should be fine

    with pytest.raises(TypeError):
        Rel(P.children) == None  # noqa

    with pytest.raises(TypeError):
        Rel(P.children) != None  # noqa


_rel_children_parent = _orm.Relationships(
    lambda: dict(a=RParent1, b=RChild1),
    dict(ab="children", ba="parent"),
    lambda fk, a, b: a.id == fk(b.parent_id),
)


class RParent1(Base):
    __tablename__ = "rparent1"

    id = sa.Column(sa.Integer, primary_key=True)

    children = _rel_children_parent.a_to_b()
    children2 = sao.relationship("RChild1", back_populates="parent2", viewonly=True)


class RChild1(Base):
    __tablename__ = "rchild1"

    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.ForeignKey("rparent1.id"))

    parent = _rel_children_parent.b_to_a()
    parent2 = sao.relationship("RParent1", back_populates="children2", viewonly=True)


_rel_rnode1 = _orm.Relationships(
    lambda: dict(a=RNode1, m=RNode1.__table__, b=RNode1),
    dict(ab="children", ba="parent"),
    lambda fk, a, b, m: a.id == fk(m.c.assoc_left_id),
    lambda fk, a, b, m: b.id == fk(m.c["assoc_right_id"]),
)


class RNode1(Base):
    # torture test for the ORM relationship feature
    __tablename__ = "rnode1"
    id = sa.Column(sa.Integer, primary_key=True)

    assoc_left_id = sa.Column(sa.ForeignKey("rnode1.id"))
    assoc_right_id = sa.Column(sa.ForeignKey("rnode1.id"))

    children = _rel_rnode1.a_to_b()
    parent = _rel_rnode1.b_to_a()

    children2 = sao.relationship(
        "RNode1",
        secondary=lambda: RNode1.__table__,
        primaryjoin=lambda: RNode1.id == sao.foreign(sao.remote(RNode1.__table__.c.assoc_left_id)),
        secondaryjoin=lambda: RNode1.id == sao.foreign(sao.remote(RNode1.__table__.c.assoc_right_id)),
        back_populates="parent2",
        viewonly=True,
    )
    parent2 = sao.relationship(
        "RNode1",
        secondary=lambda: RNode1.__table__,
        secondaryjoin=lambda: RNode1.id == sao.foreign(sao.remote(RNode1.__table__.c.assoc_left_id)),
        primaryjoin=lambda: RNode1.id == sao.foreign(sao.remote(RNode1.__table__.c.assoc_right_id)),
        back_populates="children2",
        viewonly=True,
    )


_relpair_cases = {
    "simple": (RParent1, RChild1),
    "node": (RNode1, RNode1),
}


@pytest.mark.parametrize("case", _relpair_cases.keys())
def test_relpair_simple(case):
    Parent, Child = _relpair_cases[case]
    P = sao.aliased(Parent)
    C = sao.aliased(Child)

    assert_same_sql(*(sa.select(P).join(C, rel).where(P.id == 3, P.id != C.id) for rel in (P.children, P.children2)))

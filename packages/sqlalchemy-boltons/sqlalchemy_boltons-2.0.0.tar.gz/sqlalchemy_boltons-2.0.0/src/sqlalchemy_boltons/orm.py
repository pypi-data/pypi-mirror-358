from __future__ import annotations

from sqlalchemy.sql import coercions as _coercions, util as _util


class RelationshipComparator:
    """
    This wrapper makes it possible to compare a table against a relationship using :func:`join_expr`. This can be used
    for constructing a subquery that filters using a relationship to a table from the outer query.

    For example::

        import sqlalchemy as sa
        from sqlalchemy import orm as sao
        from sqlalchemy_boltons.orm import RelationshipComparator as Rel

        Base = sao.declarative_base()


        class Parent(Base):
            __tablename__ = "parent"

            id = sa.Column(sa.Integer, primary_key=True)

            children = sao.relationship("Child", back_populates="parent")


        class Child(Base):
            __tablename__ = "child"

            id = sa.Column(sa.Integer, primary_key=True)
            parent_id = sa.Column(sa.ForeignKey("parent.id"), index=True)

            parent = sao.relationship("Parent", back_populates="children")


        # We want a query that selects every Parent that has at least one child. We also want to use aliases.
        P = sao.aliased(Parent)
        C = sao.aliased(Child)

        # This is the boring old way of doing it, which requires explicitly stating the filtering conditions in terms
        # of the columns in both tables.
        q1 = sa.select(P).where(sa.select(C).where(C.parent_id == P.id).exists())

        # Reuse the filtering conditions from the ORM relationship!
        q2 = sa.select(P).where(sa.select(C).where(Rel(C.parent) == P).exists())

        assert str(q1) == str(q2), "these should produce the same SQL code!"

    Based on this discussion: https://groups.google.com/g/sqlalchemy/c/R-qOlzzVi0o/m/NtFswgJioDIJ
    """

    def __init__(self, relationship):
        self._relationship = relationship

    def __eq__(self, other):
        if other is None:
            raise TypeError("cannot compare against None")
        return join_expr(other, self._relationship)

    def __ne__(self, other):
        return ~(self == other)


def join_expr(right, relationship):
    """
    Turn an ORM relationship into an expression that you can use for filtering.
    """

    expr = _coercions.expect(_coercions.roles.ColumnArgumentRole, relationship)
    if right is not None:
        right = _coercions.expect(_coercions.roles.FromClauseRole, right)
        expr = _util.ClauseAdapter(right).traverse(expr)
    return expr

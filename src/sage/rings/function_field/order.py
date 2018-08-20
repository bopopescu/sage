r"""
Orders of function fields

An order of a function field is a subring that is, as a module over the base
maximal order, finitely generated and of maximal rank `n`, where `n` is the
extension degree of the function field. All orders are subrings of maximal
orders.

A rational function field has two maximal orders: maximal finite order `o` and
maximal infinite order `o_\infty`. The maximal order of a rational function
field over constant field `k` is just the polynomial ring `o=k[x]`. The
maximal infinite order is the set of rational functions whose denominator has
degree greater than or equal to that of the numerator.

EXAMPLES::

    sage: K.<x> = FunctionField(QQ)
    sage: O = K.maximal_order()
    sage: I = O.ideal(1/x); I
    Ideal (1/x) of Maximal order of Rational function field in x over Rational Field
    sage: 1/x in O
    False
    sage: Oinf = K.maximal_order_infinite()
    sage: 1/x in Oinf
    True

In an extension of a rational function field, an order over the maximal finite
order is called a finite order while an order over the maximal infinite order
is called an infinite order. Thus a function field has one maximal finite order
`O` and one maximal infinite order `O_\infty`. There are other non-maximal
orders such as equation orders::

    sage: K.<x> = FunctionField(GF(3)); R.<y> = K[]
    sage: L.<y> = K.extension(y^3-y-x)
    sage: O = L.equation_order()
    sage: 1/y in O
    False
    sage: x/y in O
    True

Sage provides an extensive functionality for computations in maximal orders of
global function fields. For example, you can decompose a prime ideal of a
rational function field in an extension::

    sage: K.<x> = FunctionField(GF(2)); _.<t> = K[]
    sage: o = K.maximal_order()
    sage: p = o.ideal(x+1)
    sage: p.is_prime()
    True

    sage: F.<y> = K.extension(t^3 - x^2*(x^2 + x + 1)^2)
    sage: O = F.maximal_order()
    sage: O.decomposition(p)
    [(Ideal (x + 1, y + 1) of Maximal order
     of Function field in y defined by y^3 + x^6 + x^4 + x^2, 1, 1),
     (Ideal (x + 1, y^2 + y + 1) of Maximal order
     of Function field in y defined by y^3 + x^6 + x^4 + x^2, 2, 1)]

    sage: p1,relative_degree,ramification_index = O.decomposition(p)[1]
    sage: p1.parent()
    Monoid of ideals of Maximal order of Function field in y
    defined by y^3 + x^6 + x^4 + x^2
    sage: relative_degree
    2
    sage: ramification_index
    1

AUTHORS:

- William Stein (2010): initial version

- Maarten Derickx (2011-09-14): fixed ideal_with_gens_over_base() for rational function fields

- Julian Rueth (2011-09-14): added check in _element_constructor_

- Kwankyu Lee (2017-04-30): added maximal orders of global function fields

"""
from __future__ import absolute_import
#*****************************************************************************
#       Copyright (C) 2010 William Stein <wstein@gmail.com>
#       Copyright (C) 2011 Maarten Derickx <m.derickx.student@gmail.com>
#       Copyright (C) 2011 Julian Rueth <julian.rueth@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import cached_method
from sage.misc.lazy_import import lazy_import

from sage.rings.ring import IntegralDomain, PrincipalIdealDomain

from sage.modules.free_module_element import vector
from sage.arith.all import lcm, gcd

from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation

from sage.categories.rings import Rings
from sage.categories.integral_domains import IntegralDomains
from sage.categories.principal_ideal_domains import PrincipalIdealDomains
from sage.categories.euclidean_domains import EuclideanDomains

from .ideal import is_Ideal, IdealMonoid
from .ideal import (
    FunctionFieldIdeal_module,
    FunctionFieldIdeal_rational,
    FunctionFieldIdeal_global,
    FunctionFieldIdealInfinite_rational,
    FunctionFieldIdealInfinite_global)

lazy_import('sage.matrix.special', 'block_matrix')
lazy_import('sage.matrix.constructor', 'matrix')

class FunctionFieldOrder(Parent):
    """
    Base class for orders in function fields.
    """
    def __init__(self, field, category=None):
        """
        Initialize.

        INPUT:

        - ``field`` -- function field

        EXAMPLES::

            sage: F = FunctionField(QQ,'y')
            sage: F.maximal_order()
            Maximal order of Rational function field in y over Rational Field
        """
        Parent.__init__(self, category=category or IntegralDomains())
        self._field = field

    def _repr_(self):
        """
        Return the string representation.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order()._repr_()
            'Maximal order of Rational function field in y over Rational Field'
        """
        return "Order in {}".format(self._field)

    def is_finite(self):
        """
        Return ``False`` since orders are never finite.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order().is_finite()
            False
        """
        return False

    def is_field(self):
        """
        Return ``False`` since orders are never fields.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order().is_field()
            False
        """
        return False

    def is_noetherian(self):
        """
        Return ``True`` since orders in function fields are noetherian.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order().is_noetherian()
            True
        """
        return True

    def function_field(self):
        """
        Return the function field to which the order belongs.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order().function_field()
            Rational function field in y over Rational Field
        """
        return self._field

    fraction_field = function_field

    def is_subring(self, other):
        """
        Return ``True`` if the order is a subring of the other order.

        INPUT:

        - ``other`` -- order of the function field or the field itself

        EXAMPLES::

            sage: F = FunctionField(QQ,'y')
            sage: O = F.maximal_order()
            sage: O.is_subring(F)
            True
        """
        if other is self._field:
            return True
        else:
            raise NotImplementedError

    @cached_method
    def ideal_monoid(self):
        """
        Return the monoid of ideals of the order.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order().ideal_monoid()
            Monoid of ideals of Maximal order of Rational function field in y over Rational Field
        """
        return IdealMonoid(self)

class FunctionFieldOrder_basis(FunctionFieldOrder):
    """
    Order given by a basis over the maximal order of the base field.
    """
    def __init__(self, basis, check=True):
        """
        Initialize.

        INPUT:

        - ``basis`` -- list of elements of the function field

        - ``check`` -- (default: ``True``) if ``True``, check whether the module
          that ``basis`` generates forms an order

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order(); O
            Order in Function field in y defined by y^4 + x*y + 4*x + 1

        The basis only defines an order if the module it generates is closed under
        multiplication and contains the identity element::

            sage: K.<x> = FunctionField(QQ)
            sage: R.<y> = K[]
            sage: L.<y> = K.extension(y^5 - (x^3 + 2*x*y + 1/x));
            sage: y.is_integral()
            False
            sage: L.order(y)
            Traceback (most recent call last):
            ...
            ValueError: The module generated by basis [1, y, y^2, y^3, y^4] must be closed under multiplication

        The basis also has to be linearly independent and of the same rank as the
        degree of the function field of its elements (only checked when ``check``
        is ``True``)::

            sage: L.order(L(x))
            Traceback (most recent call last):
            ...
            ValueError: Basis [1, x, x^2, x^3, x^4] is not linearly independent
            sage: sage.rings.function_field.order.FunctionFieldOrder_basis([y,y,y^3,y^4,y^5])
            Traceback (most recent call last):
            ...
            ValueError: Basis [y, y, y^3, y^4, 2*x*y + (x^4 + 1)/x] is not linearly independent
        """
        if len(basis) == 0:
            raise ValueError("basis must have positive length")

        field = basis[0].parent()
        if len(basis) != field.degree():
            raise ValueError("length of basis must equal degree of field")

        FunctionFieldOrder.__init__(self, field)

        self._basis = tuple(basis)
        V, fr, to = field.vector_space()
        R = field.base_field().maximal_order()
        self._from_module= fr
        self._to_module = to
        self._module = V.span([to(b) for b in basis], base_ring=R)
        self._ring = field.polynomial_ring()
        self._populate_coercion_lists_(coerce_list=[self._ring])
        if check:
            if self._module.rank() != field.degree():
                raise ValueError("Basis %s is not linearly independent"%(basis))
            if not to(field(1)) in self._module:
                raise ValueError("The identity element must be in the module spanned by basis %s"%(basis))
            if not all(to(a*b) in self._module for a in basis for b in basis):
                raise ValueError("The module generated by basis %s must be closed under multiplication"%(basis))

    def _element_constructor_(self, f, check=True):
        """
        Make ``f`` an element of the order.

        INPUT:

        - ``f`` -- the element

        - ``check`` -- check if the element is in the order

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: K.maximal_order()._element_constructor_(x)
            x
        """
        field = self.function_field()

        if f.parent() is field:
            f = f.element()
        f = self._ring(f)
        if check:
            V, fr, to = field.vector_space()
            f_vector = to(field(f))
            if not f_vector in self._module:
                raise TypeError("%r is not an element of %r"%(f_vector,self))
        return field._element_class(self, f)

    def ideal_with_gens_over_base(self, gens, ideal_class=None):
        """
        Return the fractional ideal with basis ``gens`` over the
        maximal order of the base field. That this is really an ideal
        is not checked.

        INPUT:

        - ``gens`` -- list of elements of the function field

        - ``ideal_class`` -- class of the ideal generated

        EXAMPLES:

        We construct an ideal in a rational function field::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: I = O.ideal([y]); I
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: I*I
            Ideal (y^2) of Maximal order of Rational function field in y over Rational Field

        We construct some ideals in a nontrivial function field::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.equation_order(); O
            Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I = O.ideal_with_gens_over_base([1, y]);  I
            Ideal (1, y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I.module()
            Free module of degree 2 and rank 2 over Maximal order of Rational function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0]
            [0 1]

        There is no check if the resulting object is really an ideal::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.equation_order()
            sage: I = O.ideal_with_gens_over_base([y]); I
            Ideal (y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: y in I
            True
            sage: y^2 in I
            False
        """
        F = self.function_field()
        S = F.base_field().maximal_order()

        gens = [F(a) for a in gens]

        V, from_V, to_V = F.vector_space()
        M = V.span([to_V(b) for b in gens], base_ring=S)

        if ideal_class is None:
            ideal_class = FunctionFieldIdeal_module
        return ideal_class(self, M)

    def ideal(self, *gens, **kwargs):
        """
        Return the fractional ideal generated by the elements in ``gens``.

        INPUT:

        - ``gens`` -- list of generators or an ideal in a ring which
          coerces to this order

        EXAMPLES::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O.ideal(y)
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: O.ideal([y,1/y]) == O.ideal(y,1/y) # multiple generators may be given as a list
            True

        A fractional ideal of a nontrivial extension::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: O = K.maximal_order()
            sage: I = O.ideal(x^2-4)
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: S = L.equation_order()
            sage: S.ideal(1/y)
            Ideal (1, (6/(x^3 + 1))*y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I2 = S.ideal(x^2-4); I2
            Ideal (x^2 + 3, (x^2 + 3)*y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I2 == S.ideal(I)
            True
        """
        if len(gens) == 1:
            gens = gens[0]
            if not isinstance(gens, (list, tuple)):
                if is_Ideal(gens):
                    gens = gens.gens()
                else:
                    gens = [gens]
        K = self.function_field()

        if 'ideal_class' in kwargs:
            ideal_class = kwargs['ideal_class']
        else:
            ideal_class = None

        return self.ideal_with_gens_over_base([b*K(g) for b in self.basis() for g in gens],
                                              ideal_class=ideal_class)

    def polynomial(self):
        """
        Return the defining polynomial of the function field of which this is an order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.polynomial()
            y^4 + x*y + 4*x + 1
        """
        return self._field.polynomial()

    def basis(self):
        """
        Return a basis of the order over the maximal order of the base field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.basis()
            (1, y, y^2, y^3)
        """
        return self._basis

    def free_module(self):
        """
        Return the free module formed by the basis over the maximal order
        of the base function field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.free_module()
            Free module of degree 4 and rank 4 over Maximal order of Rational function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0 0 0]
            [0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]
        """
        return self._module

    def coordinate_vector(self, e):
        """
        Return the cooridinates of ``e`` with respect to the basis of the order.

        INPUT:

        - ``e`` -- element of the order or the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: f = (x + y)^3
            sage: O.coordinate_vector(f)
            (x^3, 3*x^2, 3*x, 1)
        """
        return self._module.coordinate_vector(self._to_module(e), check=False)

class FunctionFieldOrderInfinite(FunctionFieldOrder):
    """
    Base class for infinite orders on function fields.
    """
    def _repr_(self):
        """
        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order()._repr_()
            'Maximal order of Rational function field in y over Rational Field'
        """
        return "Infinite order in %s"%self.function_field()

class FunctionFieldOrderInfinite_basis(FunctionFieldOrderInfinite):
    """
    Order given by a basis over the infinite maximal order of the base
    field.

    EXAMPLES::

        sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
        sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
        sage: O = L.equation_order(); O
        Order in Function field in y defined by y^4 + x*y + 4*x + 1
        sage: type(O)
        <class 'sage.rings.function_field.order.FunctionFieldOrder_basis_with_category'>

    The basis only defines an order if the module it generates is closed under
    multiplication and contains the identity element (only checked when
    ``check`` is ``True``)::

        sage: K.<x> = FunctionField(QQ)
        sage: R.<y> = K[]
        sage: L.<y> = K.extension(y^5 - (x^3 + 2*x*y + 1/x));
        sage: y.is_integral()
        False
        sage: L.order(y)
        Traceback (most recent call last):
        ...
        ValueError: The module generated by basis [1, y, y^2, y^3, y^4] must be closed under multiplication

    The basis also has to be linearly independent and of the same rank as the
    degree of the function field of its elements (only checked when ``check``
    is ``True``)::

        sage: L.order(L(x))
        Traceback (most recent call last):
        ...
        ValueError: Basis [1, x, x^2, x^3, x^4] is not linearly independent
        sage: sage.rings.function_field.order.FunctionFieldOrder_basis([y,y,y^3,y^4,y^5])
        Traceback (most recent call last):
        ...
        ValueError: Basis [y, y, y^3, y^4, 2*x*y + (x^4 + 1)/x] is not linearly independent
    """
    def __init__(self, basis, check=True):
        """
        Initialize.

        INPUT:

        - ``basis`` -- elements of the function field

        - ``check`` -- boolean (default: ``True``); if ``True``, check the basis generates
          an order

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: L.equation_order()
            Order in Function field in y defined by y^4 + x*y + 4*x + 1
        """
        if len(basis) == 0:
            raise ValueError("basis must have positive length")

        field = basis[0].parent()
        if len(basis) != field.degree():
            raise ValueError("length of basis must equal degree of field")

        FunctionFieldOrder.__init__(self, field)

        # The function field element f is in this order if and only if
        # W.coordinate_vector(to(f)) in M
        V, fr, to = field.vector_space()
        R = field.base_field().maximal_order_infinite()
        W = V.span_of_basis([to(v) for v in basis])
        from sage.modules.free_module import FreeModule
        M = FreeModule(R,W.dimension())
        self._basis = tuple(basis)
        self._ambient_space = W
        self._module = M

        self._ring = field.polynomial_ring()
        self._populate_coercion_lists_(coerce_list=[self._ring])

        if check:
            if self._module.rank() != field.degree():
                raise ValueError("Basis %s is not linearly independent"%(basis))
            if not W.coordinate_vector(to(field(1))) in self._module:
                raise ValueError("The identity element must be in the module spanned by basis %s"%(basis))
            if not all(W.coordinate_vector(to(a*b)) in self._module for a in basis for b in basis):
                raise ValueError("The module generated by basis %s must be closed under multiplication"%(basis))

    def _element_constructor_(self, f, check=True):
        """
        Make ``f`` an element of this order.

        INPUT:

        - ``f`` -- the element

        - ``check`` -- check if the element is in the order

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: K.maximal_order()._element_constructor_(x)
            x
        """
        field=self.function_field()

        if not f.parent() is field:
            f = field(f)
        if check:
            V, fr, to = field.vector_space()
            W = self._ambient_space
            if not W.coordinate_vector(to(f)) in self._module:
                raise TypeError("%r is not an element of %r"%(f,self))
        return field._element_class(self, f.element())

    def ideal_with_gens_over_base(self, gens, ideal_class=None):
        """
        Return the fractional ideal with basis ``gens`` over the
        maximal order of the base field. That this is really an ideal
        is not checked.

        INPUT:

        - ``gens`` -- list of elements that are a basis for the
              ideal over the maximal order of the base field

        - ``ideal_class`` -- the class of the ideal generated

        EXAMPLES:

        We construct an ideal in a rational function field::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: I = O.ideal([y]); I
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: I*I
            Ideal (y^2) of Maximal order of Rational function field in y over Rational Field

        We construct some ideals in a nontrivial function field::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.equation_order(); O
            Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I = O.ideal_with_gens_over_base([1, y]);  I
            Ideal (1, y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: I.module()
            Free module of degree 2 and rank 2 over Maximal order of Rational function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0]
            [0 1]

        There is no check if the resulting object is really an ideal::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.equation_order()
            sage: I = O.ideal_with_gens_over_base([y]); I
            Ideal (y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: y in I
            True
            sage: y^2 in I
            False
        """
        F = self.function_field()
        S = F.base_field().maximal_order_infinite()

        gens = [F(a) for a in gens]

        V, from_V, to_V = F.vector_space()
        M = V.span([to_V(b) for b in gens], base_ring=S) # not work

        if ideal_class is None:
            ideal_class = FunctionFieldIdealInfinite_module
        return ideal_class(self, M)

    def ideal(self, *gens, **kwargs):
        """
        Return the fractional ideal generated by the elements in ``gens``.

        INPUT:

        - ``gens`` -- list of generators or an ideal in a ring which coerces
          to this order.

        EXAMPLES::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O.ideal(y)
            Ideal (y) of Maximal order of Rational function field in y over Rational Field
            sage: O.ideal([y,1/y]) == O.ideal(y,1/y) # multiple generators may be given as a list
            True

        A fractional ideal of a nontrivial extension::

            sage: K.<x> = FunctionField(QQ); R.<y> = K[]
            sage: O = K.maximal_order_infinite()
            sage: I = O.ideal(x^2-4)
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: S = L.order_infinite_with_basis([1, 1/x^2*y])
        """
        if len(gens) == 1:
            gens = gens[0]
            if not isinstance(gens, (list, tuple)):
                if is_Ideal(gens):
                    gens = gens.gens()
                else:
                    gens = [gens]
        K = self.function_field()

        if 'ideal_class' in kwargs:
            ideal_class = kwargs['ideal_class']
        else:
            ideal_class = None

        return self.ideal_with_gens_over_base([b*K(g) for b in self.basis() for g in gens],
                                              ideal_class=ideal_class)

    def function_field(self):
        """
        Return the function field in which this is an order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.function_field()
            Function field in y defined by y^4 + x*y + 4*x + 1
        """
        return self._field

    fraction_field = function_field

    def polynomial(self):
        """
        Return the defining polynomial of the function field of which this is an order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.polynomial()
            y^4 + x*y + 4*x + 1
        """
        return self._field.polynomial()

    def basis(self):
        """
        Return a basis of this order over the maximal order of the base field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.basis()
            (1, y, y^2, y^3)
        """
        return self._basis

    def free_module(self):
        """
        Return the free module formed by the basis over the maximal order of
        the base field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.free_module()
            Free module of degree 4 and rank 4 over Maximal order of Rational function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0 0 0]
            [0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]
        """
        return self._module

class FunctionFieldMaximalOrder(FunctionFieldOrder):
    """
    Base class of maximal orders of function fields.
    """
    def _repr_(self):
        """
        Return the string representation of the order.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order()._repr_()
            'Maximal order of Rational function field in y over Rational Field'
        """
        return "Maximal order of %s"%(self.function_field(),)

class FunctionFieldMaximalOrder_rational(FunctionFieldMaximalOrder):
    """
    Maximal orders of rational function fields.
    """
    def __init__(self, field):
        """
        Initialize.

        INPUT:

        - ``field`` -- function field

        EXAMPLES::

            sage: K.<t> = FunctionField(GF(19)); K
            Rational function field in t over Finite Field of size 19
            sage: R = K.maximal_order(); R
            Maximal order of Rational function field in t over Finite Field of size 19
        """
        FunctionFieldMaximalOrder.__init__(self, field, category=EuclideanDomains())

        self._populate_coercion_lists_(coerce_list=[field._ring])

        self._ring = field._ring
        self._gen = self(self._ring.gen())
        self._basis = (self.one(),)

    def _element_constructor_(self, f):
        """
        Make ``f`` an element of this order.

        EXAMPLES::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O._element_constructor_(y)
            y
            sage: O._element_constructor_(1/y)
            Traceback (most recent call last):
            ...
            TypeError: 1/y is not an element of Maximal order of Rational function field in y over Rational Field
        """
        if f.parent() is self.function_field():
            if not f.denominator() in self.function_field().constant_base_field():
                raise TypeError("%r is not an element of %r"%(f,self))
            f = f.element()
        from .element import FunctionFieldElement_rational
        return FunctionFieldElement_rational(self, self._ring(f))

    def _residue_field(self, ideal, name=None):
        """
        Return a field isomorphic to the residue field at the prime ideal.

        INPUT:

        - ``ideal`` -- prime ideal of the order

        - ``name`` -- string; name of the generator of the residue field

        OUTPUT:

        - a field isomorphic to the residue field

        - an isomorphism from the finite field to the residue field

        - the inverse isomorphism

        The residue field is by definition `k[x]/q` where `q` is the irreducible
        polynomial generating the prime ideal and `k` is the constant base field.

        EXAMPLES::

            sage: F.<x> = FunctionField(GF(2))
            sage: O = F.maximal_order()
            sage: I = O.ideal(x^2+x+1)
            sage: R, fr_R, to_R = O._residue_field(I)
            sage: R
            Finite Field in z2 of size 2^2
            sage: [to_R(fr_R(e)) == e for e in R]
            [True, True, True, True]
            sage: to_R(x*(x+1)) == to_R(x) * to_R(x+1)
            True
        """
        F = self.function_field()

        if not F.is_global():
            raise NotImplementedError

        q = ideal.gen().element().numerator()
        R, _from_R, _to_R = self._residue_field_global(q, name=name)

        def from_R(e):
            return F(_from_R(e))

        def to_R(f):
            return _to_R(f.numerator())

        return R, from_R, to_R

    def _residue_field_global(self, q, name=None):
        """
        Return a finite field isomorphic to the residue field at q.

        This method assumes a global rational function field, that is,
        the constant base field is a finite field.

        INPUT:

        - ``q`` -- irreducible polynomial

        - ``name`` -- string; name of the generator of the extension field

        OUTPUT:

        - a finite field

        - a function that outputs a polynomial lifting a finite field element

        - a function that outputs a finite field element for a polynomial

        The residue field is by definition `k[x]/q` where `k` is the base field.

        EXAMPLES::

            sage: k.<a> = GF(4)
            sage: F.<x> = FunctionField(k)
            sage: O = F.maximal_order()
            sage: O._ring
            Univariate Polynomial Ring in x over Finite Field in a of size 2^2
            sage: f = x^3 + x + 1
            sage: _f = f.numerator()
            sage: _f.is_irreducible()
            True
            sage: K, fr_K, to_K = O._residue_field_global(_f)
            sage: K
            Finite Field in z6 of size 2^6
            sage: all(to_K(fr_K(e)) == e for e in K)
            True

            sage: k.<a> = GF(2)
            sage: F.<x> = FunctionField(k)
            sage: O = F.maximal_order()
            sage: O._ring
            Univariate Polynomial Ring in x over Finite Field of size 2 (using GF2X)
            sage: f = x^3 + x + 1
            sage: _f = f.numerator()
            sage: _f.is_irreducible()
            True
            sage: K, fr_K, to_K = O._residue_field_global(_f)
            sage: all(to_K(fr_K(e)) == e for e in K)
            True

        """
        # polynomial ring over the base field
        R = self._ring
        x = R.gen()

        # base field of extension degree r over the prime field
        k = R.base_ring()
        a = k.gen()
        r = k.degree()

        # extend the base field to a field of degree r*s over the
        # prime field
        s = q.degree()
        K,sigma = k.extension(s, map=True, name=name)

        # find a root beta in K satisfying the irreducible q
        S = K['X']
        beta = S([sigma(c) for c in q.list()]).roots()[0][0]

        # V is a vector space over the prime subfield of k of degree r*s
        V = K.vector_space()

        w = K.one()
        beta_pow = []
        for i in range(s):
            beta_pow.append(w)
            w *= beta

        w = K.one()
        sigma_a = sigma(a)
        sigma_a_pow = []
        for i in range(r):
            sigma_a_pow.append(w)
            w *= sigma_a

        basis = [V(sigma_a_pow[j]*beta_pow[i]) for i in range(s) for j in range(r)]
        W = V.span_of_basis(basis)

        def to_K(f):
            coeffs = (f % q).list()
            return sum([sigma(coeffs[i]) * beta_pow[i] for i in range(len(coeffs))], K.zero())

        if r == 1: # take care of the prime field case
            def fr_K(g):
                co = W.coordinates(V(g),check=False)
                return R([k(co[j]) for j in range(s)])
        else:
            t = r * s
            def fr_K(g):
                co = W.coordinates(V(g),check=False)
                return R([k(co[i:i+r]) for i in range(0,t,r)])

        return K, fr_K, to_K

    def basis(self):
        """
        Return the basis (=1) of the order as a module over the polynomial ring.

        EXAMPLES::

            sage: K.<t> = FunctionField(GF(19))
            sage: O = K.maximal_order()
            sage: O.basis()
            (1,)
            sage: parent(O.basis()[0])
            Maximal order of Rational function field in t over Finite Field of size 19
        """
        return self._basis

    def ideal(self, *gens):
        """
        Return the fractional ideal generated by ``gens``.

        INPUT:

        - ``gens`` -- elements of the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O.ideal(x)
            Ideal (x) of Maximal order of Rational function field in x over Rational Field
            sage: O.ideal([x,1/x]) == O.ideal(x,1/x) # multiple generators may be given as a list
            True
            sage: O.ideal(x^3+1,x^3+6)
            Ideal (1) of Maximal order of Rational function field in x over Rational Field
            sage: I = O.ideal((x^2+1)*(x^3+1),(x^3+6)*(x^2+1)); I
            Ideal (x^2 + 1) of Maximal order of Rational function field in x over Rational Field
            sage: O.ideal(I)
            Ideal (x^2 + 1) of Maximal order of Rational function field in x over Rational Field
        """
        if len(gens) == 1:
            gens = gens[0]
            if not isinstance(gens, (list, tuple)):
                if is_Ideal(gens):
                    gens = gens.gens()
                else:
                    gens = (gens,)
        K = self.function_field()
        gens = [K(e) for e in gens if e != 0]
        if len(gens) == 0:
            gen = K(0)
        else:
            d = lcm([c.denominator() for c in gens]).monic()
            g = gcd([(d*c).numerator() for c in gens]).monic()
            gen = K(g/d)
        return FunctionFieldIdeal_rational(self, gen)

    def gen(self, n=0):
        """
        Return the ``n``-th generator of the order. Since there is only one generator ``n`` must be 0.

        EXAMPLES::

            sage: O = FunctionField(QQ,'y').maximal_order()
            sage: O.gen()
            y
            sage: O.gen(1)
            Traceback (most recent call last):
            ...
            IndexError: Only one generator.
        """
        if n != 0: raise IndexError("Only one generator.")
        return self._gen

    def ngens(self):
        """
        Return 1 the number of generators of the order.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order().ngens()
            1
        """
        return 1

class FunctionFieldMaximalOrder_global(FunctionFieldMaximalOrder):
    """
    Maximal orders of global function fields.
    """
    def __init__(self, field, basis):
        """
        Initialize.

        INPUT:

        - ``field`` -- function field to which this maximal order belongs

        - ``basis`` -- basis of this maximal order as a module over the base
          maximal order

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: L.maximal_order()
            Maximal order of Function field in y defined by y^4 + x*y + 4*x + 1
        """
        FunctionFieldMaximalOrder.__init__(self, field)

        V, fr, to = field.vector_space()
        R = field.base_field().maximal_order()

        # This module is over R, but linear algebra over R (MaximalOrder)
        # is not well supported in Sage. So we keep it as a vector space
        # over rational function field.
        self._module = V.span_of_basis([to(b) for b in basis])
        self._module_base_ring = R
        self._basis = tuple(basis)
        self._from_module = fr
        self._to_module = to

        # multiplication table (lower triangular)
        n = len(basis)
        self._mtable = []
        for i in range(n):
            row = []
            for j in range(n):
                row.append(self._coordinate_vector(basis[i] * basis[j]))
            self._mtable.append(row)

        zero = vector(R._ring,n*[0])
        def mul_vecs(f,g):
            s = zero
            for i in range(n):
                if f[i].is_zero():
                    continue
                for j in range(n):
                    if g[j].is_zero():
                        continue
                    s += f[i] * g[j] * self._mtable[i][j]
            return s
        self._mul_vecs = mul_vecs

        # We prepare for using Kummer's theorem to decompose primes. Note
        # that Kummer's theorem applies to the most of places. Here we find
        # places for which the theorem does not apply.

        # this element is integral over k[x] and a generator of the field.
        for gen in basis[1:]:
            phi = gen.minimal_polynomial()
            if phi.degree() == n:
                break

        if phi.degree() == n:
            gen_vec = self._coordinate_vector(gen)
            g = gen_vec.parent().gen(0) # x
            gen_vec_pow = [g]
            for i in range(n):
                g = mul_vecs(g, gen_vec)
                gen_vec_pow.append(g)

            # find places where {1,gen,...,gen^(n-1)} is not integral basis
            W = V.span_of_basis([to(gen ** i) for i in range(phi.degree())])

            supp = []
            for g in basis:
                for c in W.coordinate_vector(to(g), check=False):
                    if not c.is_zero():
                        supp += [f for f,_ in c.denominator().factor()]
            supp = set(supp)

            self._kummer_gen = gen
            self._kummer_gen_vec_pow = gen_vec_pow
            self._kummer_polynomial = phi
            self._kummer_places = supp

    def _element_constructor_(self, f):
        """
        Construct an element of this order from ``f``.

        INPUT:

        - ``f`` -- element convertible to the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(4)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2-x*Y+x^2+1)
            sage: O = L.maximal_order()
            sage: y in O
            True
            sage: 1/y in O
            False
            sage: x in O
            True
            sage: 1/x in O
            False
            sage: L.<y>=K.extension(Y^2+Y+x+1/x)
            sage: O = L.maximal_order()
            sage: 1 in O
            True
            sage: y in O
            False
            sage: x*y in O
            True
            sage: x^2*y in O
            True
        """
        F = self.function_field()

        if f.parent() is not F:
            f = F(f)

        # check if f is in this order
        if not all(e in self._module_base_ring for e in self.coordinate_vector(f)):
            raise TypeError( "{} is not an element of {}".format(f, self) )

        return f

    def ideal_with_gens_over_base(self, gens):
        """
        Return the fractional ideal with basis ``gens`` over the
        maximal order of the base field.

        INPUT:

        - ``gens`` -- list of elements that generates the
              ideal over the maximal order of the base field

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.maximal_order(); O
            Maximal order of Function field in y defined by y^2 + 6*x^3 + 6
            sage: I = O.ideal_with_gens_over_base([1, y]);  I
            Ideal (1) of Maximal order of Function field in y defined by y^2 + 6*x^3 + 6
            sage: I.module()
            Free module of degree 2 and rank 2 over Maximal order of Rational function field in x over Finite Field of size 7
            Echelon basis matrix:
            [1 0]
            [0 1]

        There is no check if the resulting object is really an ideal::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.equation_order()
            sage: I = O.ideal_with_gens_over_base([y]); I
            Ideal (y) of Order in Function field in y defined by y^2 + 6*x^3 + 6
            sage: y in I
            True
            sage: y^2 in I
            False
        """
        return self._ideal_from_vectors([self.coordinate_vector(g) for g in gens])

    def _ideal_from_vectors(self, vecs):
        """
        Return an ideal generated as a module by vectors over rational function
        field.

        INPUT:

        - ``vec`` -- list of vectors

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.maximal_order()
            sage: v1 = O.coordinate_vector(x^3+1)
            sage: v2 = O.coordinate_vector(y)
            sage: v1
            (x^3 + 1, 0)
            sage: v2
            (0, 1)
            sage: O._ideal_from_vectors([v1,v2])
            Ideal (x^3 + 1, y) of Maximal order of Function field in y
            defined by y^2 + 6*x^3 + 6
        """
        R = self._module_base_ring._ring
        d = lcm([v.denominator() for v in vecs])
        vecs = [[(d*c).numerator() for c in v] for v in vecs]
        return self._ideal_from_vectors_and_denominator(vecs, d, check=False)

    def _ideal_from_vectors_and_denominator(self, vecs, d=1, check=True):
        """
        Return an ideal generated as a module by vectors divided by ``d`` over
        the polynomial ring underlying the rational function field.

        INPUT:

        - ``vec`` -- list of vectors over the polynomial ring

        - ``d`` -- (default: 1) a nonzero element of the polynomial ring

        - ``check`` -- boolean (default: ``True``); if ``True``, compute the real
          denominator of the vectors, possibly different from ``d``.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: O = L.maximal_order()
            sage: I = O.ideal(y^2)
            sage: m = I.basis_matrix()
            sage: v1 = m[0]
            sage: v2 = m[1]
            sage: v1
            (x^3 + 1, 0)
            sage: v2
            (0, x^3 + 1)
            sage: O._ideal_from_vectors([v1,v2])  # indirect doctest
            Ideal (x^3 + 1) of Maximal order of Function field in y
            defined by y^2 + 6*x^3 + 6
        """
        R = self._module_base_ring._ring

        d = R(d) # make it sure that d is in the polynomial ring

        if check and not d.is_one(): # check if d is true denominator
            try:
                M = []
                g = d
                for v in vecs:
                    l = list(v)
                    for c in l:
                        g = g.gcd(c)
                        if g.is_one():
                            raise AssertionError
                    M += l
                d = d // g
                mat = matrix(R, len(vecs), [c // g for c in M])
            except AssertionError:
                mat = matrix(R, vecs)
        else:
            mat = matrix(R, vecs)

        # IMPORTANT: make it sure that pivot polynomials monic
        # so that we get a unique hnf. Here the hermite form
        # algorithm also makes the pivots monic.

        # compute the reverse hermite form with zero rows deleted
        mat.reverse_rows_and_columns()
        mat._hermite_form_euclidean(normalization=lambda p: ~p.lc())
        mat.reverse_rows_and_columns()
        i = 0
        while i < mat.nrows() and mat.row(i).is_zero():
            i += 1
        hnf = mat[i:] # remove zero rows

        return FunctionFieldIdeal_global(self, hnf, d)

    def ideal(self, *gens, **kwargs):
        """
        Return the fractional ideal generated by the elements in ``gens``.

        INPUT:

        - ``gens`` -- list of generators

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: O = K.maximal_order()
            sage: I = O.ideal(x^2-4)
            sage: L.<y> = K.extension(y^2 - x^3 - 1)
            sage: S = L.maximal_order()
            sage: S.ideal(1/y)
            Ideal (1, (1/(x^3 + 1))*y) of Maximal order of Function field
            in y defined by y^2 + 6*x^3 + 6
            sage: I2 = S.ideal(x^2-4); I2
            Ideal (x^2 + 3) of Maximal order of Function field in y defined by y^2 + 6*x^3 + 6
            sage: I2 == S.ideal(I)
            True
        """
        if len(gens) == 1:
            gens = gens[0]
            if not isinstance(gens, (list, tuple)):
                if is_Ideal(gens):
                    gens = gens.gens()
                else:
                    gens = (gens,)
        F = self.function_field()
        mgens = [b*F(g) for g in gens for b in self.basis()]
        return self.ideal_with_gens_over_base(mgens)

    def polynomial(self):
        """
        Return the defining polynomial of the function field of which this is an order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.polynomial()
            y^4 + x*y + 4*x + 1
        """
        return self._field.polynomial()

    def basis(self):
        """
        Return a basis of the order over the maximal order of the base function
        field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.equation_order()
            sage: O.basis()
            (1, y, y^2, y^3)
        """
        return self._basis

    def free_module(self):
        """
        Return the free module formed by the basis over the maximal order of the base field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.maximal_order()
            sage: O.free_module()
            Free module of degree 4 and rank 4 over Maximal order of Rational function field in x over Finite Field of size 7
            User basis matrix:
            [1 0 0 0]
            [0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]
        """
        return self._module.change_ring(self._module_base_ring)

    def coordinate_vector(self, e):
        """
        Return the cooridinates of ``e`` with respect to the basis of this order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.maximal_order()
            sage: O.coordinate_vector(y)
            (0, 1, 0, 0)
            sage: O.coordinate_vector(x*y)
            (0, x, 0, 0)
        """
        return self._module.coordinate_vector(self._to_module(e))

    def _coordinate_vector(self, e):
        """
        Return the cooridinate vector of ``e`` with respect to the basis
        of the order.

        Assuming ``e`` is in the maximal order, the coordinates are given
        as univariate polynomials in the underlying ring of the maximal
        order of the rational function field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.maximal_order()
            sage: O._coordinate_vector(y)
            (0, 1, 0, 0)
            sage: O._coordinate_vector(x*y)
            (0, x, 0, 0)
        """
        v = self._module.coordinate_vector(self._to_module(e), check=False)
        return vector([c.numerator() for c in v])

    @cached_method
    def different(self):
        """
        Return the different ideal of the function field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.maximal_order()
            sage: O.different()
            Ideal (x^4 + 4*x^3 + 3*x^2 + 6*x + 4, y + 2*x^3 + x^2 + 6*x + 1)
            of Maximal order of Function field in y defined by y^4 + x*y + 4*x + 1
        """
        return ~self.codifferent()

    @cached_method
    def codifferent(self):
        """
        Return the codifferent ideal of the function field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.maximal_order()
            sage: O.codifferent()
            Ideal (1, (1/(x^4 + 4*x^3 + 3*x^2 + 6*x + 4))*y^3
            + ((5*x^3 + 6*x^2 + x + 6)/(x^4 + 4*x^3 + 3*x^2 + 6*x + 4))*y^2
            + ((x^3 + 2*x^2 + 2*x + 2)/(x^4 + 4*x^3 + 3*x^2 + 6*x + 4))*y
            + 6*x/(x^4 + 4*x^3 + 3*x^2 + 6*x + 4)) of Maximal order of Function field
            in y defined by y^4 + x*y + 4*x + 1
        """
        T  = self._codifferent_matrix()
        return self._ideal_from_vectors(T.inverse().columns())

    @cached_method
    def _codifferent_matrix(self):
        """
        Return the matrix `T` defined in Proposition 4.8.19 of [Coh1993]_.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(7)); R.<y> = K[]
            sage: L.<y> = K.extension(y^4 + x*y + 4*x + 1)
            sage: O = L.maximal_order()
            sage: O._codifferent_matrix()
            [      4       0       0     4*x]
            [      0       0     4*x 5*x + 3]
            [      0     4*x 5*x + 3       0]
            [    4*x 5*x + 3       0   3*x^2]
        """
        rows = []
        for u in self.basis():
            row = []
            for v in self.basis():
                row.append((u*v).trace())
            rows.append(row)
        T = matrix(rows)
        return T

    @cached_method
    def p_radical(self, prime):
        """
        Return the ``prime``-radical of the maximal order.

        INPUT:

        - ``prime`` -- prime ideal of the maximal order of the base
          rational function field

        The algorithm is outlined in Section 6.1.3 of [Coh1993]_.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<t> = K[]
            sage: F.<y> = K.extension(t^3 - x^2 * (x^2 + x + 1)^2)
            sage: o = K.maximal_order()
            sage: O = F.maximal_order()
            sage: p = o.ideal(x+1)
            sage: O.p_radical(p)
            Ideal (x + 1) of Maximal order of Function field in y
            defined by y^3 + x^6 + x^4 + x^2
        """
        g = prime.gens()[0]

        if not (g.denominator() == 1 and g.numerator().is_irreducible()):
            raise ValueError('not a prime ideal')

        F = self.function_field()
        n = F.degree()
        o = prime.ring()
        p = g.numerator()

        # Fp is isomorphic to the residue field o/p
        Fp, fr_Fp, to_Fp = o._residue_field_global(p)

        # exp = q^j should be at least extension degree where q is
        # the order of the residue field o/p
        q = F.constant_base_field().order()**p.degree()
        exp = q
        while exp <= F.degree():
            exp = exp**q

        # radical equals to the kernel of the map x |-> x^exp
        mat = []
        for g in self.basis():
            v = [to_Fp(c) for c in self._coordinate_vector(g**exp)]
            mat.append(v)
        mat = matrix(Fp,mat)
        ker = mat.kernel()

        # construct module generators of the p-radical
        vecs = []
        for i in range(n):
            v = vector([p if j == i else 0 for j in range(n)])
            vecs.append(v)
        for b in ker.basis():
            v = vector([fr_Fp(c) for c in b])
            vecs.append(v)

        return self._ideal_from_vectors(vecs)

    @cached_method
    def decomposition(self, ideal):
        """
        Return the decomposition of the prime ideal.

        INPUT:

        - ``ideal`` -- prime ideal of the base maximal order

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); R.<t> = K[]
            sage: F.<y> = K.extension(t^3 - x^2*(x^2 + x + 1)^2)
            sage: o = K.maximal_order()
            sage: O = F.maximal_order()
            sage: p = o.ideal(x+1)
            sage: O.decomposition(p)
            [(Ideal (x + 1, y + 1) of Maximal order
             of Function field in y defined by y^3 + x^6 + x^4 + x^2, 1, 1),
             (Ideal (x + 1, y^2 + y + 1) of Maximal order
             of Function field in y defined by y^3 + x^6 + x^4 + x^2, 2, 1)]
        """
        F = self.function_field()
        n = F.degree()

        p = ideal.gen().numerator()
        o = ideal.ring()

        # Fp is isomorphic to the residue field o/p
        Fp, fr, to = o._residue_field_global(p)
        P,X = Fp['X'].objgen()

        V = Fp**n # Ob = O/pO

        mtable = []
        for i in range(n):
            row = []
            for j in range(n):
                row.append(V([to(e) for e in self._mtable[i][j]]))
            mtable.append(row)

        if not p in self._kummer_places:
            #####################################
            # Decomposition by Kummer's theorem #
            #####################################
            gen = self._kummer_gen
            gen_vec_pow = self._kummer_gen_vec_pow
            mul_vecs = self._mul_vecs

            f = self._kummer_polynomial
            fp = P([to(c.numerator()) for c in f.list()])
            decomposition = []
            for q, exp in fp.factor():
                # construct O.ideal([p,q(gen)])
                gen_vecs = list(matrix.diagonal(n * [p]))
                c = q.list()

                # q(gen) in vector form
                qgen = sum(fr(c[i]) * gen_vec_pow[i] for i in range(len(c)))

                I = matrix.identity(o._ring, n)
                for i in range(n):
                    gen_vecs.append(mul_vecs(qgen,I[i]))
                prime = self._ideal_from_vectors_and_denominator(gen_vecs)

                # Compute an element beta in O but not in pO. How to find beta
                # is explained in Section 4.8.3 of [Coh1993]. We keep beta
                # as a vector over k[x] with respect to the basis of O.

                # p and qgen generates the prime; modulo pO, qgenb generates the prime
                qgenb = [to(qgen[i]) for i in range(n)]
                m =[]
                for i in range(n):
                    m.append(sum(qgenb[j] * mtable[i][j] for j in range(n)))
                beta  = [fr(c) for c in matrix(m).left_kernel().basis()[0]]

                prime._is_prime = True
                prime._prime_below = ideal
                prime._relative_degree = q.degree()
                prime._ramification_index = exp
                prime._beta = beta

                prime._kummer_form = (p, qgen)

                decomposition.append((prime, q.degree(), exp))
        else:
            #############################
            # Buchman-Lenstra algorithm #
            #############################
            pO = self.ideal(p)
            Ip = self.p_radical(ideal)
            Ob = matrix.identity(Fp, n)

            def bar(I): # transfer to O/pO
                m = []
                for v in I._hnf:
                    m.append([to(e) for e in v])
                h = matrix(m).echelon_form()
                return cut_last_zero_rows(h)

            def liftb(Ib):
                m = [vector([fr(e) for e in v]) for v in Ib]
                m += [v for v in pO._hnf]
                return self._ideal_from_vectors_and_denominator(m,1)

            def cut_last_zero_rows(h):
                i = h.nrows()
                while i > 0 and h.row(i-1).is_zero():
                    i -= 1
                return h[:i]

            def mul_vec(v1,v2):
                s = 0
                for i in range(n):
                    for j in range(n):
                        s += v1[i] * v2[j] * mtable[i][j]
                return s

            def pow(v, r): # r > 0
                m = v
                while r > 1:
                    m = mul_vec(m,v)
                    r -= 1
                return m

            # Algorithm 6.2.7 of [Coh1993]
            def div(Ib, Jb):
                # compute a basis of Jb/Ib
                sJb = Jb.row_space()
                sIb = Ib.row_space()
                sJbsIb,proj_sJbsIb,lift_sJbsIb = sJb.quotient_abstract(sIb)
                supplement_basis = [lift_sJbsIb(v) for v in sJbsIb.basis()]

                m = []
                for b in V.gens(): # basis of Ob = O/pO
                    b_row = [] # row vector representation of the map a -> a*b
                    for a in supplement_basis:
                        c = 0
                        for i in range(n):
                            for j in range(n):
                                c += a[i] * b[j] * mtable[i][j]
                        b_row += lift_sJbsIb(proj_sJbsIb(c))
                    m.append(b_row)
                return matrix(Fp,n,m).left_kernel().basis_matrix()

            # Algorithm 6.2.5 of [Coh1993]
            def mul(Ib, Jb):
                m = []
                for v1 in Ib:
                    for v2 in Jb:
                        m.append(mul_vec(v1,v2))
                h = matrix(m).echelon_form()
                return cut_last_zero_rows(h)

            def add(Ib,Jb):
                m = block_matrix([[Ib], [Jb]])
                h = m.echelon_form()
                return cut_last_zero_rows(h)

            # K_1, K_2, ...
            Lb = IpOb = bar(Ip+pO)
            Kb = [Lb]
            while not Lb.is_zero():
                Lb = mul(Lb,IpOb)
                Kb.append(Lb)

            # J_1, J_2, ...
            Jb =[Kb[0]] + [div(Kb[j],Kb[j-1]) for j in range(1,len(Kb))]

            # H_1, H_2, ...
            Hb = [div(Jb[j],Jb[j+1]) for j in range(len(Jb)-1)] + [Jb[-1]]

            q = Fp.order()

            def split(h):
                # VsW represents O/H as a vector space
                W = h.row_space() # H/pO
                VsW,to_VsW,lift_to_V = V.quotient_abstract(W)

                # compute the space K of elements in O/H that satisfy a^q-a=0
                l = [lift_to_V(b) for b in VsW.basis()]

                images = [to_VsW(pow(x, q) - x) for x in l]
                K = VsW.hom(images, VsW).kernel()

                if K.dimension() == 0:
                    return []
                if K.dimension() == 1: # h is prime
                    return [(liftb(h),VsW.dimension())] # relative degree

                # choose a such that a^q - a is 0 but a is not in Fp
                for a in K.basis():
                    # IMPORTANT: This criterion is based on the assumption
                    # that O.basis() starts with 1.
                    if a.support() != [0]:
                        break
                else:
                    raise AssertionError('No appropriate value found')

                a = lift_to_V(a)
                # compute the minimal polynomial of a
                m = [to_VsW(Ob[0])] # 1 in VsW
                apow = a
                while True:
                    v = to_VsW(apow)
                    try:
                        sol = matrix(m).solve_left(v)
                    except ValueError:
                        m.append(v)
                        apow = mul_vec(apow, a)
                        continue
                    break

                minpol = X**len(sol) - P(list(sol))

                # The minimal polynomial of a has only linear factors and at least two
                # of them. We set f to the first factor and g to the product of the rest.
                fac = minpol.factor()
                f = fac[0][0]
                g = (fac/f).expand()
                d,u,v = f.xgcd(g)

                assert d == 1, "Not relatively prime {} and {}".format(f,g)

                # finally, idempotent!
                e = lift_to_V(sum([c1*c2 for c1,c2 in zip(u*f,m)]))

                h1 = add(h, matrix([mul_vec(e,Ob[i]) for i in range(n)]))
                h2 = add(h, matrix([mul_vec(Ob[0]-e,Ob[i]) for i in range(n)]))

                return split(h1) + split(h2)

            decomposition = []
            for i in range(len(Hb)):
                index = i + 1 # Hb starts with H_1
                for prime, degree in split(Hb[i]):
                    # Compute an element beta in O but not in pO. How to find beta
                    # is explained in Section 4.8.3 of [Coh1993]. We keep beta
                    # as a vector over k[x] with respect to the basis of O.
                    m =[]
                    for i in range(n):
                        r = []
                        for g in prime._hnf:
                            r += sum(to(g[j]) * mtable[i][j] for j in range(n))
                        m.append(r)
                    beta = [fr(e) for e in matrix(m).left_kernel().basis()[0]]

                    prime._is_prime = True
                    prime._prime_below = ideal
                    prime._relative_degree = degree
                    prime._ramification_index = index
                    prime._beta = beta

                    decomposition.append((prime, degree, index))

        return decomposition

class FunctionFieldMaximalOrderInfinite(FunctionFieldMaximalOrder, FunctionFieldOrderInfinite):
    """
    Base class of maximal infinite orders of function fields.
    """
    def _repr_(self):
        """
        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order_infinite()
            Maximal infinite order of Rational function field in y over Rational Field

            sage: K.<x> = FunctionField(GF(2)); R.<t> = PolynomialRing(K)
            sage: F.<y> = K.extension(t^3-x^2*(x^2+x+1)^2)
            sage: F.maximal_order_infinite()
            Maximal infinite order of Function field in y defined by y^3 + x^6 + x^4 + x^2
        """
        return "Maximal infinite order of %s"%(self.function_field(),)

class FunctionFieldMaximalOrderInfinite_rational(FunctionFieldMaximalOrderInfinite):
    """
    Maximal infinite orders of rational function fields.
    """
    def __init__(self, field, category=None):
        """
        Initialize.

        INPUT:

        - ``field`` -- function field

        EXAMPLES::

            sage: K.<t> = FunctionField(GF(19)); K
            Rational function field in t over Finite Field of size 19
            sage: R = K.maximal_order_infinite(); R
            Maximal infinite order of Rational function field in t over Finite Field of size 19
        """
        FunctionFieldOrderInfinite.__init__(self, field,
                                            category=category or PrincipalIdealDomains())
        self._populate_coercion_lists_(coerce_list=[field.constant_base_field()])

    def basis(self):
        """
        Return the basis (=1) of the order as a module over the polynomial ring.

        EXAMPLES::

            sage: K.<t> = FunctionField(GF(19))
            sage: O = K.maximal_order()
            sage: O.basis()
            (1,)
            sage: parent(O.basis()[0])
            Maximal order of Rational function field in t over Finite Field of size 19
        """
        return 1/self.function_field().gen()

    def prime_ideal(self):
        """
        Return the unique prime ideal of the order.

        EXAMPLES::

            sage: K.<t> = FunctionField(GF(19))
            sage: O = K.maximal_order_infinite()
            sage: O.prime_ideal()
            Ideal (1/t) of Maximal infinite order of Rational function field in t
            over Finite Field of size 19
        """
        return self.ideal( 1/self.function_field().gen() )

    def ideal(self, *gens):
        """
        Return the fractional ideal generated by ``gens``.

        INPUT:

        - ``gens`` -- elements of the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(QQ)
            sage: O = K.maximal_order_infinite()
            sage: O.ideal(x)
            Ideal (x) of Maximal infinite order of Rational function field in x over Rational Field
            sage: O.ideal([x,1/x]) == O.ideal(x,1/x) # multiple generators may be given as a list
            True
            sage: O.ideal(x^3+1,x^3+6)
            Ideal (x^3) of Maximal infinite order of Rational function field in x over Rational Field
            sage: I = O.ideal((x^2+1)*(x^3+1),(x^3+6)*(x^2+1)); I
            Ideal (x^5) of Maximal infinite order of Rational function field in x over Rational Field
            sage: O.ideal(I)
            Ideal (x^5) of Maximal infinite order of Rational function field in x over Rational Field
        """
        if len(gens) == 1:
            gens = gens[0]
            if not isinstance(gens, (list, tuple)):
                if is_Ideal(gens):
                    gens = gens.gens()
                else:
                    gens = (gens,)
        K = self.function_field()
        gens = [K(g) for g in gens]
        try:
            d = max(g.numerator().degree() - g.denominator().degree() for g in gens if g != 0)
            gen = K.gen() ** d
        except ValueError: # all gens are zero
            gen = K(0)
        return FunctionFieldIdealInfinite_rational(self, gen)

    def gen(self, n=0):
        """
        Return the ``n``-th generator of self. Since there is only one generator ``n`` must be 0.

        EXAMPLES::

            sage: O = FunctionField(QQ,'y').maximal_order()
            sage: O.gen()
            y
            sage: O.gen(1)
            Traceback (most recent call last):
            ...
            IndexError: Only one generator.
        """
        if n != 0: raise IndexError("Only one generator.")
        return self._gen

    def ngens(self):
        """
        Return 1 the number of generators of the order.

        EXAMPLES::

            sage: FunctionField(QQ,'y').maximal_order().ngens()
            1
        """
        return 1

    def _element_constructor_(self, f):
        """
        Make ``f`` an element of this order.

        EXAMPLES::

            sage: K.<y> = FunctionField(QQ)
            sage: O = K.maximal_order()
            sage: O._element_constructor_(y)
            y
            sage: O._element_constructor_(1/y)
            Traceback (most recent call last):
            ...
            TypeError: 1/y is not an element of Maximal order of Rational function field in y over Rational Field
        """
        if not f.parent() is self.function_field():
            f = self.function_field()(f)
        f = f.element()
        if f.denominator().degree() < f.numerator().degree():
            raise TypeError("%r is not an element of %r"%(f,self))
        from .element import FunctionFieldElement_rational
        return FunctionFieldElement_rational(self, f)

class FunctionFieldMaximalOrderInfinite_global(FunctionFieldMaximalOrderInfinite):
    """
    Maximal infinite orders of global function fields.
    """
    def __init__(self, field, basis):
        """
        Initialize.

        INPUT:

        - ``field`` -- function field

        - ``basis`` -- list of elements of the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<t> = PolynomialRing(K)
            sage: F.<y> = K.extension(t^3-x^2*(x^2+x+1)^2)
            sage: F.maximal_order_infinite()
            Maximal infinite order of Function field in y defined by y^3 + x^6 + x^4 + x^2

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: L.maximal_order_infinite()
            Maximal infinite order of Function field in y defined by y^2 + y + (x^2 + 1)/x
        """
        FunctionFieldOrderInfinite.__init__(self, field)

        V, fr, to = field.vector_space()
        R = field.base_field().maximal_order_infinite()

        self._basis = tuple(basis)
        self._module = V.span_of_basis([to(v) for v in basis])
        self._module_base_ring = R
        self._to_module = to

    def _element_constructor_(self, f):
        """
        Make ``f`` an element of this order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: Oinf.basis()
            (1, 1/x*y)
            sage: 1 in Oinf
            True
            sage: 1/x*y in Oinf
            True
            sage: x*y in Oinf
            False
            sage: 1/x in Oinf
            True
        """
        if not f.parent() is self.function_field():
            f = self.function_field()(f)

        oinf = self.function_field().base_field().maximal_order_infinite()
        coordinates = self.coordinate_vector(f)
        if not all(c in oinf for c in coordinates):
            raise TypeError("%r is not an element of %r"%(f,self))
        return f

    def basis(self):
        """
        Return a basis of this order as a module over the maximal order
        of the base function field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<t> = K[]
            sage: L.<y> = K.extension(t^3 - x^2*(x^2 + x + 1)^2)
            sage: Oinf = L.maximal_order_infinite()
            sage: Oinf.basis()
            (1, 1/x^2*y, (1/(x^4 + x^3 + x^2))*y^2)

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: Oinf.basis()
            (1, 1/x*y)
        """
        return self._basis

    def ideal(self, *gens):
        """
        Return the ideal generated by ``gens``.

        INPUT:

        - ``gens`` -- tuple of elements of the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<t> = K[]
            sage: F.<y> = K.extension(t^3 - x^2*(x^2 + x + 1)^2)
            sage: Oinf = F.maximal_order_infinite()
            sage: I = Oinf.ideal(x,y); I
            Ideal (x^2) of Maximal infinite order of Function field
            in y defined by y^3 + x^6 + x^4 + x^2

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: I = Oinf.ideal(x,y); I
            Ideal (x) of Maximal infinite order of Function field in y defined by y^2 + y + (x^2 + 1)/x
        """
        if len(gens) == 1:
            gens = gens[0]
            if not type(gens) in (list,tuple):
                gens = (gens,)
        mgens = [g * b for g in gens for b in self._basis]
        return self.ideal_with_gens_over_base(mgens)

    def ideal_with_gens_over_base(self, gens):
        """
        Return the ideal generated by ``gens`` as a module.

        INPUT:

        - ``gens`` -- tuple of elements of the function field

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); R.<t> = K[]
            sage: F.<y> = K.extension(t^3 - x^2*(x^2 + x + 1)^2)
            sage: Oinf = F.maximal_order_infinite()
            sage: Oinf.ideal_with_gens_over_base((x^2, y, (1/(x^2 + x + 1))*y^2))
            Ideal (x^2) of Maximal infinite order of Function field in y
            defined by y^3 + x^6 + x^4 + x^2
        """
        F = self.function_field()
        iF, from_iF, to_iF = F._inversion_isomorphism()
        iO = iF.maximal_order()

        ideal = iO.ideal_with_gens_over_base([to_iF(g) for g in gens])

        if not ideal.is_zero():
            # Now the ideal does not correspond exactly to the ideal in the
            # maximal infinite order through the inversion isomorphism. The
            # reason is that the ideal also has factors not lying over x.
            # The following procedure removes the spurious factors. The idea
            # is that for an integral ideal I, J_n = I + (xO)^n stabilizes
            # if n is large enough, and then J_n is the I with the spurious
            # factors removed. For a fractional ideal, we also need to find
            # the largest factor x^m that divides the denominator.
            d = ideal.denominator()
            h = ideal.hnf()
            x = d.parent().gen()

            # find the largest factor x^m that divides the denominator
            i = 0
            while d[i].is_zero():
                i += 1
            d = x ** i

            # find the largest n such that I + (xO)^n stabilizes
            h1 = h
            MS = h1.matrix_space()
            k = MS.identity_matrix()
            while True:
                k = x * k

                h2 = block_matrix([[h],[k]])
                h2.reverse_rows_and_columns()
                h2._hermite_form_euclidean(normalization=lambda p: ~p.lc())
                h2.reverse_rows_and_columns()
                i = 0
                while i < h2.nrows() and h2.row(i).is_zero():
                    i += 1
                h2 = h2[i:] # remove zero rows

                if h2 == h1:
                    break
                h1 = h2

            # reconstruct ideal
            ideal = iO._ideal_from_vectors_and_denominator(list(h1), d)

        return FunctionFieldIdealInfinite_global(self, ideal)

    def _to_iF(self, I):
        """
        Return the ideal in the inverted function field from ``I``.

        INPUT:

        - ``I`` -- ideal of the function field

        EXAMPLES::

            sage: K.<x>=FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y>=K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: I = Oinf.ideal(y)
            sage: Oinf._to_iF(I)
            Ideal (1, 1/x*s) of Maximal order of Function field in s
            defined by s^2 + x*s + x^3 + x
        """
        F = self.function_field()
        iF,from_iF,to_iF = F._inversion_isomorphism()
        iO = iF.maximal_order()
        iI = iO.ideal_with_gens_over_base([to_iF(b) for b in I.gens_over_base()])
        return iI

    def decomposition(self):
        """
        Return prime ideal decomposition of `pO_\infty` where `p` is the unique
        prime ideal of the maximal infinite order of the rational function field.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<t> = K[]
            sage: F.<y> = K.extension(t^3 - x^2*(x^2 + x + 1)^2)
            sage: Oinf = F.maximal_order_infinite()
            sage: Oinf.decomposition()
            [(Ideal (1/x,1/x^2*y + 1) of Maximal infinite order
             of Function field in y defined by y^3 + x^6 + x^4 + x^2, 1, 1),
             (Ideal (1/x,1/x^4*y^2 + 1/x^2*y + 1) of Maximal infinite order
             of Function field in y defined by y^3 + x^6 + x^4 + x^2, 2, 1)]

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: Oinf.decomposition()
            [(Ideal (1/x,1/x*y) of Maximal infinite order of Function field in y
            defined by y^2 + y + (x^2 + 1)/x, 1, 2)]
        """
        F = self.function_field()
        K = F.base_field()
        iF,from_iF,to_iF = F._inversion_isomorphism()

        x = iF.base_field().gen()
        iO = iF.maximal_order()
        io = iF.base_field().maximal_order()
        ip = io.ideal(x)

        dec = []
        for iprime, deg, exp in iO.decomposition(ip):
            prime = FunctionFieldIdealInfinite_global(self, iprime)
            dec.append((prime, deg, exp))
        return dec

    def different(self):
        """
        Return the different ideal of the maximal infinite order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: Oinf.different()
            Ideal (1/x) of Maximal infinite order of Function field in y
            defined by y^2 + y + (x^2 + 1)/x
        """
        T = self._codifferent_matrix()
        codiff_gens = []
        for c in T.inverse().columns():
            codiff_gens.append(sum([ci*bi for ci,bi in zip(c,self.basis())]))
        codiff = self.ideal_with_gens_over_base(codiff_gens)
        return ~codiff

    @cached_method
    def _codifferent_matrix(self):
        """
        Return the codifferent matrix of the maximal infinite order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: Oinf._codifferent_matrix()
            [    0   1/x]
            [  1/x 1/x^2]
        """
        rows = []
        for u in self.basis():
            row = []
            for v in self.basis():
                row.append((u*v).trace())
            rows.append(row)
        T = matrix(rows)
        return T

    def coordinate_vector(self, e):
        """
        Return the cooridinates of ``e`` with respect to the basis of the order.

        INPUT:

        - ``e`` -- element of the function field

        The returned coordinates are in the base maximal infinite order if and only
        if the element is in the order.

        EXAMPLES::

            sage: K.<x> = FunctionField(GF(2)); _.<Y> = K[]
            sage: L.<y> = K.extension(Y^2 + Y + x + 1/x)
            sage: Oinf = L.maximal_order_infinite()
            sage: f = 1/y^2
            sage: f in Oinf
            True
            sage: Oinf.coordinate_vector(f)
            ((x^3 + x^2 + x)/(x^4 + 1), x^3/(x^4 + 1))
        """
        return self._module.coordinate_vector(self._to_module(e))
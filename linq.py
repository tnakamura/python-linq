# -*- coding: utf-8 -*-

__author__ = "tnakamura"
__copyright__ = "Copyright (c) 2011 tnakamura"
__credits__ = ["tnakamura"]
__license__ = "BSD"
__version__ = "0.1.0"
__maintainer__ = "tnakamura"

def _default_predicate(value):
    return True

def _require_not_none(value, name):
    if value is None:
        raise ValueError(name)

def _require_callable(value, name):
    if not callable(value):
        raise ValueError(name)

def _require_greater_or_equal(expt, value, name):
    if value < expt:
        raise ValueError(name)

class Enumerable(object):
    def __init__(self, source):
        self._source = (v for v in source)

    def __iter__(self):
        return self._source

    def next(self):
        return self._source.next()

    @classmethod
    def range(cls, start, count):
        """
        >>> list(Enumerable.range(1, 5))
        [1, 2, 3, 4, 5]
        """
        return cls(range(start, start + count))

    @classmethod
    def repeat(cls, result, count):
        """
        >>> list(Enumerable.repeat(7, 3))
        [7, 7, 7]
        """
        _require_greater_or_equal(0, count, "count")
        return cls((result for i in range(0, count)))

    @classmethod
    def empty(cls):
        """
        >>> list(Enumerable.empty())
        []
        """
        return cls([])

    def element_at(self, index):
        """
        >>> Enumerable([1,2,3,4,5]).element_at(0)
        1
        >>> Enumerable([1,2,3,4,5]).element_at(4)
        5
        >>> Enumerable([1,2,3,4,5]).element_at(-1)
        Traceback (most recent call last):
            ...
        ValueError: index
        >>> Enumerable([1,2,3,4,5]).element_at(5)
        Traceback (most recent call last):
            ...
        ValueError: index
        """
        _require_greater_or_equal(0, index, "index")
        for i, v in enumerate(self):
            if i == index:
                return v
        raise ValueError("index")

    def element_at_or_default(self, index):
        """
        >>> Enumerable([1,2,3,4,5]).element_at_or_default(0)
        1
        >>> Enumerable([1,2,3,4,5]).element_at_or_default(4)
        5
        >>> Enumerable([1,2,3,4,5]).element_at_or_default(-1) is None
        True
        >>> Enumerable([1,2,3,4,5]).element_at_or_default(5) is None
        True
        """
        if index < 0:
            return None
        for i, v in enumerate(self):
            if i == index:
                return v
        return None

    def first(self, predicate=_default_predicate):
        """
        >>> Enumerable([1,2,3,4,5]).first()
        1
        >>> Enumerable([1,2,3,4,5]).first(lambda x: x % 2 == 0)
        2
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")
        for v in self:
            if predicate(v):
                return v
        raise ValueError()

    def first_or_default(self, predicate=_default_predicate):
        """
        >>> Enumerable([1,2,3,4,5]).first_or_default()
        1
        >>> Enumerable([1,2,3,4,5]).first_or_default(lambda x: x % 2 == 0)
        2
        >>> Enumerable([1,2,3,4,5]).first_or_default(lambda x: 10 < x) is None
        True
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")
        for v in self:
            if predicate(v):
                return v
        return None

    def single(self, predicate=_default_predicate):
        """
        >>> Enumerable([1]).single()
        1
        >>> Enumerable([1,2,3,4,5]).single(lambda x: x == 3)
        3
        >>> Enumerable([1,2,3,4,5]).single(lambda x: x == 100)
        Traceback (most recent call last):
            ...
        ValueError: predicate
        >>> Enumerable([1,2,3,4,5]).single(lambda x: x % 2 == 0)
        Traceback (most recent call last):
            ...
        ValueError: predicate
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")

        single_value = None
        is_matched = False
        for v in self:
            if predicate(v):
                if is_matched:
                    raise ValueError("predicate")
                single_value = v 
                is_matched = True

        if not is_matched:
            raise ValueError("predicate")
        return single_value

    def single_or_default(self, predicate=_default_predicate):
        """
        >>> Enumerable([1]).single_or_default()
        1
        >>> Enumerable([1,2,3,4,5]).single_or_default(lambda x: x == 3)
        3
        >>> Enumerable([1,2,3,4,5]).single_or_default(lambda x: x == 100) is None
        True
        >>> Enumerable([1,2,3,4,5]).single_or_default(lambda x: x % 2 == 0)
        Traceback (most recent call last):
            ...
        ValueError: predicate
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")

        single_value = None
        is_matched = False
        for v in self:
            if predicate(v):
                if is_matched:
                    raise ValueError("predicate")
                single_value = v 
                is_matched = True

        if not is_matched:
            return None
        else:
            return single_value

    def select(self, selector):
        """
        >>> list(Enumerable([1,2,3,4,5]).select(lambda x: x * 2))
        [2, 4, 6, 8, 10]
        """
        _require_not_none(selector, "selector")
        _require_callable(selector, "selector")
        return self.__class__((selector(v) for v in self))

    def where(self, predicate):
        """
        >>> list(Enumerable([1,2,3,4,5]).where(lambda x: x % 2 == 1))
        [1, 3, 5]
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")
        return self.__class__((v for v in self if predicate(v)))

    def skip(self, count):
        """
        >>> list(Enumerable([1,2,3,4,5]).skip(3))
        [4, 5]
        >>> list(Enumerable([1,2,3,4,5]).skip(5))
        []
        """
        _require_greater_or_equal(0, count, "count")
        def iter():
            for i, v in enumerate(self):
                if i < count:
                    continue
                yield v
        return self.__class__(iter())

    def take(self, count):
        """
        >>> list(Enumerable([1,2,3,4,5]).take(3))
        [1, 2, 3]
        >>> list(Enumerable([1,2,3,4,5]).take(5))
        [1, 2, 3, 4, 5]
        >>> list(Enumerable([1,2,3,4,5]).take(6))
        [1, 2, 3, 4, 5]
        """
        _require_greater_or_equal(0, count, "count")
        def iter():
            for i, v in enumerate(self):
                if i < count:
                    yield v
        return self.__class__(iter())

    def skip_while(self, predicate):
        """
        >>> list(Enumerable([1,2,3,4,5]).skip_while(lambda x: x < 3))
        [3, 4, 5]
        >>> list(Enumerable([1,2,3,4,5]).skip_while(lambda x: x < 10))
        []
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")
        def iter():
            for v in self:
                if predicate(v):
                    continue
                yield v
        return self.__class__(iter())

    def take_while(self, predicate):
        """
        >>> list(Enumerable([1,2,3,4,5]).take_while(lambda x: x < 3))
        [1, 2]
        >>> list(Enumerable([1,2,3,4,5]).take_while(lambda x: 10 < x))
        []
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")
        def iter():
            for v in self:
                if predicate(v):
                    yield v
                else:
                    return
        return self.__class__(iter())

    def all(self, predicate):
        """
        >>> Enumerable([1,2,3,4,5]).all(lambda x: x < 6)
        True
        >>> Enumerable([1,2,3,4,5]).all(lambda x: x % 2 == 2)
        False
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")
        for v in self:
            if not predicate(v):
                return False
        return True

    def any(self, predicate):
        """
        >>> Enumerable([1,2,3,4,5]).any(lambda x: x < 6)
        True
        >>> Enumerable([1,2,3,4,5]).any(lambda x: x % 2 == 0)
        True
        >>> Enumerable([1,2,3,4,5]).any(lambda x: 5 < x)
        False
        """
        _require_not_none(predicate, "predicate")
        _require_callable(predicate, "predicate")
        for v in self:
            if predicate(v):
                return True
        return False

    def run(self, callable):
        _require_not_none(callable, "callable")
        _require_callable(callable, "callable")
        for v in self:
            callable(v)
    
    def count(self):
        """
        >>> Enumerable([1,2,3,4,5]).count()
        5
        """
        c = 0
        for v in self:
            c += 1
        return c

    def reverse(self):
        """
        >>> list(Enumerable([1,2,3,4,5]).reverse())
        [5, 4, 3, 2, 1]
        """
        lst = list(self)
        lst.reverse()
        return Enumerable((v for v in lst))

    def select_many(self, selector):
        """
        >>> list(Enumerable([1,2,3]).select_many(lambda x: range(1,x+1)))
        [1, 1, 2, 1, 2, 3]
        """
        def iter():
            for v in self:
                for v2 in selector(v):
                    yield v2
        return Enumerable(iter())

    def to_list(self):
        """
        >>> Enumerable([1,2,3,4,5]).to_list()
        [1, 2, 3, 4, 5]
        """
        return list(self)

    def group_by(self, key_selector):
        _require_not_none(key_selector, "key_selector")
        _require_callable(key_selector, "key_selector")
        groups = {}
        for v in self:
            key = key_selector(v)
            if not key in groups:
                groups[key] = []
            groups[key].append(v)
        return groups

    def join(self, inner, outer_key_selector, inner_key_selector, result_selector):
        _require_not_none(outer_key_selector, "outer_key_selector")
        _require_not_none(inner_key_selector, "inner_key_selector")
        _require_not_none(result_selector, "result_selector")

        def iter():
            for outer_value in self:
                outer_key = outer_key_selector(outer_value)
                for inner_value in inner:
                    inner_key = inner_key_selector(inner_value)
                    if outer_key == inner_key:
                        yield result_selector(outer_value, inner_value)
        return Enumerable(iter())

if __name__ == '__main__':
    import doctest
    doctest.testmod()

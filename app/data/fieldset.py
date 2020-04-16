class EntityFields:
    def __init__(self, fields, ctor, table=None):
        self.fields = fields
        self.ctor = ctor
        self.table = table

    def __call__(self, table):
        return EntityFields(self.fields, self.ctor, table)

    def __str__(self):
        return ', '.join(f'{self.table}.{f}' for f in self.fields)

    def unpack(self, fields):
        if not fields:
            return None
        if self.ctor:
            return self.ctor(*fields)
        return fields

    def unpack_iter(self, it):
        return map(self.unpack, it)


class FieldSet:
    def __init__(self, *sets):
        self.sets = sets
        self.constructor = None

    def __str__(self):
        return ', '.join(str(s) for s in self.sets)

    def unpack_entities(self, t):
        start = 0
        for s in self.sets:
            stop = start + len(s.fields)
            yield s.unpack(t[start:stop])
            start = stop

    def unpack(self, t):
        if not t:
            return None
        entities = self.unpack_entities(t)
        if self.constructor:
            return self.constructor(*entities)
        return tuple(entities)

    def unpack_iter(self, it):
        return map(self.unpack, it)

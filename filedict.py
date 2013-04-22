"""filedict.py
a Persistent Dictionary in Python

Author: Erez Shinan
Date  : 31-May-2009
"""

from collections import UserDict
import pickle
import sqlite3
import hashlib
import threading

class FileDict(UserDict):
    """A dictionary that stores its data persistantly in a file

    Options:
        filename - which file to use
        table - which table name to use for storing data (default: 'dict')

    """

    def __init__(self, filename=None, **options):
        if not filename:
            raise ValueError("Must provide 'connection' or 'filename'")
        self._filename = filename

        self._connections = dict()
        conn = self._conn

        self._tablename = options.pop('table', 'dict')

        self._nocommit = False

        assert not options, "Unrecognized options: %s" % options

        self._execute('CREATE TABLE IF NOT EXISTS %s (id integer primary key, hash integer, key blob, value blob);'%self._tablename)
        self._execute('CREATE INDEX IF NOT EXISTS %s_index ON %s(hash);' % (self._tablename, self._tablename))
        self._commit()

    @property
    def _conn(self):
        try:
            return self._connections[threading.current_thread().ident]
        except KeyError:
            self._connections[threading.current_thread().ident] = sqlite3.connect(self._filename)
            return self._connections[threading.current_thread().ident]

    def _execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    def _commit(self):
        if self._nocommit:
            return

        self._conn.commit()

    def __pack(self, value):
        return pickle.dumps(value, 3)
    def __unpack(self, value):
        return pickle.loads(value)

    def __hash(self, data):
        binary_data = self.__pack(data)
        hash = int(hashlib.md5(binary_data).hexdigest(),16)
        # We need a 32bit hash:
        return hash % 0x7FFFFFFF

    def __get_id(self, key):
        cursor = self._execute('SELECT key,id FROM %s WHERE hash=?;'%self._tablename, (self.__hash(key),))
        for k,id in cursor:
            if self.__unpack(k) == key:
                return id

        raise KeyError(key)

    def __getitem__(self, key):
        cursor = self._execute('SELECT key,value FROM %s WHERE hash=?;'%self._tablename, (self.__hash(key),))
        for k,v in cursor:
            if self.__unpack(k) == key:
                return self.__unpack(v)

        raise KeyError(key)

    def __setitem(self, key, value):
        value_pickle = self.__pack(value)

        try:
            id = self.__get_id(key)
            cursor = self._execute('UPDATE %s SET value=? WHERE id=?;'%self._tablename, (value_pickle, id) )
        except KeyError:
            key_pickle = self.__pack(key)
            cursor = self._execute('INSERT INTO %s (hash, key, value) values (?, ?, ?);'
                    %self._tablename, (self.__hash(key), key_pickle, value_pickle) )

        assert cursor.rowcount == 1

    def __setitem__(self, key, value):
        self.__setitem(key, value)
        self._commit()

    def __delitem__(self, key):
        id = self.__get_id(key)
        cursor = self._execute('DELETE FROM %s WHERE id=?;'%self._tablename, (id,))
        if cursor.rowcount <= 0:
            raise KeyError(key)

        self._commit()


    def update(self, d):
        for k,v in d.items():
            self.__setitem(k, v)
        self._commit()

    def __iter__(self):
        return (self.__unpack(x[0]) for x in self._execute('SELECT key FROM %s;'%self._tablename) )
    def keys(self):
        return iter(self)
    def values(self):
        return (self.__unpack(x[0]) for x in self._execute('SELECT value FROM %s;'%self._tablename) )
    def items(self):
        return (list(map(self.__unpack, x)) for x in self._execute('SELECT key,value FROM %s;'%self._tablename) )

    def __contains__(self, key):
        try:
            self.__get_id(key)
            return True
        except KeyError:
            return False

    def __len__(self):
        return self._execute('SELECT COUNT(*) FROM %s;' % self._tablename).fetchone()[0]

    def __del__(self):
        try:
            self._conn
        except AttributeError:
            pass
        else:
            self._commit()

    @property
    def batch(self):
        return self._Batch(self)

    class _Batch:
        def __init__(self, d):
            self.__d = d

        def __enter__(self):
            self.__old_nocommit = self.__d._nocommit
            self.__d._nocommit = True
            return self.__d

        def __exit__(self, type, value, traceback):
            self.__d._nocommit = self.__old_nocommit
            self.__d._commit()
            return True


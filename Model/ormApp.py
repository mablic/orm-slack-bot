from datetime import datetime
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging


def conn_pool(kw):
    logging.info('create database connection pool...')
    global __pool
    global __conn
    conn = URL(**kw)
    engine = create_engine(conn)
    __pool = sessionmaker(bind=engine)
    __conn = engine.connect()


def conn_sql():
    user_connection = {
        'drivername': 'mysql+mysqlconnector',
        'username': 'root',
        'password': '123456789',
        'host': 'localhost',
        'port': '3306',
        'database': 'google_search'
    }
    try:
        conn_pool(user_connection)
    except KeyError:
        print('Connection key error')


def log(sql, msg=None):
    logging.info(msg + sql)


def select_function(sql, args=None):
    log(sql, 'execute args ' + args)
    global __conn
    conn_sql()
    output = __conn.execute(sql)
    __conn.close()
    return output


def execute_function(sql, kwargs, args=None):
    log(sql, 'execute args ' + args)
    global __conn
    conn_sql()
    __conn.execute(sql.replace('?', '%s'), kwargs)
    __conn.close()

class Field(object):

    def __init__(self, name, col_type):
        self.name = name
        self.column_type = col_type

    def __str__(self):
        return '<%s, %s>' % (self.__class__.__name__, self.name)

    __repr__ = __str__


class StringField(Field):

    def __init__(self, name):
        super(StringField, self).__init__(name, 'varchar(50)')


class IntegerField(Field):

    def __init__(self, name):
        super(IntegerField, self).__init__(name, 'bigint')


class DateField(Field):

    def __init__(self, name):
        super(DateField, self).__init__(name, 'date')


class Modelmetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        all_columns = dict()
        fields = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                all_columns[k] = v
                fields.append(v.name)
        for key in all_columns.keys():
            attrs.pop(key)
        attrs['__columns__'] = all_columns
        attrs['__table__'] = name
        attrs['__select__'] = 'select * from %s' % name  # where name = "?";'
        attrs['__insert__'] = 'insert into %s (%s) values (%s)' %  \
            (name, ', '.join(fields), ', '.join(['?' for _ in range(len(fields))]))
        attrs['__delete__'] = 'delete from %s ' % name
        attrs['__findAll__'] = 'select * from %s' % name
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=Modelmetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('Key %s do not exist.' % item)

    @classmethod
    def select(cls, where=None, args=None):
        sql = cls.__select__
        if where:
            sql += ' where '
            sql += where
            if args:
                sql += ' = '
                sql += '"%s"' % args
        rs = select_function(sql, 'Select')
        return [x for x in rs]

    @classmethod
    def insert(cls, *kwargs):
        sql = cls.__insert__
        execute_function(sql, kwargs, 'Insert')

    @classmethod
    def delete(cls, where, args=None):
        sql = cls.__delete__
        if where:
            sql += ' where '
            sql += where
            sql += ' =?'
        else:
            raise ValueError('please pass where statement for deletion.')
        execute_function(sql, (args,), 'Delete')


class Users(Model):
    name = StringField('name')
    keyword = StringField('keyword')
    dateval = DateField('datetime')


if __name__ == '__main__':

    user_connection = {
        'drivername': 'mysql+mysqlconnector',
        'username' : 'root',
        'password': '123456789',
        'host': 'localhost',
        'port': '3306',
        'database': 'google_search'
    }
    try:
        conn_pool(user_connection)
    except KeyError:
        print('Connection key error')

    user = Users(name='mike', keyword='test', dateval=datetime.now().strftime('%a, %b %d %H:%M'))
    Users.select('name', 'MikeH')
    Users.insert('MikeH', 'test', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    Users.delete('name', 'Mike')




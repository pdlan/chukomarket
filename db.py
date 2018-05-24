from peewee import *

db = SqliteDatabase('market.db')

TYPE_NAME = ['书籍', '日用品', '电子设备', '其他']

class User(Model):
    id_ = PrimaryKeyField()
    name = CharField()
    student_id = CharField()
    phone = CharField()
    is_admin = BooleanField()
    has_registered = BooleanField()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return str(self.id_)

    class Meta:
        database = db

class Item(Model):
    id_ = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='item')
    type_ = IntegerField()
    name = CharField()
    detail = CharField()
    img_filename = CharField()
    price = DecimalField()
    has_saled = BooleanField()
    sale_self = BooleanField()
    will_take_back = BooleanField()
    is_deleted = BooleanField()
    has_given_staff = BooleanField()

    class Meta:
        database = db
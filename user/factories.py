# from copy import deepcopy
# from .models import User
# import factory
# from faker import Faker
#
# fake = Faker()
#
#
# class UserFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = User()
#
#     email = factory.Faker('email')
#     first_name = factory.Faker('first_name')
#     last_name = factory.Faker('last_name')
#     password = factory.Faker('password')
#
#     @classmethod
#     def _create(cls, model_class, *args, **kwargs):
#         manager = model_class._default_manager
#         instance = manager.create_user(*args, **kwargs)
#         return instance
#
#
# class SuperUserFactory(UserFactory):
#     is_staff = True
#     is_superuser = True
#     is_active = True
#
#     @classmethod
#     def _create(cls, model_class, *args, **kwargs):
#         manager = model_class._default_manager
#         instance = manager.create_superuser(*args, **kwargs)
#         return

import factory

from django.utils import timezone

from apps.accounts.models import User, BillingAddress, Payment, FAQs, USER_TYPES

roles, verbose_names = zip(*USER_TYPES)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Faker('email')
    user_name = factory.Faker('user_name')
    verification_token = factory.Faker('uuid4')
    token_creation_date = factory.LazyFunction(timezone.now)
    is_active = factory.Faker('boolean')
    date_joined = factory.LazyFunction(timezone.now)
    role = factory.Faker('word', ext_word_list=list(roles))
    mobile_number = factory.Faker('phone_number')
    is_staff = factory.Faker('boolean')
    password = factory.Faker('password')


class BillingAddressFactory(factory.DjangoModelFactory):
    user = factory.RelatedFactory(UserFactory)
    address = factory.Faker('address')
    city = factory.Faker('city')
    state = factory.Faker('state')
    country = factory.Faker('country')
    zip_code = factory.Faker('zipcode')
    default = factory.Faker('boolean')

    class Meta:
        model = BillingAddress


class PaymentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Payment


class FAQsFactory(factory.DjangoModelFactory):
    question = factory.Faker('word')
    answer = factory.Faker('word')

    class Meta:
        model = FAQs



import os
from pprint import pprint

from django.db.models import F, OuterRef, Q, Subquery, Sum

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thriftease_api.settings")

# Initialize the Django application
import django

django.setup()


from accounts.models import Account
from transactions.models import Transaction

Q
F
OuterRef
Subquery
Sum

Ac = Account
Tr = Transaction
obs = Tr.objects
# flt = Q(account=F("account")) & (Q(datetime__lte=F("datetime")) & ~Q(pk__lt=F("pk")))


# qry = (
#     obs.order_by("datetime", "id")
#     .alias(
#         old_account_balance=Sum(
#             "amount",
#             filter=flt,
#             default=Decimal("0.00"),
#         )
#     )
#     .annotate(old_account_balance=F("old_account_balance"))
# )
# # pprint(str(qry.query))
# # print()
# # print()
# # print(qry.values())
# print(obs.filter(flt))

# first = Account.objects.first()
# if first:
#     pprint(list(first.transaction_set.all().values()))
# print()
# last = obs.values().last()
# print(
#     Transaction.objects.filter(
#         Q(account=F("account")) & (Q(datetime__lte=F("datetime")) & (~Q(pk=F("pk")) | Q(p)))
#     )
# )

# subquery = (
#     Transaction.objects.filter(
#         Q(account=OuterRef("account"), datetime__lt=OuterRef("datetime"))
#         | Q(datetime=OuterRef("datetime"), id__lt=OuterRef("id"))
#     )
#     .order_by("datetime", "id")
#     .values("amount")
#     .annotate(old_account_balance=Sum("amount"))
#     .values("old_account_balance")[:1]
# )

# result = Transaction.objects.annotate(old_account_balance=Subquery(subquery))

# print(result.query)
# qry = Transaction.objects.raw(
#     """
# SELECT
#   id,
#   account_id,
#   amount,
#   datetime,
#   (
#     SELECT
#       SUM(amount)
#     FROM
#       transactions_transaction AS t2
#     WHERE
#       (
#         t2.account_id = t1.account_id
#         AND t2.datetime < t1.datetime
#       )
#       OR (
#         t2.datetime = t1.datetime
#         AND t2.id != t1.id
#         AND t2.id < t1.id
#       )
#     ORDER BY
#       t2.datetime,
#       t2.id
# ) AS old_account_balance
# FROM
#   transactions_transaction AS t1
# ORDER BY
#     t1.datetime,
#     t1.id
# """
# )
pprint(Transaction.objects.values()[2])

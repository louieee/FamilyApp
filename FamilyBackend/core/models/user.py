from itertools import chain

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models


# Create your models here.


class Gender(models.TextChoices):
    Male = ("Male", "Male")
    Female = ("Female", "Female")


class Couple(models.Model):
    name = models.CharField(max_length=100, default="")
    users = models.ManyToManyField("core.User")


class User(AbstractUser):
    family = models.ForeignKey("core.Family", on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey(
        "Couple", null=True, default=None, on_delete=models.SET_NULL
    )
    last_name = family.name
    gender = models.CharField(
        max_length=10, choices=Gender.choices, default=None, null=True
    )

    @property
    def children(self):
        marriages = Couple.objects.filter(user__in=[self]).values_list("id", flat=True)
        return User.objects.filter(parent_id__in=marriages)

    @property
    def siblings(self):
        return User.objects.filter(parent=self.parent)

    @property
    def grand_parents(self):
        parents = chain(
            *self.parent.users.values_list("parent__users__username", flat=True)
        )
        return User.objects.filter(username__in=parents)

    @property
    def parents(self):
        return self.parent.users.all()

    @property
    def parent_siblings(self):
        return User.objects.filter(
            parent_id__in=self.parents.values_list("parent_id", flat=True)
        )

    @property
    def siblings_children(self):
        couples = Couple.objects.filter(users__in=self.siblings).values_list(
            "id", flat=True
        )
        return User.objects.filter(parent_id__in=couples)

    @property
    def parent_siblings_children(self):
        couples = Couple.objects.filter(users__in=self.parent_siblings).values_list(
            "id", flat=True
        )
        return User.objects.filter(parent_id__in=couples)

    def relationship(self, user):
        relationship = cache.get(f"{self.id}->{user.id}")
        if relationship:
            return relationship
        else:
            if user in self.children:
                relationship = "son" if user.gender == Gender.Male else "daughter"
            elif user in self.siblings:
                relationship = "brother" if user.gender == Gender.Male else "sister"
            elif user in self.parents:
                relationship = "father" if user.gender == Gender.Male else "mother"
            elif user in self.grand_parents:
                relationship = (
                    "grand father" if user.gender == Gender.Male else "grand mother"
                )
            elif user in self.parent_siblings:
                relationship = "uncle" if user.gender == Gender.Male else "aunty"
            elif user in self.siblings_children:
                relationship = "nephew" if user.gender == Gender.Male else "niece"
            elif user in self.parent_siblings_children:
                relationship = "cousin"
            cache.set(f"{self.id}->{user.id}", relationship)
            return relationship

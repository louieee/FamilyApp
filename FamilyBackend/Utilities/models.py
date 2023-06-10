import os

import django
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FamilyBackend.settings')
django.setup()
from User.models import User
from Family.models import Family


# Create your models here.

# User.objects.create_user(first_name="Izu", username="izu", email="izu@example.com", password="MONKEYSex")
f = Family.objects.last()
users = User.objects.exclude(family_id=f.id).update(family_id=f.id)

print(User.objects.last().family.name)

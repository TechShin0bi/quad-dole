# Connect the signals
from django.db.models.signals import post_save


# Signal to create/update user profile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()




post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)

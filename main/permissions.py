from django.contrib.auth.mixins import UserPassesTestMixin


class UserPermissionsMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.get_object().owner == self.request.user

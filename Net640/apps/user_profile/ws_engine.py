from django.contrib.auth import get_user_model


User = get_user_model()


class UserProfileWS:

    def __call__(self, user, message):
        # TODO: try..except
        func = getattr(self, message['action'])
        return func(user, message)

    def get_user_page_size(self, user, message=None):
        return {"result": True,
                "action": "user_page_size",
                "size": user.get_size(explicit=True)
                }

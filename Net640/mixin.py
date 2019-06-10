from Net640.settings import MAX_PAGE_SIZE


class LikesMixin:
    def get_rating(self):
        rating = 0
        for user in self.likes.all():
            rating += (MAX_PAGE_SIZE - user.get_size()) / MAX_PAGE_SIZE
        return rating

    def has_like(self, somebody):
        if self.likes.filter(username=somebody.username).first():
            return True
        else:
            return False

    def add_like(self, user_who_likes_us):
        if not self.has_like(user_who_likes_us):
            self.likes.add(user_who_likes_us)
            return True

    def remove_like(self, user_who_dislikes_us):
        if self.has_like(user_who_dislikes_us):
            self.likes.remove(user_who_dislikes_us)
            return True

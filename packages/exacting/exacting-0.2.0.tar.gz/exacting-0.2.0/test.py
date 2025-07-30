from exacting import Exact, field


class Stuff(Exact):
    cool: bool


class Comment(Exact):
    user: str
    stars: int = field(minv=1, maxv=5)
    stuff: Stuff


b = Comment(user="Waltuh", stars=3, stuff=Stuff(cool=True)).exact_as_bytes()
print(b)
print(Comment.exact_from_bytes(b))

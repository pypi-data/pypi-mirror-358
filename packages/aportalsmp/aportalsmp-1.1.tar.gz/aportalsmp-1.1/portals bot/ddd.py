import asyncio

from tonnelmp import *
auth = "user=%7B%22id%22%3A6083232778%2C%22first_name%22%3A%22bleach%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22gtbdg%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2Fak_-2z0eUHRjUWa7d8dvlHFL1P3Dmra-ES-NHSK1ST3Uo-fo-iIXSNpZbs2t-MPl.svg%22%7D&chat_instance=4821523022942172384&chat_type=sender&auth_date=1749803690&signature=NQ_uZ_naKri_s8IEsTabnksUC-LoZ6IH4g7ZVfg_v1D_TNLskFOETvMkJ-4KZdStKZIwHcRGNNsuHT8lIfEpDA&hash=674ea8370f0fb318c956d24fa820f83676f60e6acdaeccd9c5b7f11fc35205b7"
print(getGifts(authData=auth))
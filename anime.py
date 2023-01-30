import anime_qq
from anime_qq.util import save_anime_image
from anime_qq.anime_post import AnimePost
import random
import sys
import logging

logger = logging.getLogger(__name__)
def photo_to_anime(input_file:str, output_file):
    anime = AnimePost.get_anime_image(input_file)
    if anime.error is not None:
        raise Exception(anime.error)
    #logger.info("anime_qq results urls: " + str(anime.extra))
    save_anime_image(output_file, anime.extra[0])

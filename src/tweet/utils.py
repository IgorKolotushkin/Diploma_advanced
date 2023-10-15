"""Модуль для работы с загружаемыми файлами."""
from os import path
from random import choice
from string import ascii_letters, digits

from aiofiles.os import remove
from aiofiles import open
from fastapi import UploadFile
from sqlalchemy import ScalarResult

SYMBOLS = ascii_letters + digits


async def delete_medias(medias: ScalarResult) -> None:
    """
    Функция для удаления изображения при удалении твита.

    Args:
        medias: путь до удаляемого файла
    """
    for media in medias.all():
        await remove('/src/{}'.format(media.media_path))


async def save_media(media_file: UploadFile) -> str:
    """
    Функция сохранения изображения.

    Args:
        media_file: файл для сохранения

    Returns:
        str: путь до сохраненного файла
    """
    file_name: str = media_file.filename
    if path.exists('/src/media/{file_name}'.format(file_name=file_name)):
        parts_file: list[str] = file_name.split('.')
        random_sym: str = ''.join(choice(SYMBOLS) for _ in range(8))
        file_name: str = ''.join(
            [
                parts_file[0],
                '_',
                random_sym,
                '.',
                parts_file[1],
            ],
        )
    async with open('/src/media/{}'.format(file_name), 'wb') as image_file:
        await image_file.write(await media_file.read())

    return file_name

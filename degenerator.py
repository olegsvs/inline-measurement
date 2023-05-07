import os
import cv2
import numpy as np
import random
from PIL import ImageFont, ImageDraw, Image

FRAME_MARGIN_X = 23  # отступ до окантовки фрейма по Ox
FRAME_MARGIN_Y = 13  # отступ до окантовки фрейма по Oy
FRAME_THICKNESS = 1  # размер окантовки
FRAME_INNER_PADDING = 3  # внутренний отступ до медиа (без учёта толщины)

MEDIA_WIDTH = 306  # длина медиа в фрейме
MEDIA_HEIGHT = 284  # ширина медиа в фрейме

TEXT_AREA_HEIGHT = 69  # высота области для текста
TEXT_DEFAULT_FONT_SIZE = 28  # дефолтный размер шрифта
TEXT_CONTAINER_PADDING = 14  # отступы контейнера

# margin - padding - media - padding - margin
WIDTH = 2 * FRAME_MARGIN_X + 2 * FRAME_INNER_PADDING + MEDIA_WIDTH
# margin - padding - media - padding - text
HEIGHT = FRAME_MARGIN_Y + 2 * FRAME_INNER_PADDING + MEDIA_HEIGHT + TEXT_AREA_HEIGHT

# margin - padding - media - padding - text
MEDIA_TOP = FRAME_MARGIN_Y + FRAME_INNER_PADDING
MEDIA_BOTTOM = HEIGHT - TEXT_AREA_HEIGHT - FRAME_INNER_PADDING

# margin - padding - media - padding - margin
MEDIA_LEFT = FRAME_MARGIN_X + FRAME_INNER_PADDING
MEDIA_RIGHT = WIDTH - FRAME_MARGIN_X - FRAME_INNER_PADDING

# margin - padding - container[text] - padding - margin
MAX_TEXT_LENGTH = WIDTH - 2 * FRAME_MARGIN_X - 2 * TEXT_CONTAINER_PADDING

TEMPLATE = cv2.rectangle(
    # чёрный фон по размерам медиа
    img=np.zeros(
        (HEIGHT, WIDTH, 3),
        dtype=np.uint8
    ),

    # верхний левый угол окантовки
    pt1=(FRAME_MARGIN_X,
         FRAME_MARGIN_Y),

    # нижний правый угол окантовки
    pt2=(WIDTH - FRAME_MARGIN_X - 1,
         HEIGHT - TEXT_AREA_HEIGHT - 1),

    color=(255, 255, 255),
    thickness=FRAME_THICKNESS
)

# кэш для сгенерированных размеров шрифтов
# TODO: пре-генерация? возможно целесообразнее
cached_sizes: dict[int, ImageFont] = {}

all_txt = [
    [u"А че"],
    [u"заставляет задуматься"],
    [u"Жалко пацана"],
    [u"ты че сука??"],
    [u"ААХАХАХАХХАХА", u"ААХАХААХАХА"],
    [u"ГИГАНТ МЫСЛИ", u"отец русской демократии"],
    [u"Он"],
    [u"ЧТО БЛЯТЬ?"],
    [u"охуенная тема"],
    [u"ВОТ ОНИ", u"типичные комедиклабовские шутки"],
    [u"НУ НЕ БЛЯДИНА?"],
    [u"Узнали?"],
    [u"Согласны?"],
    [u"Вот это мужик"],
    [u"ЕГО ИДЕИ", u"будут актуальны всегда"],
    [u"ПРИ СТАЛИНЕ ОН БЫ СИДЕЛ"],
    [u"о вадим"],
    [u"2 месяца на дваче", u"и это, блядь, нихуя не смешно"],
    [u"Что дальше?", u"Чайник с функцией жопа?"],
    [u"И нахуя мне эта информация?"],
    [u"Верхний текст"],
    [u"нижний текст"],
    [u"Показалось"],
    [u"Суды при анкапе"],
    [u"Хуйло с района", u"такая шелупонь с одной тычки ляжет"],
    [u"Брух"],
    [u"Расскажи им", u"как ты устал в офисе"],
    [u"Окурок блять", u"есть 2 рубля?"],
    [u"Аниме ставшее легендой"],
    [u"СМИРИСЬ", u"ты никогда не станешь настолько же крутым"],
    [u"а ведь это идея"],
    [u"Если не лайкнешь у тебя нет сердца"],
    [u"Вместо тысячи слов"],
    [u"ШАХ И МАТ!!!"],
    [u"Самый большой член в мире", u"У этой девушки"],
    [u"Немного", u"перфекционизма"],
    [u"кто"],
    [u"эта сука уводит чужих мужей"],
    [u"Кто он???"],
    [u"Вы тоже хотели насрать туда в детстве?"],
    [u"Вся суть современного общества", u"в одном фото"],
    [u"Он обязательно выживет!"],
    [u"Вы тоже хотите подрочить ему?"],
    [u"И вот этой хуйне поклоняются русские?"],
    [u"Вот она суть", u"человеческого общества в одной картинке"],
    [u"Вы думали это рофл?", u"Нет это жопа"],
    [u"При сталине такой хуйни не было", u"А у вас было?"],
    [u"Он грыз провода"],
    [u"Назло старухам", u"на радость онанистам"],
    [u"Где-то в Челябинске"],
    [u"ИДЕАЛЬНО"],
    [u"Грыз?"],
    [u"Ну давай расскажи им", u"какая у тебя тяжелая работа"],
    [u"Желаю в каждом доме такого гостя"],
    [u"Шкура на вырост"],
    [u"НИКОГДА", u"не сдавайся"],
    [u"Оппа гангнам стайл", u"уууу сэкси лейди оп оп"],
    [u"Они сделали это", u"сукины дети, они справились"],
    [u"Эта сука", u"хочет денег"],
    [u"Это говно, а ты?"],
    [u"Вот она нынешняя молодежь"],
    [u"Погладь кота", u"погладь кота сука"],
    [u"Я обязательно выживу"],
    [u"Вот она, настоящая мужская дружба", u"без политики и лицимерия"],
    [u"Царь, просто царь"],
    [u"Нахуй вы это в учебники вставили?", u"И ещё ебаную контрольную устроили"],
    [u"ЭТО НАСТОЯЩАЯ КРАСОТА", u"а не ваши голые бляди"],
    [u"Тема раскрыта ПОЛНОСТЬЮ"],
    [u"РОССИЯ, КОТОРУЮ МЫ ПОТЕРЯЛИ"],
    [u"ЭТО - Я", u"ПОДУМАЙ МОЖЕТ ЭТО ТЫ"],
    [u"почему", u"что почему"],
    [u"КУПИТЬ БЫ ДЖЫП", u"БЛЯТЬ ДА НАХУЙ НАДО"],
    [u"мы не продаём бомбастер лицам старше 12 лет"],
    [u"МРАЗЬ"],
    [u"Правильная аэрография"],
    [u"Вот она русская", u"СМЕКАЛОЧКА"],
    [u"Он взял рейхстаг!", u"А чего добился ты?"],
    [u"На аватарку"],
    [u"Фотошоп по-деревенски"],
    [u"Инструкция в самолете"],
    [u"Цирк дю Солей"],
    [u"Вкус детства", u"школоте не понять"],
    [u"Вот оно - СЧАСТЬЕ"],
    [u"Он за тебя воевал", u"а ты даже не знаешь его имени"],
    [u"Зато не за компьютером"],
    [u"Не трогай это на новый год"],
    [u"Мой первый рисунок", u"мочой на снегу"],
    [u"Майские праздники на даче"],
    [u"Ваш пиздюк?"],
    [u"Тест драйв подгузников"],
    [u"Не понимаю", u"как это вообще выросло?"],
    [u"Супермен в СССР"],
    [u"Единственный", u"кто тебе рад"],
    [u"Макдональдс отдыхает"],
    [u"Ну че", u" как дела на работе пацаны?"],
    [u"Вся суть отношений"],
    [u"Беларусы, спасибо!"],
    [u"У дверей узбекского военкомата"],
    [u"Вместо 1000 слов"],
    [u"Один вопрос", u"нахуя?"],
    [u"Ответ на санкции", u"ЕВРОПЫ"],
    [u"ЦЫГАНСКИЕ ФОКУСЫ"],
    [u"Блять!", u"да он гений!"],
    [u"ВОТ ЭТО", u"НАСТОЯЩИЕ КАЗАКИ а не ряженные"],
    [u"Нового года не будет", u"Санта принял Ислам"],
    [u"Он был против наркотиков", u"а ты и дальше убивай себя"],
    [u"Всем похуй!", u"Всем похуй!"],
    [u"БРАТЬЯ СЛАВЯНЕ", u"помните друг о друге"],
    [u"ОН ПРИДУМАЛ ГОВНО", u"а ты даже не знаешь его имени"],
    [u"краткий курс истории нацболов"],
    [u"Эпоха ренессанса"]

]


# достать шрифт из кэша, либо сгенерировать новый
def get_font_by_size(size: int) -> ImageFont:
    if size in cached_sizes:
        return cached_sizes[size]

    font = ImageFont.truetype(os.getenv("FONT_PATH", "font.ttf"), size)
    cached_sizes[size] = font

    return font


# подобрать шрифт по (размеру) текста
def generate_font_from_text(text: str) -> ImageFont:
    font = get_font_by_size(TEXT_DEFAULT_FONT_SIZE)
    text_length = font.getlength(text)

    # если текст больше дозволенного
    if text_length > MAX_TEXT_LENGTH:
        # изменение размера шрифта пропорционально превышению
        ratio = MAX_TEXT_LENGTH / text_length
        font_size = int(TEXT_DEFAULT_FONT_SIZE * ratio)
        font_size += font_size % 2  # 23 -> 24, 25 -> 26
        font = get_font_by_size(int(font_size))

    return font


# манипуляция с масштабированием и наложением фрейма
# TODO: mp & frame-division: https://stackoverflow.com/a/55259105/20949821
def modify_template_by_frame(template: np.ndarray, frame: np.ndarray):
    frame = cv2.resize(
        frame,
        (MEDIA_WIDTH, MEDIA_HEIGHT),

        # лучшее соотношение задержки к качеству
        # чёткое изображение ценой +100-200мс оверхэда
        interpolation=cv2.INTER_CUBIC
    )

    # замена пикселей в области y:x на фрейм
    template[MEDIA_TOP:MEDIA_BOTTOM, MEDIA_LEFT:MEDIA_RIGHT] = frame


# запись видео демика
def write_video(input_file: str, output_file: str, template: np.ndarray):
    stream = cv2.VideoCapture(input_file)

    out = cv2.VideoWriter(
        output_file,
        cv2.VideoWriter_fourcc(*'mp4v'),
        stream.get(cv2.CAP_PROP_FPS),
        (WIDTH, HEIGHT)
    )

    while stream.isOpened():
        flag, frame = stream.read()
        if not flag:
            break

        modify_template_by_frame(template, frame)
        out.write(template)

    stream.release()
    out.release()


# запись фото демика
def write_image(input_file: str, output_file: str, template: np.ndarray):
    image = cv2.imread(input_file)
    modify_template_by_frame(template, image)
    cv2.imwrite(output_file, template)


def generate_demotivator(input_file: str, output_file: str, custom_text):
    text_sample = all_txt[random.randrange(len(all_txt))]
    if len(text_sample) == 2:
        text = f'{text_sample[0]}\n{text_sample[1]}'
    else:
        text = f'{text_sample[0]}'
    if custom_text is not None:
        text = custom_text
    font = generate_font_from_text(text)

    _, _, text_width, text_height = font.getbbox(text)
    text_x = WIDTH - FRAME_MARGIN_X - TEXT_CONTAINER_PADDING - MAX_TEXT_LENGTH / 2
    text_y = HEIGHT - TEXT_AREA_HEIGHT / 2 - 1

    # opencv image (numpy matrix) -> pil image
    image = Image.fromarray(TEMPLATE)

    draw = ImageDraw.Draw(image)
    draw.text(
        (text_x, text_y),
        text=text,
        font=font,
        fill="#fff",
        anchor="mm",
        align="center"
    )

    # pil image -> opencv image (numpy matrix)
    template = np.array(image)  # noqa

    if input_file.endswith(".mp4"):  # если видео
        return write_video(input_file, output_file, template)
    elif input_file.endswith(".jpg"):  # если изображение
        return write_image(input_file, output_file, template)

    # что это за херня?
    raise NotImplementedError

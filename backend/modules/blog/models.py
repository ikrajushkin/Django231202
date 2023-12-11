from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey


User = get_user_model()


class Article(models.Model):
    """
    Модель постов для сайта
    """    

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'), 
        ('draft', 'Черновик')
    )

    title = models.CharField(verbose_name='Заголовок', max_length=255)
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    category = TreeForeignKey('Category', on_delete=models.PROTECT, related_name='articles', verbose_name='Категория')
    short_description = models.TextField(verbose_name='Краткое описание', max_length=500)
    full_description = models.TextField(verbose_name='Полное описание')
    thumbnail = models.ImageField(
        verbose_name='Превью поста', 
        blank=True, 
        upload_to='images/thumbnails/%Y/%m/%d/', 
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))]
    )
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус поста', max_length=10)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    author = models.ForeignKey(to=User, verbose_name='Автор', on_delete=models.SET_DEFAULT, related_name='author_posts', default=1)
    updater = models.ForeignKey(to=User, verbose_name='Обновил', on_delete=models.SET_NULL, null=True, related_name='updater_posts', blank=True)
    fixed = models.BooleanField(verbose_name='Зафиксировано', default=False)

    class Meta:
        db_table = 'app_articles'
        ordering = ['-fixed', '-time_create']
        indexes = [models.Index(fields=['-fixed', '-time_create', 'status'])]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title

        '''
        Примечания за поля модели:

title - заголовок, с максимальным количеством символов 255
slug - ссылка на материал (латиница), или в простонародии ЧПУ-человеко-понятный урл, с максимальным количеством символов 255, blank (необязательно к заполнению)
short_description - текстовое поле, ограниченное 300 символами.
full_description - аналогично, без ограничений.
thumbnail - превью статьи.
status - опубликована статья, или черновик.
time_create и time_update - время создания и обновления статьи.
author - ключ ссылаемый на пользователя из другой таблицы (пользователей) c on_delete=models.PROTECT (при удалении происходит защита, что не позволяет так просто удалить пользователя с его статьями, чтоб вы могли передать статьи другому человеку)
updater - аналогично, только если при обновлении статьи выводить того, кто редактировал (добавлять, если вам это нужно) c on_delete=models.CASCADE (при удалении просто убирается значение того, кто обновил у статей каскадно)
fixed - булево значение, по умолчанию False (не закреплено)
Примечания в параметрах Meta:

ordering - сортировка, ставим -created_at, чтобы выводились статьи в обратном порядке (сначала новые, потом старые).
verbose_name - название модели в админке в ед.ч
verbose_name_plural - в мн.числе
db_table - название таблицы в БД. (можно не добавлять, будет создано автоматически)
indexes - индексирование полей, чтобы ускорить результаты сортировки.
Примечание о get_user_model():

get_user_model() - это удобный способ получить модель пользователя, определенную в проекте Django. Вместо того, чтобы явно импортировать модель пользователя (from django.contrib.auth.models import User), get_user_model() возвращает модель пользователя, которая настроена в настройках проекта (AUTH_USER_MODEL).

Основные преимущества использования get_user_model():

Гибкость: get_user_model() возвращает текущую модель пользователя проекта, что позволяет изменить модель пользователя, используемую в проекте, без необходимости изменения кода.
Портативность: использование get_user_model() позволяет вашему коду быть переносимым между различными проектами Django, где может быть использована различная модель пользователя.
Расширяемость: если вы расширяете модель пользователя проекта, например, добавляете новые поля, использование get_user_model() обеспечивает совместимость с этими изменениями, не нарушая стандартных возможностей аутентификации Django.
Кроме того, использование get_user_model() вместо явного импорта модели пользователя упрощает написание тестов, так как тесты не будут зависеть от конкретной модели пользователя.
        '''

class Category(MPTTModel):
    """
    Модель категорий с вложенностью
    """
    title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, verbose_name='URL категории', blank=True)
    description = models.TextField(verbose_name='Описание категории', max_length=300)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    class MPTTMeta:
        """
        Сортировка по вложенности
        """
        order_insertion_by = ('title',)

    class Meta:
        """
        Сортировка, название модели в админ панели, таблица в данными
        """
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'app_categories'

    def __str__(self):
        """
        Возвращение заголовка статьи
        """
        return self.title
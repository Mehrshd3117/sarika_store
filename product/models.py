from django.contrib.auth.models import User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext_lazy as _


class Category(MPTTModel):
    title = models.CharField(_('عنوان'), max_length=50)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name=_('والد'))
    slug = models.SlugField(_('اسلاگ'), allow_unicode=True, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(_('تاریخ قرارگیری در سایت'), auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('دسته بندی')
        verbose_name_plural = _('دسته بندی ها')


class Product(models.Model):
    title = models.CharField(_('عنوان'), max_length=100)
    description = models.TextField(_('توضیحات'))
    category = models.ForeignKey(Category, models.CASCADE, related_name='categories', null=True, blank=True,
                                 verbose_name=_('دسته بندی'))
    price = models.PositiveIntegerField(_('قیمت(تومان)'), default=0)
    discount = models.FloatField(_('درصد تخفیف'), null=True, blank=True)
    discount_price = models.PositiveIntegerField(_('قیمت تخفیف خورده (تومان )'), null=True, blank=True)
    slug = models.SlugField(_('اسلاگ'), allow_unicode=True, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(_('تاریخ قرارگیری در سایت'), auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('محصول')
        verbose_name_plural = _('محصولات')


class Picture(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pictures', verbose_name=_('محصول'))
    image = models.ImageField(_('تصویر محصول'), upload_to='products/picture')

    def __str__(self):
        return self.image.url

    class Meta:
        verbose_name = _('عکس')
        verbose_name_plural = _('عکس ها')


class Favorite(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='favorites', verbose_name=_('کاربر'))
    product = models.ForeignKey(Product, models.CASCADE, related_name='favorites', verbose_name=_('محصول'))

    def __str__(self):
        return f"{self.user.first_name} - {self.product.title}"

    class Meta:
        verbose_name = _('علاقه مندی')
        verbose_name_plural = _('علاقه مندی ها')

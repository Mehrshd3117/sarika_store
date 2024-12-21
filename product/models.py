from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories', null=True, blank=True,
                                 verbose_name=_('دسته بندی'))
    price = models.PositiveIntegerField(_('قیمت(تومان)'), default=0)
    discount = models.FloatField(_('درصد تخفیف'), null=True, blank=True)
    discounted_price = models.PositiveIntegerField(_('قیمت تخفیف خورده (تومان )'), null=True, blank=True)
    slug = models.SlugField(_('اسلاگ'), allow_unicode=True, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(_('تاریخ قرارگیری در سایت'), auto_now_add=True)

    # Discount related processes
    def save(self, *args, **kwargs):
        discount, discounted_price = None, None

        try:
            discounted_price = self.price - (self.price * self.discount / 100)
            print(discounted_price, 1)
        except:
            pass

        try:
            discount = ((self.price - self.discounted_price) / self.price) * 100
            print(discount, 2)
        except:
            pass

        if discounted_price and discount:
            self.discounted_price = discounted_price
        elif discounted_price and not discount:
            self.discounted_price = discounted_price
            self.discount = self.discount
        elif discount and not discounted_price:
            self.discount = discount
            self.discounted_price = self.discounted_price
        else:
            self.discounted_price = self.price

        super().save(*args, **kwargs)

    def get_discounted_price(self):
        price = self.discounted_price
        return "{:,.0f} تومان ".format(price)

    def get_price(self):
        price = self.price
        return "{:,.0f} تومان ".format(price)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('کاربر'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites', verbose_name=_('محصول'))

    def __str__(self):
        return f"{self.user.first_name} - {self.product.title}"

    class Meta:
        verbose_name = _('علاقه مندی')
        verbose_name_plural = _('علاقه مندی ها')


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name=_('محصول'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users', verbose_name=_('کاربر'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True,
                               verbose_name=_('کامنت والد'))
    body = models.TextField(_('متن کامنت'))
    is_active = models.BooleanField(default=False, verbose_name=_('فعال بودن'))
    created_at = models.DateTimeField(_('تاریخ قرارگیری در سایت'), auto_now_add=True)

    def __str__(self):
        return f'  نظر توسط کاربر {self.body[:20]} ---- نظر:{self.user.first_name}'

    class Meta:
        verbose_name = _('نظر')
        verbose_name_plural = _('نظرات')
        ordering = ['-created_at']


class DiscountCode(models.Model):
    name = models.CharField(_('نام کد تخفیف'), max_length=50)
    price = models.PositiveIntegerField(_('قیمت (تومان)'), default=0)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('قابل استفاده برای محصولات'))
    limit = models.PositiveIntegerField(_('حداقل قیمت'))
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    used_by = models.ManyToManyField(User, verbose_name=_('استفاده شده توسط'), null=True, blank=True,
                                     related_name='discounts')
    expiration = models.DateTimeField(_('تاریخ انقضا'), null=True, blank=True)

    def get_price(self):
        price = self.price
        return "{:,.0f}".format(price)

    def get_limit(self):
        limit = self.limit
        return "{:,.0f}".format(limit)

    def is_not_expired(self):
        if self.expiration >= timezone.localtime(timezone.now()):
            return True
        else:
            return False

    def __str__(self):
        return f'{self.name} --- {self.quantity}'

    class Meta:
        verbose_name = _('کد تخفیف')
        verbose_name_plural = _('کد های تخفیف')

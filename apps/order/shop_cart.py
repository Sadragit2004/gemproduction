# apps/cart/shop_cart.py
from apps.file.models import File
from decimal import Decimal

class ShopCart:
    """
    سبد خرید فایل‌ها (دیجیتال)
    ذخیره در session
    """

    SESSION_KEY = "shop_cart"

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if not cart:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def add(self, file: File):
        """
        افزودن فایل به سبد خرید
        (بدون تکرار یا تعداد)
        """
        file_id = str(file.id)
        if file_id not in self.cart:
            self.cart[file_id] = {
                "title": file.title,
                "price": str(file.price),
                'final_price':file.get_price_by_discount(),
                "image": file.image.url if file.image else "",
            }
            self.save()


    def get_cart(self):
        items = []
        file_ids = self.cart.keys()
        files = File.objects.filter(id__in=file_ids)

        for f in files:
            item = self.cart[str(f.id)]
            items.append({
                "file": f,  # خود مدل File
                "title": item["title"],
                "price": item["price"],
                "final_price": item["final_price"],  # 🔥 اضافه شد
                "image": item["image"],
            })
        return items




    def remove(self, file: File):
        """
        حذف فایل از سبد خرید
        """
        file_id = str(file.id)
        if file_id in self.cart:
            del self.cart[file_id]
            self.save()

    def clear(self):
        """
        خالی کردن کل سبد خرید
        """
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def save(self):
        """
        ذخیره تغییرات
        """
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def __iter__(self):
        """
        پیمایش آیتم‌ها
        """
        file_ids = self.cart.keys()
        files = File.objects.filter(id__in=file_ids)

        for file in files:
            item = self.cart[str(file.id)]
            item["file"] = file
            item["total_price"] = Decimal(item["final_price"])
            yield item

    def __len__(self):
        """
        تعداد فایل‌ها در سبد خرید
        """
        return len(self.cart)

    def get_total_price(self):
        """
        مجموع قیمت فایل‌ها
        """
        return sum(Decimal(item["final_price"]) for item in self.cart.values())

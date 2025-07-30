![موتور جستجوی گردو](https://gerdoo.me/static/commons/img/logo.c179f12989b4.svg)



# Gerdoo

این کتابخانه مخصوص استفاده برای موتور جستجوی **گردو** طراحی شده است


برای ساخت یک یک شیء از سرچ کننده گردو این کار را انجام دهید :
```python

import Gerdoo from Gerdoo

gerdoo = Gerdoo(
    "Query",#الزامی
    Proxies={},#الزامی نمی باشد
    Base_Url="url",#الزامی نمی باشد
    User_Agent="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"#الزامی نمی باشد
)
```

## امکانات
- جستجوی کلی
- جستجوی تصویر
- جستجوی ویدیو
- جستجوی اخبار
- دریافت پیشنهادات برای جستجو

## Enums
```python
from Gerdoo.enums import (
    Search,
    SearchImage,
    SearchVideo,
    SearchNews
)
```
مثال استفاده از اینامز ها :
```python
from Gerdoo import Gerdoo
from Gerdoo.enums import Search


search = Gerdoo("Query")

for Item in search.search(
        filter_date=Search.filter_date.DAY
    ):
    for Key , Value in Item.items():
        print(f"{Key} : {Value}")
    print("\n\n=====================================\n\n")
```


## جستجوی کلی

```python

import Gerdoo from Gerdoo

gerdoo = Gerdoo("Query")
print(gerdoo.search())
```


## جستجوی تصاویر

```python

import Gerdoo from Gerdoo

gerdoo = Gerdoo("Query")
print(gerdoo.search_image())
```


## جستجوی ویدیو ها

```python

import Gerdoo from Gerdoo

gerdoo = Gerdoo("Query")
print(gerdoo.search_video())
```


## جستجوی اخبار

```python

import Gerdoo from Gerdoo

gerdoo = Gerdoo("Query")
print(gerdoo.search_news())
```


## دریافت پیشنهادات برای جستجو

```python

import Gerdoo from Gerdoo

gerdoo = Gerdoo("Query")
print(gerdoo.GetSuggestions())
```


### لینک ها
- [نویسنده](https://apicode.pythonanywhere.com/)
- [موتور جستجوی گردو](https://gerdoo.me/)
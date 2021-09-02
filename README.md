# ServerMobileParserLinuxOrgRu
Сервер [мобильного приложения](https://github.com/lelsene/MobileParserLinuxOrgRu), агрегатора новостей linux.org.ru.

## Описание
Принимает запросы на:
- получение списка новостей со смещением: "/articles/\<offset\>". 
- получение конкретной новости с комментариями по секции и id: "/article/\<section\>/\<id\>". <br /> 

Возвращает запрашиваемые данные в JSON формате.

## Пример
 - http://127.0.0.1:5000/articles/0
    - ![image](https://user-images.githubusercontent.com/43280704/131816983-0b013cd8-36a1-4cc9-b484-93cd0e828832.png)

 - http://127.0.0.1:5000/article/hardware/16506300
    - ![image](https://user-images.githubusercontent.com/43280704/131817164-aaa1596b-77c8-4fbf-9b52-02b1883b76ab.png)  

## Технологии
- Python 3.7.8
- Flask 1.1.2
- Beautiful Soup 4.9.3

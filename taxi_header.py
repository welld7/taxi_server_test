# -*- coding: utf-8 -*-

"""Сервер такси.

Помогает найти водителя.

Для начала использования необходимо зарегистрироваться.


## Клиентский протокол

### Создание пользователя

    POST /signup
    {
        "name": "Петя",
        "username": "petya",
        "secret": "somesecret"
    }

    200 - пользователь создан
    406 - username занят

### Обновление данных пользователя

    POST /user/edit?username=petya
    Authorization: Custom somesecret
    {
        "new_secret": "supersecret"
    }

    200 - обновили данные пользователя
    403 - неверный ключ

### Получение идентификатора для создания заказа

    POST /order/draft?username=petya
    Authorization: Custom supersecret

    200 OK
    {
        "order_id": "11111111111111111111111111111111"
    }

С полученным идентификатором можно создать заказ.
Идентификатор хранится на сервере минимум 30 секунд, потом удаляется.

### Создание заказа

    POST /order/commit?username=petya&order_id=11111111111111111111111111111111
    Authorization: Custom supersecret
    {
        "address": "Малая Бронная, 12"
    }

    200 - заказ создан
    403 - неверный ключ
    404 - идентификатор заказа не найден
    429 - превышен лимит на число заказов

### Получение списка заказов

    GET /orders?username=petya&show=all
    Authorization: Custom supersecret
    {
        "orders": [
            {
                "order_id": "11111111111111111111111111111111",
                "address": "Малая Бронная, 12",
                "created": 1480409575.600229,
                "updated": 1480409575.600229,
                "status": "pending"
            },
            {
                "order_id": "22222222222222222222222222222222",
                "address": "Большая Бронная, 21",
                "created": 1480409575.600229,
                "updated": 1480409575.600229,
                "status": "found",
                "performer": {
                    "name": "Пётр"
                }
            },
            {
                "order_id": "33333333333333333333333333333333",
                "address": "Большая Никитская, 13",
                "created": 1480409575.600229,
                "updated": 1480409575.600229,
                "status": "complete",
                "performer": {
                    "name": "Пётр"
                }
            },
            {
                "order_id": "44444444444444444444444444444444",
                "address": "Большая Никитская, 13",
                "created": 1480409575.600229,
                "updated": 1480409575.600229,
                "status": "expired"
            },
            {
                "order_id": "55555555555555555555555555555555",
                "address": "Малая Бронная, 12",
                "created": 1480409575.600229,
                "updated": 1480409575.600229,
                "status": "cancelled"
            }
        ]
    }

    200 - OK, список заказов
    403 - неверный ключ

    Статусы:
        pending   - ищем исполнителя
        found     - исполнитель найден
        complete  - заказ завершён
        expired   - не смогли найти исполнителя на заказ
        cancelled - отменён пользователем

    Значения фильтра show:
        all    - показать все заказы
        active - только активные (pending, found)

### Отмена заказа

    POST /order/cancel?username=petya&order_id=11111111111111111111111111111111
    Authorization: Custom supersecret

    200 - заказ отменён
    403 - неверный ключ
    404 - заказ не найден
    406 - заказ нельзя отменить (исполнитель найден, поиск не удался)

"""

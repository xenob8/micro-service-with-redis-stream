<p>
Есть два сервиса inventory и payment
</p>
<p>
inventory управляет данными о продуктах: название, цена, количество
</p>
<p>
сервис payment создает ордера на продажу, ордер имеет следующие поля:
</p>
<p>
id продукта, цена продукта, комиссия, итоговая цена продажи, количество штук на покупку, текущий статус ордера (ожидание, завершено, отмена платежа)
</p>
<p>
Чтобы создать ордер на покупку пользователь должен получить id продукта.
</p>
<p>
Когда пользователь создает ордер на покупку товара, payment обращается к inventory и дополняет необходимые поля класса Order. После этого присваивает статус pending. Затем в бекграунд отправляется задача, эмулирующая процесс оплаты (заглушка 5 сек). После завершения статус становится completed и через шину redis stream отправляется Event order_completed. Сервис inventory слушает шину в блокирующем режиме. После получения ивента он уменьшает количество товара. В случае, если товар был удален за это время, он отправляет Event refund_order. Сервис payment  тоже слушает ивенты, и, в случе, если ему приходит refund_order он меняет статус ордера на refunded и сохраняет в БД.
</p>
<p>
У каждого сервиса своя бд в Redis. Также есть отдельная БД для redis stream. Весь проект можно поднять с помощью docker compose. Настроен nginx для работы всех сервисов на одном порту 8080.
</p>
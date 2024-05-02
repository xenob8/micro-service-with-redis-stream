from main import redis_stream, Order

key = 'refund_order'

while True:
    try:
        results = redis_stream.xread({key: "$"}, block=1000, count=5)

        if results != []:
            print(results)
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj['pk'])
                order.status = 'refunded'
                order.save()

    except Exception as e:
        print(str(e))


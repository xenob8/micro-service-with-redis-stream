from main import redis_stream, Product

key = 'order_completed'

while True:
    try:
        results = redis_stream.xread({key: "$"}, block=1000, count=5)

        if results != []:
            for result in results:
                obj = result[1][0][1]
                try:
                    product = Product.get(obj['product_id'])
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()
                except:
                    redis_stream.xadd('refund_order', obj, '*')

    except Exception as e:
        print(str(e))

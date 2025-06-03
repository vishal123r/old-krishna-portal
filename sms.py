order)
    total_repeat_customers_query = '''
        SELECT COUNT(DISTINCT mobile) AS total_repeat_customers
        FROM customers
        WHERE mobile IN (
            SELECT mobile
            FROM customers
            GROUP BY mobile
            HAVING COUNT(mobile) > 1
        )
        AND mobile NOT LIKE '0%' 
        AND mobile NOT LIKE '%000000%' 
        AND LENGTH(mobile) > 5
    '''
    cursor.execute(total_repeat_customers_query)
    total_repeat_customers = cursor.fetchone()[0]

    # Query for repeat orders (customers with more than 1 order)
    repeat_query = '''
        SELECT COUNT(mobile) AS repeat_orders
        FROM customers
        WHERE mobile IN (
            SELECT mobile
            FROM customers
            GROUP BY mobile
            HAVING COUNT(mobile) > 1
        )
        AND mobile NOT LIKE '0%' 
        AND mobile NOT LIKE '%000000%' 
        AND LENGTH(mobile) > 5
    '''
    cursor.execute(repeat_query)
    repeat_orders = cursor.fetchone()[0]

    # Query for new orders (customers
from sortedcontainers import SortedDict

# Create SortedDicts for buy and sell prices
li_b = SortedDict({
    400: None,
    390: None,
    380: None,
    320: None,
    318: None,
    310: None,
    309: None,
    308: None,
    307: None,
    300: None,
    200: None
})

li_s = SortedDict({
    310: None,
    320: None,
    321: None,
    322: None,
    326: None,
    329: None,
    330: None,
    380: None,
    403: None
})


from bisect import bisect_left

def find_closest_elements(lst, x):
    # Sort the list to prepare for binary search
    sorted_lst = sorted(lst)
    
    # Check if x is in the list
    if x in sorted_lst:
        return x
    
    # Use bisect to find the position where x would fit
    pos = bisect_left(sorted_lst, x)
    
    # Initialize variables for lower and higher elements
    lower = None
    higher = None
    
    # Find the closest lower element
    if pos > 0:
        lower = sorted_lst[pos - 1]
    
    # Find the closest higher element
    if pos < len(sorted_lst):
        higher = sorted_lst[pos]
    
    return lower, higher



# print(li_s, li_b)

def get_best_price(price, incoming_buy=True):
    prices = li_s if incoming_buy else li_b

    percent = 2/100

    # Check if the price exists in the prices
    if price in prices:
        return price
    (lower_price, upper_price) = find_closest_elements(prices.keys(), price)   # Highest price <= price
        
           # Lowest price >= price
    l = 1 - percent
    r = 1 + percent

    print(lower_price, upper_price, price)
    # For buy orders
    if incoming_buy:

        if upper_price !=  None:
            if lower_price != None:
                return upper_price if abs(price-lower_price) > abs(price - upper_price) and price*percent > abs(price-upper_price) else lower_price
            else:
                return -1 if price*r < upper_price else upper_price
        else:
            return -1 if lower_price == None else lower_price
    # For sell orders
    else:
        if lower_price != None:
            if upper_price != None:
                return lower_price if abs(price-lower_price) < abs(price-upper_price) and abs(price-lower_price) < price*percent else upper_price
            else:
                return -1 if price*l > lower_price else lower_price

        else:
            return -1 if upper_price ==None else upper_price


print(get_best_price(324.00001, incoming_buy=True))   # Should select either 326 or a suitable lower price
print(get_best_price(329, incoming_buy=False))  # Should select either a suitable higher price or 326


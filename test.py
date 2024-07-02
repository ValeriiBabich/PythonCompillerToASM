def algorithm(start, end):
    start = int(input('start:'))
    end = int(input('end:'))
    while ((start < 0) | (end <= start)):
        print('Not correct range')
        start = int(input('start:'))
        end = int(input('end:'))
    lst = []
    for x in range(start, end):
        for i in range(2, x):
            if x % i == 0:
                break
        else:
            lst.append(x)
    try:
        lst.remove(0) 
        lst.remove(1) 
    except:
        pass
    print(sum(lst))
    
algorithm(0, 20)
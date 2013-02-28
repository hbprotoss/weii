#!/usr/bin/env python3

at_terminator = set(''' ~!@#$%^&*()+`={}|[]\;':",./<>?~！￥×（）、；：‘’“”《》？，。''')
url_legal = set('''!#$&'()*+,/:;=?@-._~'''
                + ''.join([chr(c) for c in range(ord('0'), ord('9')+1)])
                + ''.join([chr(c) for c in range(ord('a'), ord('z')+1)])
                + ''.join([chr(c) for c in range(ord('A'), ord('Z')+1)]))

def findAtEnding(src, start):
    i = start
    length = len(src)
    while(i < length):
        if src[i] in at_terminator:
            return i
        i += 1
    return i

def findUrlEnding(src, start):
    i = start
    length = len(src)
    while(i < length):
        if src[i] not in url_legal:
            return i
        i += 1
    return i

def formatLink(src):
    if src[0] == '@':
        rtn = '<a style="text-decoration:none" href="user:%s">%s</a>' % (src[1:], src)
    elif src[0] == 'h':
        rtn = '<a style="text-decoration:none" href="%s">%s</a>' % (src, src)
    else:
        rtn = src
    return rtn

def analyse(src):
    length = len(src)
    i = 0
    target = []
    try:
        while(i < length):
            if src[i] == '@':
                end = findAtEnding(src, i+1)
                target.append((i, end))
                i = end
            elif (src[i] == 'h' and src[i+1] == 't' and src[i+2] == 't' and src[i+3] == 'p'):
                if(src[i+4] == 's' and src[i+5] == ':' and src[i+6] == '/' and src[i+7] == '/'):
                    end = findUrlEnding(src, i+8)
                    target.append((i, end))
                    i = end
                elif(src[i+4] == ':' and src[i+5] == '/' and src[i+6] == '/'):
                    end = findUrlEnding(src, i+7)
                    target.append((i, end))
                    i = end
                pass
            i += 1
    except IndexError:
        pass
    
    if(len(target) == 0):
        target.append((0, len(target)+1))
    
#    for item in target:
#        print(src[item[0] : item[1]])
        
    seg_list = []
    try:
        for index,item in enumerate(target):
            seg = src[item[0] : item[1]]
            seg = formatLink(seg)
            seg_list.append(seg)
            
            seg = src[ item[1] : target[index+1][0] ]
            seg = formatLink(seg)
            seg_list.append(seg)
        pass
    except IndexError:
        seg_list.append(src[ item[1] : ])
        pass
    
    rtn = ''.join(seg_list)
    if not (target[0][0] == 0):
        rtn = src[:target[0][0]] + rtn 
    return rtn
        
if __name__ == '__main__':
    while(True):
        src = input()
        print(analyse(src))

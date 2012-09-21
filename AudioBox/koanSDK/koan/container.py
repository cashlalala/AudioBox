from event import EventManager

class List(list, EventManager):
    '''
    events:
        - Change
    '''
    def __init__(self, *argv, **argd):
        list.__init__(self, *argv, **argd)
        EventManager.__init__(self)

    def append(self, o):
        list.append(self, o)
        self.invoke('Change')

    def extend(self, o):
        list.extend(self, o)
        self.invoke('Change')

    def insert(self, i, o):
        list.insert(self, i, o)
        self.invoke('Change')

    def remove(self, o):
        list.remove(self, o)
        self.invoke('Change')

    def clear(self):
        l = len(self)
        if l:
            self.__delslice__(0,l)

    def pop(self):
        ret = list.pop(self)
        self.invoke('Change')
        return ret
        
    def __iadd__(self, o):
        ret = list.__iadd__(self, o)
        self.invoke('Change')
        return ret

    def __imul__(self, o):
        ret = list.__imul__(self, o)
        self.invoke('Change')
        return ret
                
    def __setitem__(self, index, value):
        ret = list.__setitem__(self, index, value)
        self.invoke('Change')
        return ret
        
    def __delitem__(self, index):
        ret = list.__delitem__(self, index)
        self.invoke('Change')
        return ret

    def __setslice__(self, i, j, seq):
        ret = list.__setslice__(self, i, j, seq)
        self.invoke('Change')
        return ret
        
    def __delslice__(self, i, j):    
        ret = list.__delslice__(self, i, j)
        self.invoke('Change')
        return ret



if __name__ == '__main__':
    data = List()
    
    data.append(2)
    data.extend([2,3])
    data.pop()
    data.insert(2, 4)
    data.remove(4)
    data += [11,22,33,44]
    data *= 4
    data[4] = 'hello'
    del data[4]
    data[4:10] = []
    del data[4:10]

    data.close()
    data = None

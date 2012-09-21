class Rectangle(object):
    """
    a class to ease manipulation of rectangle

    xy:         (left, top) of the rectangle
    position:   (left, top, right, buttom) of the rectangle
    rect:       (left, top, width, height) of the rectangle
    localRect:  (0, 0, width, height) of the rectangle
    size:       (width, height) of the rectangle

    @type xy: tuple of numbers
    @type position: tuple of numbers
    @type rect: tuple of numbers
    @type localRect: tuple of numbers
    @type size: tuple of numbers
    """
    def __init__(self, *args):
        if len(args) == 4:
            self.left, self.top, self.width, self.height = args
        else:
            self.left, self.top = 0, 0
            self.width, self.height = 10, 10

    def __setxy(self, p):
        self.left   = p[0]
        self.top    = p[1]
    def __getxy(self):
        return self.left, self.top
    xy = property(__getxy, __setxy)

    def __setRight(self, p):
        self.left = p - self.width
    def __getRight(self):
        return self.left + self.width
    right = property(__getRight, __setRight)
    
    def __setBottom(self, p):
        self.top = p - self.height
    def __getBottom(self):
        return self.top + self.height
    bottom = property(__getBottom, __setBottom)
    
    def __setPosition(self, p):
        self.left   = p[0]
        self.top    = p[1]
        self.width  = p[2] - p[0]
        self.height = p[3] - p[1]
    def __getPosition(self):
        return self.left, self.top, self.left + self.width, self.top + self.height
    position = property(__getPosition, __setPosition)

    def __setRect(self, p):
        self.left   = p[0]
        self.top    = p[1]
        self.width  = p[2]
        self.height = p[3]
    def __getRect(self):
        return self.left, self.top, self.width, self.height
    rect = property(__getRect, __setRect)

    def __setLocalRect(self, p):
        self.left   = 0
        self.top    = 0
        self.width  = p[2]
        self.height = p[3]
    def __getLocalRect(self):
        return 0, 0, self.width, self.height
    localRect = property(__getLocalRect, __setLocalRect)
    localPosition = property(__getLocalRect, __setLocalRect)

    def __setSize(self, s):
        self.width, self.height = s
    def __getSize(self):
        return self.width, self.height
    size = property(__getSize, __setSize)

    def ptInRect(self, x, y):
        """
        check if point(x, y) is inside the rectangle
        """
        r = self.position
        return x >= r[0] and x < r[2] and y >= r[1] and y < r[3]

    def offset(self, x, y):
        """
        move the rectangle with offset (x, y)
        """
        self.left += x
        self.top += y

    def inner(self, v):
        """
        shrink the rectangle on the four edges

        ----------------                         | <- v
        |              |         --------------
        |              |         |            |
        |              |   ->    |            |
        |              |         |            |
        |              |         --------------
        ----------------                       __
                                               ^
                                               v
        """
        self.left += v
        self.top += v
        self.width -= 2 * v
        self.height -= 2 * v

    def innerOffset(self, left, top, right, bottom):
        """
        move and resize the rectangle
        (left, top) offset the lefttop point of the rectangle
        (right, bottom) offset the rightbuttom point of the rectangle
        """
        self.left += left
        self.top += top
        self.width -= (left + right)
        self.height -= (top + bottom)

    def outter(self, v):
        """
        expand the rectangle on the four edges
        the reverse of inner
        """
        self.inner(-v)

    def outterOffset(self, left, top, right, bottom):
        self.innerOffset(-left, -top, -right, -bottom)

    def union(self, r):
        """
        calculate the union rect by two rectangles
        """
        union_rect = Rectangle()
        union_rect.left = min(self.left, r.left)
        union_rect.top = min(self.top, r.top)
        union_rect.width = max(self.left+self.width, r.left+r.width) - union_rect.left
        union_rect.height = max(self.top+self.height, r.top+r.height) - union_rect.top
        return union_rect

    def isEmpty(self):
        return self.width <= 0 or self.height <= 0

    def intersect(self, r):
        right = min(self.right, r.right)
        bottom = min(self.bottom, r.bottom)
        left = max(self.left, r.left)
        top = max(self.top, r.top)

        return Rectangle(left, top, right - left, bottom - top)
    
    

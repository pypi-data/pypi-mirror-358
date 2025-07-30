__author__ = 'DavidYdin'
__version__ = '2.1'
__email__ = 'David.2280@yandex.ru'
rules = 'vertical, horizontal, power_on_symbol, The_shutdown_symbol, movement_system'
class bin_matrix :
    def __init__(self, vertical, horizontal, power_on_symbol, The_shutdown_symbol, movement_system = False):
        self.vertical = vertical
        self.horizontal = horizontal
        self.power_on_symbol = power_on_symbol
        self.The_shutdown_symbol = The_shutdown_symbol
        self.movement_system = movement_system
        a = []
        for i in range(vertical):
            b = f"{The_shutdown_symbol} "*horizontal
            b = b[:-1]
            a += [b.split(' ')]
        self.matrix = a
        if movement_system == True:
            self.matrix[0][0] = power_on_symbol
    def show_matrix(self):
        for i in self.matrix:
            print(*i)
    def on_off_switch(self,v, h):
        if self.movement_system == False:
            if self.matrix[v-1][h-1] == self.power_on_symbol:
                self.matrix[v-1][h-1] = self.The_shutdown_symbol
            elif self.matrix[v-1][h-1] == self.The_shutdown_symbol:
                self.matrix[v-1][h-1] = self.power_on_symbol
        else:
            print("movement_system: on")
    def moving(self, direction):
        if self.movement_system == True:
            a = 0
            b = 0
            a_1 = 0
            b_1 = 0
            for x in self.matrix:
                a_1 += 1
                for y in x:
                    b_1 += 1
                    if y == self.power_on_symbol:
                        a = a_1-1
                        b = b_1-1
                b_1 = 0
            self.matrix[a][b] = self.The_shutdown_symbol
            #up down right left
            if direction == 'up':
                a -= 1
            elif direction == 'down':
                a += 1
            elif direction == 'right':
                b += 1
            elif direction == 'left':
                b -= 1
            else:
                print('Such a stand is not suitable for moving sides')
            self.matrix[a][b] = self.power_on_symbol
        else:
            print("movement_system: off")
class matrix :
    def __init__(self, vertical, horizontal, The_shutdown_symbol=0):
        self.vertical = vertical
        self.horizontal = horizontal
        self.The_shutdown_symbol = The_shutdown_symbol
        a = []
        for i in range(vertical):
            b = f"{The_shutdown_symbol} "*horizontal
            b = b[:-1]
            a += [b.split(' ')]
        self.matrix = a
    def show_matrix(self):
        for i in self.matrix:
            print(*i)
        print()
    def switch(self,v, h, simbol = 1):
        self.matrix[v-1][h-1] = simbol
    def create (self, name, def_):
        for x in range(0, self.vertical):
            for y in range(0, self.horizontal):
                def def__(x, y):
                    if def_(x, y)==None:
                        return self.The_shutdown_symbol
                    else:
                        return def_(x, y)
                name.switch(x, y, def__(x, y))
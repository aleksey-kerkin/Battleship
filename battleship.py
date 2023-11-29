from random import randint


# создаем класс-родитель для исключений
class BoardException(Exception):
    pass


#  создаем класс для вывода сшибки при попытке выстрела за поле
class BoardOutException(BoardException):
    def __str__(self):
        return (f" ───────────────────────── \n"
                "│      Вы  пытаетесь      │\n"
                "│   выстрелить за доску!  │")


# создаем класс для вывода ошибки при выстреле в занятую клетку
class BoardUsedException(BoardException):
    def __str__(self):
        return (f" ───────────────────────── \n"
                "│     Вы уже стреляли     │\n"
                "│       в эту клетку!     │")


# этот класс нам понадобится для обработки ошибки при установке кораблей в занятые клетки
class BoardWrongShipException(BoardException):
    pass


# класс для точек на игровом поле, добавлены методы для сравнения и вывода точек
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


# создание класса корабля
class Ship:
    def __init__(self, bow, length, orient):
        self.bow = bow
        self.length = length
        self.orient = orient
        self.lives = length

    # свойство класса для создания списка точек в которых находятся корабли
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            point_x = self.bow.x
            point_y = self.bow.y

            if self.orient == 0:
                point_x += i

            elif self.orient == 1:
                point_y += i

            ship_dots.append(Dot(point_x, point_y))

        return ship_dots

    def shots(self, shot):
        return shot in self.dots


# создание игрового поля
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["☐"] * size for _ in range(size)]

        self.occupied = []
        self.ships = []

    # метод для добавления корабля на доску
    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.occupied:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.occupied.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # метод для автоматического обвода контура корабля
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                point = Dot(d.x + dx, d.y + dy)
                if not (self.out(point)) and point not in self.occupied:
                    if verb:
                        self.field[point.x][point.y] = "•"
                    self.occupied.append(point)

    # этот дандер рисует саму доску, скрывая игровое поле противника и отображая поле игрока
    def __str__(self):
        res = ""
        res += "  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} │ {' │ '.join(row)} │"

        if self.hid:
            res = res.replace("■", "☐")
        return res

    # метод для определения координат за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # метод выстрела и проверки клетки на наличие кораблей, так же считает жизни кораблей,
    # отмечает попадания и выводит сообщения о подбитии, промахе или потоплении кораблей
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.occupied:
            raise BoardUsedException()

        self.occupied.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print(" ───────────────────────── \n"
                          "│    Корабль  потоплен!   │")
                    return False
                else:
                    print(" ───────────────────────── \n"
                          "│     Корабль подбит!     │")
                    return True

        self.field[d.x][d.y] = "•"
        print(" ───────────────────────── \n"
              "│         Промах!         │\n"
              " ───────────────────────── ")
        return False

    def begin(self):
        self.occupied = []

    def defeat(self):
        return self.count == len(self.ships)


# создание родительского класса игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# создание класса ИИ путем наследования
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"│   Ход компьютера: {d.x + 1} {d.y + 1}   │")
        return d


# создание класса пользователя путем наследования
# создание внешней логики и интерфейса пользователя
class User(Player):
    def ask(self):
        while True:
            coords = input(" ───────────────────────── \n"
                           "│       Ваш выстрел:      │\n"
                           " ───────────────────────── \n"
                           "            ").split()

            if len(coords) != 2:
                print(" ───────────────────────── \n"
                      "│  Введите 2 координаты!  │\n"
                      " ───────────────────────── ")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" ───────────────────────── \n"
                      "│     Введите  числа!     │\n"
                      " ───────────────────────── ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# класс самой игры, случайная расстановка кораблей
# на полях для ИИ и для пользователя, их размерность и количество
class Game:
    def __init__(self, size=6):
        self.size = size
        self.lengths = [3, 2, 2, 1, 1, 1, 1]
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.user = User(player, computer)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # метод для случайной расстановки кораблей
    def random_place(self):

        board = Board(size=self.size)
        attempts = 0
        for length in self.lengths:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # метод для приветственного сообщения
    def greet(self):
        print(" ───────────────────────── \n"
              "│     Добро пожаловать    │\n"
              "│          в игру         │\n"
              "│       Морской Бой       │\n"
              " ───────────────────────── \n"
              "│       Формат ввода:     │\n"
              "│            x y          │\n"
              "│     x - номер столбца   │\n"
              "│     y - номер строки    │"
              )

    def print_boards(self):
        print(" ───────────────────────── \n"
              "│    Доска пользователя:  │\n"
              " ───────────────────────── ")
        print(self.user.board)
        print(" ───────────────────────── \n"
              "│    Доска компьютера:    │\n"
              " ───────────────────────── ")
        print(self.ai.board)
        print(" ───────────────────────── \n")

    # запуск цикла игры, очередность ходов и определение победителя
    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print(" ───────────────────────── \n"
                      "│   Ходит пользователь.   │")
                repeat = self.user.move()
            else:
                print(" ───────────────────────── \n"
                      "│     Ходит компьютер.    │\n"
                      " ───────────────────────── ")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print(" ───────────────────────── \n")
                self.print_boards()
                print(" ───────────────────────── \n"
                      "│  Пользователь выиграл!  │\n"
                      " ───────────────────────── \n")
                break

            if self.user.board.defeat():
                print(" ───────────────────────── \n")
                self.print_boards()
                print(" ───────────────────────── \n")
                print(" ───────────────────────── \n"
                      "│    Компьютер выиграл!   │\n"
                      " ───────────────────────── \n")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


# создание и запуск игры
game = Game()
game.start()

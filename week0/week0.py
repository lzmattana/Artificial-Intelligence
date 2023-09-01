import sys

class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():

    def __init__(self, filename):

        # Lê o arquivo e define a altura e largura do labirinto
        with open(filename) as f:
            contents = f.read()

        # Valida o ponto de partida e o objetivo
        if contents.count("A") != 1:
            raise Exception("o labirinto deve ter exatamente um ponto de partida")
        if contents.count("B") != 1:
            raise Exception("o labirinto deve ter exatamente um objetivo")

        # Determina a altura e largura do labirinto
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Acompanha as paredes
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None


    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    def neighbors(self, state):
        row, col = state
        candidates = [
            ("cima", (row - 1, col)),
            ("baixo", (row + 1, col)),
            ("esquerda", (row, col - 1)),
            ("direita", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result


    def solve(self):
        """Encontra uma solução para o labirinto, se existir."""

        # Acompanha o número de estados explorados
        self.num_explored = 0

        # Inicializa a fronteira apenas com a posição de partida
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Inicializa um conjunto vazio de estados explorados
        self.explored = set()

        # Continua até encontrar uma solução
        while True:

            # Se a fronteira estiver vazia, não há caminho
            if frontier.empty():
                raise Exception("sem solução")

            # Escolhe um nó da fronteira
            node = frontier.remove()
            self.num_explored += 1

            # Se o nó for o objetivo, encontramos uma solução
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Marca o nó como explorado
            self.explored.add(node.state)

            # Adiciona vizinhos à fronteira
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)


    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Cria um canvas em branco
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Paredes
                if col:
                    fill = (40, 40, 40)

                # Início
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Objetivo
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solução
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explorado
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Célula vazia
                else:
                    fill = (237, 240, 252)

                # Desenha a célula
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


if len(sys.argv) != 2:
    sys.exit("Uso: python maze.py maze.txt")

m = Maze(sys.argv[1])

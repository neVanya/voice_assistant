import random
import logging
from config.settings import Settings

logger = logging.getLogger('VoiceAssistant')


class TicTacToe:
    """Класс игры в крестики-нолики (ваш код)"""

    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.board = [str(i + 1) for i in range(9)]  # ["1", "2", "3", ... "9"]
        self.current_player = "X"  # Игрок всегда X
        self.game_active = False

    def get_board_description(self):
        """Описывает доску голосом"""
        description = "Текущая доска: \n"
        for i in range(0, 9, 3):
            row = []
            for j in range(3):
                cell = self.board[i + j]
                if cell == "X":
                    row.append("X")
                elif cell == "O":
                    row.append("O")
                else:
                    row.append(f"{i + j + 1}")
            description += f"{' | '.join(row)}\n"
        return description

    def make_player_move(self, position):
        """Ход игрока"""
        try:
            pos = int(position) - 1
            if 0 <= pos <= 8 and self.board[pos] not in ["X", "O"]:
                self.board[pos] = "X"
                self.current_player = "O"
                return True, "Отличный ход!"
            return False, "Неверная клетка или она уже занята!"
        except:
            return False, "Скажите номер от 1 до 9"

    def make_ai_move(self):
        """Ход компьютера"""
        # Сначала проверяем выигрышный ход
        for i in range(9):
            if self.board[i] not in ["X", "O"]:
                self.board[i] = "O"
                if self.check_winner() == "O":
                    return i + 1
                self.board[i] = str(i + 1)

        # Блокируем игрока
        for i in range(9):
            if self.board[i] not in ["X", "O"]:
                self.board[i] = "X"
                if self.check_winner() == "X":
                    self.board[i] = "O"
                    return i + 1
                self.board[i] = str(i + 1)

        # Центр
        if self.board[4] not in ["X", "O"]:
            self.board[4] = "O"
            return 5

        # Углы
        corners = [0, 2, 6, 8]
        for corner in corners:
            if self.board[corner] not in ["X", "O"]:
                self.board[corner] = "O"
                return corner + 1

        # Любая свободная клетка
        for i in range(9):
            if self.board[i] not in ["X", "O"]:
                self.board[i] = "O"
                return i + 1

        return None

    def check_winner(self):
        """Проверяет победителя"""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Горизонтали
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Вертикали
            [0, 4, 8], [2, 4, 6]  # Диагонали
        ]

        for line in lines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]]:
                return self.board[line[0]]

        if all(cell in ["X", "O"] for cell in self.board):
            return "D"  # Ничья

        return None

    def get_game_state(self):
        """Возвращает текущее состояние игры"""
        winner = self.check_winner()
        if winner == "X":
            return "player_win", "Поздравляю! Вы выиграли! 🎉"
        elif winner == "O":
            return "ai_win", "Я выиграл! Попробуйте еще раз! 🤖"
        elif winner == "D":
            return "draw", "Ничья! Хорошая игра! 🤝"
        else:
            return "continue", self.get_board_description()


class GameEngine:
    """Движок для управления играми"""

    def __init__(self):
        self.tic_tac_toe = TicTacToe()
        self.current_game = None
        self.game_active = False

    def start_tic_tac_toe(self):
        """Начинает новую игру в крестики-нолики"""
        self.tic_tac_toe.reset_game()
        self.tic_tac_toe.game_active = True
        self.current_game = "tic_tac_toe"
        self.game_active = True

        start_text = """
        Начинаем игру в Крестики-нолики!
        Вы играете крестиками, я - ноликами.
        Сетка клеток:
         1 | 2 | 3
        -----------
         4 | 5 | 6
        -----------  
         7 | 8 | 9
        Скажите номер клетки от 1 до 9 для вашего хода.
        """

        print(start_text)
        return "Начинаем игру в Крестики-нолики! Вы играете крестиками, я - ноликами. Скажите номер клетки от 1 до 9 для вашего хода."

    def extract_move_from_text(self, text):
        """Извлекает номер хода из текста (ваш код)"""
        text = text.lower().strip()

        # Словарь для преобразования слов в цифры
        number_words = {
            "один": "1", "два": "2", "три": "3", "четыре": "4", "пять": "5",
            "шесть": "6", "восемь": "8", "семь": "7", "девять": "9",
            "первый": "1", "второй": "2", "третий": "3", "четвертый": "4",
            "пятый": "5", "шестой": "6", "седьмой": "7", "восьмой": "8", "девятый": "9",
            "раз": "1"
        }

        # Убираем лишние слова
        remove_words = ['номер', 'клетка', 'клетку', 'ставь', 'поставь', 'ход']
        for word in remove_words:
            text = text.replace(word, '').strip()

        # 1. Ищем слова-числа
        for word, number in number_words.items():
            if word in text:
                return number

        # 2. Ищем цифры в тексте
        for char in text:
            if char.isdigit() and 1 <= int(char) <= 9:
                return char

        # 3. Ищем числа (например, "восемь")
        words = text.split()
        for word in words:
            if word in number_words:
                return number_words[word]

        return None

    def process_game_input(self, text):
        """Обрабатывает ввод в активной игре и возвращает (ответ, игра_продолжается)"""
        if not self.game_active:
            return None, False

        text = text.lower()

        # Выход из игры
        if any(word in text for word in ['стоп', 'выход', 'закончить игру', 'хватит', 'выйти', 'закончить']):
            self.game_active = False
            self.current_game = None
            return "Выхожу из игры. Можете продолжить общение!", False

        # Обработка крестиков-ноликов
        if self.current_game == "tic_tac_toe":
            # Извлекаем номер хода из текста
            move = self.extract_move_from_text(text)

            if not move:
                available_moves = [str(i + 1) for i in range(9) if self.tic_tac_toe.board[i] not in ["X", "O"]]
                return f"Не понял ход. Скажите номер клетки от 1 до 9. Свободные клетки: {', '.join(available_moves)}", True

            # Обрабатываем ход и получаем статус продолжения игры
            response, game_continues = self._process_tic_tac_toe_move(move)

            # Обновляем статус игры
            if not game_continues:
                self.game_active = False
                self.current_game = None

            return response, game_continues

        return None, False

    def _process_tic_tac_toe_move(self, position):
        """Обрабатывает ход в крестики-нолики"""
        if not self.tic_tac_toe.game_active:
            return "Игра не активна. Скажите 'начать игру' чтобы играть в крестики-нолики", False

        try:
            # Ход игрока
            success, message = self.tic_tac_toe.make_player_move(position)
            if not success:
                # Добавляем больше информации о доступных ходах
                available_moves = [str(i + 1) for i in range(9) if self.tic_tac_toe.board[i] not in ["X", "O"]]
                if available_moves:
                    return f"{message}. Свободные клетки: {', '.join(available_moves)}", True
                else:
                    return message, True

            # Проверяем состояние после хода игрока
            state, state_message = self.tic_tac_toe.get_game_state()
            if state != "continue":
                self.tic_tac_toe.game_active = False
                return state_message, False

            # Ход компьютера
            ai_move = self.tic_tac_toe.make_ai_move()
            if ai_move:
                state, state_message = self.tic_tac_toe.get_game_state()
                response = f"Я ставлю нолик в клетку {ai_move}. {state_message}"
                if state != "continue":
                    self.tic_tac_toe.game_active = False
                    return response, False
                return response, True

            return "Что-то пошло не так", False

        except Exception as e:
            return f"Ошибка при обработке хода: {e}", False

    def get_game_status(self):
        """Возвращает статус текущей игры"""
        if not self.game_active:
            return "Сейчас нет активной игры."

        if self.current_game == "tic_tac_toe":
            return self.tic_tac_toe.get_board_description()

        return f"Активна игра: {self.current_game}"

    def is_game_command(self, text):
        """Проверяет, является ли команда игровой"""
        text = text.lower()

        # Команды начала игр
        start_commands = ['крестики нолики', 'начать игру', 'играть в крестики', 'хочу играть']
        if any(cmd in text for cmd in start_commands):
            return True

        # Команды статуса
        status_commands = ['статус игры', 'ход игры', 'поле', 'доска', 'какое поле']
        if any(cmd in text for cmd in status_commands):
            return True

        # В игровом режиме ВСЕ команды считаются игровыми
        if self.game_active:
            return True

        return False


# Глобальный экземпляр игрового движка
game_engine = GameEngine()
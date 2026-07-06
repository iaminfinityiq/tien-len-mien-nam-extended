from __future__ import annotations
from os import system
from typing import List, Self, Callable

def cls() -> None:
    system("clear")

def petc() -> None:
    input("Nhấn enter để tiếp tục...")

def instruct(instruction: str, inputs: List[str] = []) -> List[str]:
    returned: List[str] = []
    
    cls()
    print(instruction)
    for inp in inputs:
        returned += [input(inp)]

    petc()    
    return returned

def remind(message: str) -> None:
    print(message)
    petc()

class Player:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.hp: int = 1
        self.melee: int = 1
        self.efficiency: int = 1
        self.economy: int = 100
        self.money: int = 0
        self.troops: int = 1_000_000

        self.hp_upgrade_price: int = 100
        self.melee_upgrade_price: int = 100
        self.efficiency_upgrade_price: int = 500
        self.economy_upgrade_price: int = 600
    
    def upgrade_hp(self) -> bool:
        if self.money < self.hp_upgrade_price:
            remind(f"{self.name}, bạn hiện đang không có đủ tiền để nâng phòng thủ, bạn hiện đang thiếu {self.hp_upgrade_price - self.money}000 VND nữa để nâng cấp")
            return False
        
        self.money -= self.hp_upgrade_price
        self.hp += 1
        self.hp_upgrade_price += 100
        remind(f"{self.name}, bạn đã nâng cấp phòng thủ thành công")
        return True
    
    def upgrade_melee(self) -> bool:
        if self.money < self.melee_upgrade_price:
            remind(f"{self.name}, bạn hiện đang không có đủ tiền để nâng sát thương, bạn hiện đang thiếu {self.melee_upgrade_price - self.money}000 VND nữa để nâng cấp")
            return False
        
        self.money -= self.melee_upgrade_price
        self.melee += 1
        self.melee_upgrade_price += 100
        remind(f"{self.name}, bạn đã nâng cấp sát thương thành công")
        return True
    
    def upgrade_efficiency(self) -> bool:
        if self.money < self.efficiency_upgrade_price:
            remind(f"{self.name}, bạn hiện đang không có đủ tiền để nâng hiệu suất, bạn hiện đang thiếu {self.efficiency_upgrade_price - self.money}000 VND nữa để nâng cấp")
            return False
        
        self.money -= self.efficiency_upgrade_price
        self.efficiency += 1
        self.efficiency_upgrade_price += 500
        remind(f"{self.name}, bạn đã nâng cấp hiệu suất thành công")
        return True
    
    def upgrade_economy(self) -> bool:
        if self.money < self.economy_upgrade_price:
            remind(f"{self.name}, bạn hiện đang không có đủ tiền để nâng kinh tế, bạn hiện đang thiếu {self.economy_upgrade_price - self.money}000 VND nữa để nâng cấp")
            return False
        
        self.money -= self.economy_upgrade_price
        self.economy += 100
        self.economy_upgrade_price += 600
        remind(f"{self.name}, bạn đã nâng cấp kinh tế thành công")
        return True

class Cell:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.troops_per_player: List[int] = [0, 0]
        self.paths: List[Self] = []
    
    def add_path(self, other: Self) -> None:
        self.paths += [other]
        other.paths += [self]
    
    def add_troops(self, turn: int, amount: int) -> None:
        self.troops_per_player[turn] += amount

    def move_troops(self, player_name: str, turn: int, amount: int, cell: Self) -> bool:
        if self.troops_per_player[turn] == 0:
            remind(f"{player_name}, bạn không có quân ở {self.name}")
            return False
        
        if amount > self.troops_per_player[turn]:
            remind(f"{player_name}, bạn không thể di chuyển số quân vượt mức số quân ở ô")
            return False
        
        if amount == 0:
            remind(f"{player_name}, bạn không thể di chuyển 0 quân")
            return False
        
        if cell not in self.paths:
            remind(f"{player_name}, bạn không thể di chuyển quân của mình ra {cell.name}, một ô không nằm bên cạnh {self.name}")
            return False
        
        self.troops_per_player[turn] -= amount
        cell.troops_per_player[turn] += amount
        remind(f"{player_name}, bạn đã thành công di chuyển {amount} quân ra {cell.name}")
        return True
    
    def trigger_battle(self, players: List[Player]) -> None:
        if 0 in self.troops_per_player:
            return
        
        hits: List[int] = [-(-players[i].hp // players[1-i].melee) for i in range(2)]
        loss: List[int] = [self.troops_per_player[1-i] // hits[i] for i in range(2)]
        for i in range(2):
            if loss[i] > self.troops_per_player[i]:
                players[i].troops -= self.troops_per_player[i]
                self.troops_per_player[i] = 0
            else:
                players[i].troops -= loss[i]
                self.troops_per_player[i] -= loss[i]
        
        for i in range(2):
            if self.troops_per_player[1-i] == 0:
                remind(f"{players[i].name} đã tiêu diệt hết quân của {players[1-i].name} trong {self.name}")

class Action:
    def __init__(self, name: str, game: Game, functionality: Callable[[Game], bool], lose_action: bool = True) -> None:
        self.name: str = name
        self.game: Game = game
        self.functionality: Callable[[Game], bool] = functionality
        self.lose_action: bool = lose_action
    
    def do(self) -> bool:
        return self.functionality(self.game)

def visit(game: Game) -> bool:
    player: Player = game.players[game.turn]
    paths: List[Cell] = game.watching_cell.paths
    cls()
    print(f"{player.name}, bạn hiện chỉ có thể ghé thăm những địa điểm sau:")
    for i, cell in enumerate(paths):
        print(f"[{i+1}] {cell.name}")
    
    choice: str = input(f"\nNhập một số từ 1 đến {len(paths)} để chọn thành phố mình muốn ghé thăm hoặc để trống để quay về màn hình chính: ").strip()
    if choice == "":
        return False
    
    if not all(char in "0123456789" for char in choice):
        remind(f"{player.name}, {choice} không phải là một con số hợp lệ")
        return False
    
    index: int = int(choice)
    if index <= 0 or index > len(paths):
        remind(f"{player.name}, {choice} không phải là một con số hợp lệ")
        return False
    
    game.watching_cell = paths[index-1]
    return True

def upgrade_hp(game: Game) -> bool:
    player: Player = game.players[game.turn]
    return player.upgrade_hp()

def upgrade_melee(game: Game) -> bool:
    player: Player = game.players[game.turn]
    return player.upgrade_melee()

def upgrade_efficiency(game: Game) -> bool:
    player: Player = game.players[game.turn]
    return player.upgrade_efficiency()

def upgrade_economy(game: Game) -> bool:
    player: Player = game.players[game.turn]
    return player.upgrade_economy()

class Game:
    def __init__(self, player_names: List[str]) -> None:
        self.players: List[Player] = [Player(name) for name in player_names]
        self.turn: int = 0
        self.actions: int = 0
        self.generate_map()
    
    def generate_map(self) -> None:
        hanoi: Cell = Cell("Hà Nội")
        trieu_son_1: Cell = Cell("Triệu Sơn 1")
        trieu_son_2: Cell = Cell("Triệu Sơn 2")
        quang_tri: Cell = Cell("Quảng Trị")
        co_do_2: Cell = Cell("Cờ Đỏ 2")
        co_do_1: Cell = Cell("Cờ Đỏ 1")
        nong_cong_1: Cell = Cell("Nông Cống 1")
        nong_cong_2: Cell = Cell("Nông Cống 2")
        hue: Cell = Cell("Huế")
        thoi_lai_2: Cell = Cell("Thới Lai 2")
        thoi_lai_1: Cell = Cell("Thới Lai 1")
        tinh_gia_1: Cell = Cell("Tĩnh Gia 1")
        tinh_gia_2: Cell = Cell("Tĩnh Gia 2")
        da_nang: Cell = Cell("Đà Nẵng")
        o_mon_2: Cell = Cell("Ô Môn 2")
        o_mon_1: Cell = Cell("Ô Môn 1")
        saigon: Cell = Cell("Sài Gòn")

        hanoi.add_path(trieu_son_1)
        hanoi.add_path(nong_cong_1)
        hanoi.add_path(tinh_gia_1)
        trieu_son_1.add_path(trieu_son_2)
        nong_cong_1.add_path(nong_cong_2)
        tinh_gia_1.add_path(tinh_gia_2)
        trieu_son_2.add_path(quang_tri)
        nong_cong_2.add_path(hue)
        tinh_gia_2.add_path(da_nang)
        saigon.add_path(co_do_1)
        saigon.add_path(thoi_lai_1)
        saigon.add_path(o_mon_1)
        co_do_1.add_path(co_do_2)
        thoi_lai_1.add_path(thoi_lai_2)
        o_mon_1.add_path(o_mon_2)
        co_do_2.add_path(quang_tri)
        thoi_lai_2.add_path(hue)
        o_mon_2.add_path(da_nang)
        quang_tri.add_path(hue)
        hue.add_path(da_nang)

        self.capitals: List[Cell] = [hanoi, saigon]
        self.centers: List[Cell] = [quang_tri, hue, da_nang]
        self.cells: List[Cell] = [hanoi, trieu_son_1, trieu_son_2, quang_tri, co_do_2, co_do_1, nong_cong_1, nong_cong_2, hue, thoi_lai_2, thoi_lai_1, tinh_gia_1, tinh_gia_2, da_nang, o_mon_2, o_mon_1, saigon]
    
    def before_action(self) -> None:
        cls()
        for cell in self.cells:
            cell.trigger_battle(self.players)
        
        self.players[self.turn].money += self.players[self.turn].economy
    
    def perform_action(self) -> None:
        self.watching_cell: Cell = self.capitals[self.turn]
        player: Player = self.players[self.turn]
        while True:
            cls()
            actions: List[Action] = [Action("Ghé thăm địa điểm kế bên", self, visit, False), Action("Nâng cấp phòng thủ", self, upgrade_hp), Action("Nâng cấp sát thương", self, upgrade_melee), Action("Nâng cấp hiệu suất", self, upgrade_efficiency), Action("Nâng cấp kinh tế", self, upgrade_economy)]
            print(f"""Chào mừng {player.name}, bạn hiện đang quan sát vùng đất {self.watching_cell.name}

------------------------
| THÔNG TIN NGƯỜI CHƠI |
------------------------
Bạn hiện đang còn {player.troops} quân trong trận
Tiền: {player.money}000 VND
Phòng thủ: Cấp độ {player.hp}
Sát thương: Cấp độ {player.melee}
Hiệu suất: Cấp độ {player.efficiency}
Kinh tế: Nhận {player.economy}000 VND trước mỗi hành động của hai người chơi

----------------------------------
| SỰ KIỆN ĐANG XẢY RA Ở VÙNG ĐẤT |
----------------------------------
Có {self.watching_cell.troops_per_player[self.turn]} quân của bạn và {self.watching_cell.troops_per_player[1-self.turn]} quân của đối thủ đang ở {self.watching_cell.name}
Hiện tại đang{' không' if 0 in self.watching_cell.troops_per_player else ''} xảy ra xung đột ở vùng đất này

----------------
| CÁC NÂNG CẤP |
----------------
Phòng thủ (Cấp độ {player.hp} -> {player.hp+1}): {player.hp_upgrade_price}000 VND
Sát thương (Cấp độ {player.melee} -> {player.melee+1}): {player.melee_upgrade_price}000 VND
Hiệu suất (Cấp độ {player.efficiency} -> {player.efficiency+1}): {player.efficiency_upgrade_price}000 VND
Kinh tế (Nhận {player.economy}000 VND -> {player.economy+100}000 VND trước mỗi lượt hành động của mỗi người chơi): {player.economy_upgrade_price}000 VND

-------------
| HÀNH ĐỘNG |
-------------
Bạn hiện có thể thực hiện {self.actions}/{player.efficiency} hành động trong lượt của mình. Có một số hành động sẽ không tiêu hao số lượng hành động bạn có thể làm. Những hành động bạn có thể làm gồm:
""")
            
            for i, action in enumerate(actions):
                print(f"[{i+1}] {action.name}")
            
            choice: str = input(f"\nNhập một số từ 1 đến {len(actions)} để thực hiện hành động bạn muốn làm: ")
            if not choice or not all(char in "0123456789" for char in choice):
                remind(f"{player.name}, {choice} không phải là một con số hợp lệ")
                continue
            
            index: int = int(choice)
            if index <= 0 or index > len(actions):
                remind(f"{player.name}, {choice} không phải là một con số hợp lệ")
                continue

            action: Action = actions[index-1]
            result: bool = action.do()
            if result and action.lose_action:
                break

    def perform_turn(self) -> None:
        player: Player = self.players[self.turn]
        instruct(f"Đang là lượt của {player.name}, hãy đưa máy cho họ")

        self.actions = player.efficiency
        self.before_action()
        while self.actions != 0:
            self.perform_action()
            self.actions -= 1

        self.turn = 1 - self.turn

instruct("Chào mừng các bạn đến với Tiến lên Miền Nam mở rộng")
instruct("Trước khi chơi, chúng ta cần phải biết luật chơi của trò này")
instruct("Đầu tiên, chúng ta cần 2 người chơi")
player_names: List[str] = instruct("Đầu tiên, chúng ta cần 2 người chơi", ["P1: ", "P2: "])
instruct(f"""Chúng ta sẽ chơi trên bản đồ sau:
              --- Hà Nội ---
            /       |        \\
Triệu Sơn 1   Nông Cống 1     Tĩnh Gia 1
     |              |              |
Triệu Sơn 2   Nông Cống 2     Tĩnh Gia 2
     |              |              |
 Quảng Trị ------- Huế -------- Đà Nẵng
     |              |              |
  Cờ Đỏ 2      Thới Lai 2       Ô Môn 2
     |              |              |
  Cờ Đỏ 1      Thới Lai 1       Ô Môn 1
          \\         |         /
            ---- Sài Gòn ----

{player_names[0]} có thủ đô là Hà Nội, còn {player_names[1]} có thủ đô là Sài Gòn""")
instruct(f"Mỗi bên lực lượng có 1 triệu quân\n{player_names[0]} sẽ sắp xếp các quân của mình ở Hà Nội, Triệu Sơn 1, Nông Cống 1 và Tĩnh Gia 1\nCòn {player_names[1]} sẽ sắp xếp các quân của mình ở Sài Gòn, Cờ Đỏ 1, Thới Lai 1 và Ô Môn 1")
instruct("Trong lượt của mình, người chơi có thể nâng cấp lực lượng để chống lại quân của đối thủ, hoặc di chuyển một số quân ở một ô nhất định sang ô kế bên")
instruct("Nếu ở một ô có quân của cả hai bên thì tất cả các quân của ô đấy sẽ đánh nhau. Việc tăng số lượng quân và các thuộc tính khác sẽ giúp bạn tiêu diệt nhiều quân hơn\nSẽ có khả năng sau khi đánh nhau thì cả hai bên vẫn còn quân, hoặc tất cả các quân của cả hai bên đều bị tiêu diệt")
instruct("Nhiệm vụ của cả hai bên là đưa quân tới thủ đô của đối thủ và tiêu diệt hết các quân đang ở thủ đô")
instruct("Chúc may mắn...")

game: Game = Game(player_names)
while True:
    game.perform_turn()
import logging
import sys
from enum import Enum
from random import randint, choice
from typing import Union, Tuple, Dict, Any

class CharacterType(Enum):
    TANK = 1
    SUPPORT = 2
    DPS = 3

class ItemCategory(Enum):
    SPIRIT = 1
    HEALTH = 2
    GUN = 3

class ItemType(Enum):
    MOVEMENT = 0
    RESIST = 1
    MELEE = 2
    SPIRIT = 3
    GUN = 4
    SUSTAIN = 6

class StatKey(Enum):
    HEALTH = 0
    SPIRITPOWER = 1
    STAMINA = 2
    BULLETDAMAGE = 3
    AMMO = 4
    BPS = 5
    HEALTH_REGEN = 6
    MOVE_SPEED = 7
    SPIRIT_LIFESTEAL = 8

class ItemMode(Enum):
    ADD = 1
    MULTIPLY = 2

class Teams(Enum):
    ARCH_MOTHER = 1
    HIDDEN_KING = 2

class Choices(Enum):
    calculate_item_to_buy = 1
    check_teams = 2
    next_phase = 3
    exit = 4

Effect = Tuple[ItemMode, float]
class Item:
    def __init__(self, name, price, item_category: ItemCategory, stats: Dict[StatKey, Effect], item_type: ItemType):
        self.itemCategory = item_category
        self.name = name
        self.price = price
        self.stats: Dict[StatKey, Effect] = stats
        self.itemType = item_type

class Character:
    def __init__(
            self, name, characterType, stats: dict, currentSouls=0, current_items: list[Item]=None, statWeights: dict=None,
            typeWeights: dict=None):

        self.statWeights = {
            StatKey.HEALTH: 1.0,
            StatKey.SPIRITPOWER: 1.0,
            StatKey.STAMINA: 1.0,
            StatKey.BULLETDAMAGE: 1.0,
            StatKey.AMMO: 1.0,
            StatKey.BPS: 1.0,
            StatKey.HEALTH_REGEN: 1.0,
            StatKey.MOVE_SPEED: 1.0,
            StatKey.SPIRIT_LIFESTEAL: 1.0,
        }

        self.typeWeights = {
            ItemType.MOVEMENT: 1.0,
            ItemType.RESIST: 1.0,
            ItemType.MELEE: 1.0,
            ItemType.SPIRIT: 1.0,
            ItemType.GUN: 1.0,
            ItemType.SUSTAIN: 1.0,
        }

        if current_items is None:
            current_items = []
        # TODO Endre intersection, kanskje til within
        if statWeights is not None:
            assert set(StatKey).intersection(set(statWeights)), "Stat weights must contain at least one of StatKey"
            self.statWeights.update(statWeights)

        if typeWeights is not None:
            assert set(ItemType).intersection(set(typeWeights)), "Stat weights must contain at least one of StatKey"
            self.typeWeights.update(typeWeights)

        self.currentItems = current_items
        self.currentSouls = currentSouls
        self.name = name
        self.characterType = characterType
        self.stats = stats

        assert self.stats.keys() == set(StatKey), "Stats must be a dict of StatKey"
        assert self.statWeights.keys() == set(StatKey), "Stats must be a dict of StatKey"

    def buyitem(self, newitem):
        if newitem.price > self.currentSouls:
            return

        if newitem in self.currentItems:
            return

        self.currentSouls -= newitem.price
        self.currentItems.append(newitem)
        for key_idx, multiplier in newitem.stats.items():
            stat_key = StatKey(key_idx) if isinstance(key_idx, int) else key_idx

            if stat_key not in self.stats:
                continue

            if multiplier[0] == ItemMode.ADD:
                self.stats[stat_key] += multiplier[1]
            elif multiplier[0] == ItemMode.MULTIPLY:
                self.stats[stat_key] *= multiplier[1]

    def print_stats(self):
        print(self.name, "Stats:")
        for key, value in self.stats.items():
            print(key.name,": ", value)

    def print_stat_weights(self):
        print(self.name, "Stat weights:")
        for key, value in self.statWeights.items():
            print(key.name,": ", value)

    def print_type_weights(self):
        print(self.name, "Type weights:")
        for key, value in self.typeWeights.items():
            print(key.name,": ", value)

def relative_stat_increase(character: Character, item: Item):
    total_percent = 0.0
    for key_idx, (mode, val) in item.stats.items():
        key = StatKey(key_idx) if isinstance(key_idx, int) else key_idx
        old = float(character.stats.get(key, 0.0))
        baseline = old if old != 0.0 else 1.0
        if mode == ItemMode.ADD:
            new = old + val
        else:
            new = old * val
        total_percent += (new - baseline) / baseline * 100.0
    return total_percent

def calculate_item_to_buy(character: Character, possible_items: list[Item], debug=False):
    best_item: Tuple[Any, float] = (None, float('-inf'))

    for i in possible_items:
        if i in character.currentItems:
            continue

        save_weight = 1.0
        compound_stat_weight = 1.0

        for key_idx in i.stats.keys():
            stat_key = StatKey(key_idx) if isinstance(key_idx, int) else key_idx
            if stat_key not in character.statWeights:
                continue
            compound_stat_weight *= character.statWeights.get(stat_key, 1.0)

        if i.price > character.currentSouls:
            save_weight = character.currentSouls / i.price

        increase = relative_stat_increase(character, i)
        weighted_increase = increase * save_weight * compound_stat_weight * character.typeWeights.get(i.itemType, 1.0)

        if weighted_increase > best_item[1]:
            best_item = (i, weighted_increase)

        if debug:
            print(
                f"{i.name} | price = {i.price} | save weight = {save_weight:.3f} | compound weight = {compound_stat_weight:.3f} "
                f"| compound percent stat increase = {increase:.2f}% | weighted score = {weighted_increase:.3f} |")

    return best_item[0]
class User:
    time = 0.0
    Arch_Mother: set["User"] = set()
    Hidden_King: set["User"] = set()

    @classmethod
    def get_all_players(cls) -> set["User"]:
        return cls.Arch_Mother | cls.Hidden_King

    def __init__(self, character: Character, kills: int = 0, deaths: int = 0, assists: int = 0):
        if not character:
            raise ValueError("Character cannot be None")

        self.character = character
        self.kills = kills
        self.deaths = deaths
        self.assists = assists

    def add_to_team(self, team: Teams, debug=False) -> None:
        team_sets = {
            Teams.ARCH_MOTHER: User.Arch_Mother,
            Teams.HIDDEN_KING: User.Hidden_King
        }
        target_team = team_sets[team]
        temp_arch = User.Arch_Mother.copy()
        temp_hidden = User.Hidden_King.copy()

        if team not in team_sets:
            raise ValueError("Invalid team. Must be Teams.ARCH_MOTHER or Teams.HIDDEN_KING")

        if self in target_team:
            if debug:
                logging.error(f"{self.character.name} is already in {team.name}.")
            return

        if len(target_team) >= 5:
            if debug:
                logging.error(f"{team.name} is full. Cannot add more members.")
            return

        if team == Teams.ARCH_MOTHER:
            temp_arch.add(self)
        else:
            temp_hidden.add(self)

        if not temp_arch.isdisjoint(temp_hidden):
            if debug:
                logging.error('Arch Mother and Hidden King would have overlapping members.')
            return

        target_team.add(self)

        if debug:
            print(f"Added {self.character.name} to {team.name}")
    def check_team_membership(self) -> Teams:
        if self in User.Arch_Mother:
            return Teams.ARCH_MOTHER
        elif self in User.Hidden_King:
            return Teams.HIDDEN_KING
        else:
            raise ValueError("Not part off any team.")
    def add_weight(self, itemType, updated_value, debug=False) -> None:
        old = self.character.typeWeights.get(itemType)
        print(f"Old weight for {itemType}: {old}")
        if old is None:
            print(f"[WARN] Missing key in typeWeights for {itemType} -> creating with 0.0")
            old = 0.0
        self.character.typeWeights[itemType] = old + updated_value
        if debug:
            print(f"Updated {itemType}: {old} -> {self.character.typeWeights[itemType]}")

    def is_fed_calc(self, debug=False) -> None:
        selfkda = (self.kills + (self.assists / 2)) / max(1, self.deaths)
        team_check = self.check_team_membership()
        team_variable = User.Arch_Mother if team_check == Teams.ARCH_MOTHER else User.Hidden_King
        teammates = [user for user in team_variable if user is not self]
        if len(teammates) == 0:
            raise ValueError(f"No teammates to compare for {self.character.name}.")

        total_kda = 0
        team_avg_kda = 0
        for user in teammates:
            user_kda = (user.kills + (user.assists / 2)) / max(1, user.deaths)
            total_kda += user_kda
            team_avg_kda = total_kda / len(teammates)

        if debug:
            print(f"Total KDA / All teammate KDA added upp: {total_kda:.2f}")
            print(f"Team Average KDA: {team_avg_kda:.2f}")
            print(f"{self.character.name}'s KDA: {selfkda:.2f}")
            print(f"Before Type Weights: {self.character.typeWeights}")

        ctype = self.character.characterType


        if selfkda > team_avg_kda:
            if debug:
                print("got past the selfkda > team_avg_kda check")
            if ctype == CharacterType.SUPPORT:
                if debug:
                    print(f"{self.character.name} is a support, so they get more sustain items.")
                self.add_weight(ItemType.SUSTAIN, 0.4, debug=debug)
            elif ctype == CharacterType.TANK:
                if debug:
                    print(f"{self.character.name} is a tank, so they get more sustain and gun items.")
                self.add_weight(ItemType.SUSTAIN, 0.4, debug=debug)
                self.add_weight(ItemType.GUN, 0.4, debug=debug)
            elif ctype == CharacterType.DPS:
                if debug:
                    print(f"{self.character.name} is a DPS, so they get more gun and spirit items.")
                self.add_weight(ItemType.GUN, 0.4, debug=debug)

            print(
                f"{self.character.name} is fed with a KDA of {selfkda:.2f} compared to the team average of {team_avg_kda:.2f}.")
        elif selfkda < team_avg_kda:
            self.add_weight(ItemType.SUSTAIN, 0.4, debug=debug)
            print(
                f"{self.character.name} is not fed with a KDA of {selfkda:.2f} compared to the team average of {team_avg_kda:.2f}.")
        if debug:
            print(f"After Type Weights: {self.character.typeWeights}")

    def menu(self):
        self.character.print_stats()
        print(f"Current Souls: {self.character.currentSouls}")
        print("\n" + "-" * 50 + "\n")
        if self.time == 0.0:
            print("Welcome to the Item Recommendation System!")
        print("Please select an option:")
        print(f"1. Calculate optimal item for {self.character.name} and buy it")
        print("2. Check team stats")
        print("3. Next phase")
        print("4. Exit")

    def assign_stats_to_teams(self) -> None:
        self.character.currentSouls += choice([800, 1600])
        for user in User.Arch_Mother:
            user.kills += randint(0, 5)
            user.deaths += randint(0, 3)
            user.assists += randint(0, 3)
        for user in User.Hidden_King:
            user.kills += randint(0, 5)
            user.deaths += randint(0, 3)
            user.assists += randint(0, 3)
    def simulate_game(self):
        print("Simulating game for", self.character.name)
        while self.time <= 50.0:
            self.divider()
            self.menu()

            if self.time > 0.0:
                self.is_fed_calc(debug=False)

            choice_user = input("Enter your choice: (1 - 4) ")
            try:
                choice_enum = Choices(int(choice_user))
            except ValueError:
                print("Was not able to parse choice. Please enter a number between 1 and 4.")
                return

            if choice_enum == Choices.calculate_item_to_buy:
                optimal_item = calculate_item_to_buy(self.character, list(items.values()), debug=True)
                if optimal_item:
                    print(f"Optimal item to buy: {optimal_item.name}")
                    self.character.buyitem(optimal_item)
                else:
                    print("No optimal item found or not enough souls to buy any item.")
            elif choice_enum == Choices.check_teams:
                User.check_teams()
            elif choice_enum == Choices.next_phase:
                self.assign_stats_to_teams()
                print("Moving to next phase...")
                self.time += 10
                if self.time > 50.0:
                    print("Reached end of simulation time.")
                    break
            elif choice_enum == Choices.exit:
                print("Exiting the simulation. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")

    @classmethod
    def check_teams(cls) -> None:
        print("Arch Mother Supporters:")
        for user in cls.Arch_Mother:
            print(f"  {user.character.name} - Kills: {user.kills}, Assists: {user.assists}, Deaths: {user.deaths}")

        print("Hidden King Supporters:")
        for user in cls.Hidden_King:
            print(f"  {user.character.name} - Kills: {user.kills}, Assists: {user.assists}, Deaths: {user.deaths}")

    def divider(self):
        print("\n" + "-" * 200 + "\n")
        print(f"\n--- Minute {self.time} ---")

if __name__ == '__main__':



# TODO legg til slik at det bare kan være 1 av hver karakter, ikke duplikater
# TODO Få initialiseringen av objekter inn i en egen fil, og importer det inn i App.py, for å gjøre det mer oversiktlig
#region character setup
    infernus = Character(
        name='Infernus',
        characterType = CharacterType.DPS,
        currentSouls = 2400,
        stats = {
            StatKey.HEALTH: 800,
            StatKey.SPIRITPOWER: 0,
            StatKey.STAMINA: 3,
            StatKey.BULLETDAMAGE: 5.5,
            StatKey.AMMO: 27,
            StatKey.BPS: 9.52,
            StatKey.HEALTH_REGEN: 2.0,
            StatKey.MOVE_SPEED: 6.7,
            StatKey.SPIRIT_LIFESTEAL: 0.0,
        },
        statWeights= {
            StatKey.BULLETDAMAGE: 1.2,
            StatKey.HEALTH: 0.8,
            StatKey.SPIRITPOWER: 1.5,
            StatKey.STAMINA: 1.1,
            StatKey.AMMO: 2.0,
        },
        typeWeights={
            ItemType.SUSTAIN: 1.15,
            ItemType.GUN: 1.2,
            ItemType.SPIRIT: 1.25
        }
    )

    pocket = Character(
        name='Pocket',
        characterType=CharacterType.DPS,
        currentSouls=2400,
        stats={
            StatKey.HEALTH: 750,
            StatKey.SPIRITPOWER: 0,
            StatKey.STAMINA: 3,
            StatKey.BULLETDAMAGE: 4.28,
            StatKey.AMMO: 11,
            StatKey.BPS: 1.9,
            StatKey.HEALTH_REGEN: 1.0,
            StatKey.MOVE_SPEED: 7.2,
            StatKey.SPIRIT_LIFESTEAL: 0.0,
        },
        statWeights={
            StatKey.BULLETDAMAGE: 0.3,
            StatKey.HEALTH: 0.8,
            StatKey.SPIRITPOWER: 2.0,
            StatKey.STAMINA: 1.5,
            StatKey.AMMO: 0.2,
        },
        typeWeights={
            ItemType.SUSTAIN: 1.05,
            ItemType.GUN: 1.10,
            ItemType.SPIRIT: 1.45
        }
    )

    dynamo = Character(
        name='Dynamo',
        characterType=CharacterType.SUPPORT,
        currentSouls=2400,
        stats={
            StatKey.HEALTH: 850,
            StatKey.SPIRITPOWER: 0,
            StatKey.STAMINA: 3,
            StatKey.BULLETDAMAGE: 12.6,
            StatKey.AMMO: 18,
            StatKey.BPS: 3.81,
            StatKey.HEALTH_REGEN: 1.8,
            StatKey.MOVE_SPEED: 6.7,
            StatKey.SPIRIT_LIFESTEAL: 0.0,
        },
        statWeights={
            StatKey.BULLETDAMAGE: 0.3,
            StatKey.HEALTH: 0.8,
            StatKey.SPIRITPOWER: 2.0,
            StatKey.STAMINA: 1.5,
            StatKey.AMMO: 0.2,
        },
        typeWeights={
            ItemType.SUSTAIN: 1.35,
            ItemType.GUN: 1.05,
            ItemType.SPIRIT: 1.25
        }
    )

    mokrill = Character(
        name='Mo & Krill',
        characterType=CharacterType.TANK,
        currentSouls=2400,
        stats={
            StatKey.HEALTH:940,
            StatKey.SPIRITPOWER:0,
            StatKey.STAMINA:3,
            StatKey.BULLETDAMAGE:2.82,
            StatKey.AMMO:20,
            StatKey.BPS:5.29,
            StatKey.HEALTH_REGEN:1.0,
            StatKey.MOVE_SPEED:8.0,
            StatKey.SPIRIT_LIFESTEAL:0.0,
        },
        statWeights={
            StatKey.BULLETDAMAGE:0.3,
            StatKey.HEALTH:2.0,
            StatKey.SPIRITPOWER:1.2,
            StatKey.STAMINA:1.1,
            StatKey.AMMO:0.2,
        },
        typeWeights={
            ItemType.SUSTAIN:1.65,
            ItemType.GUN:1.05,
            ItemType.SPIRIT:1.25 }
    )

    mirage = Character(
        name='Mirage',
        characterType=CharacterType.DPS,
        currentSouls=2400,
        stats={
            StatKey.HEALTH: 740,
            StatKey.SPIRITPOWER: 0,
            StatKey.STAMINA: 3,
            StatKey.BULLETDAMAGE: 14.8,
            StatKey.AMMO: 16,
            StatKey.BPS: 2.72,
            StatKey.HEALTH_REGEN: 2.0,
            StatKey.MOVE_SPEED: 7.0,
            StatKey.SPIRIT_LIFESTEAL: 0.0,
        },
        statWeights={
            StatKey.BULLETDAMAGE:2.3,
            StatKey.HEALTH:1.0,
            StatKey.SPIRITPOWER:2.2,
            StatKey.STAMINA:1.3,
            StatKey.AMMO:0.2,
        },
        typeWeights={
            ItemType.SUSTAIN:1.05,
            ItemType.GUN:1.55,
            ItemType.SPIRIT:1.35 }
    )

    shiv = Character(
        name='Shiv',
        characterType=CharacterType.DPS,
        currentSouls=2400,
        stats={
            StatKey.HEALTH: 840,
            StatKey.SPIRITPOWER: 0,
            StatKey.STAMINA: 3,
            StatKey.BULLETDAMAGE: 4.8,
            StatKey.AMMO: 10,
            StatKey.BPS: 1.81,
            StatKey.HEALTH_REGEN: 2.0,
            StatKey.MOVE_SPEED: 6.5,
            StatKey.SPIRIT_LIFESTEAL: 0.0,
        },
        statWeights={
            StatKey.BULLETDAMAGE:0.3,
            StatKey.HEALTH:1.2,
            StatKey.SPIRITPOWER:2.2,
            StatKey.STAMINA:1.3,
            StatKey.AMMO:0.2,
        },
        typeWeights={
            ItemType.SUSTAIN:1.25,
            ItemType.GUN:1.00,
            ItemType.SPIRIT:1.65 }
    )

    paige = Character(
        name='Paige',
        characterType=CharacterType.SUPPORT,
        currentSouls=2400,
        stats={
            StatKey.HEALTH: 690,
            StatKey.SPIRITPOWER: 0,
            StatKey.STAMINA: 2,
            StatKey.BULLETDAMAGE: 35.52,
            StatKey.AMMO: 14,
            StatKey.BPS: 1.67,
            StatKey.HEALTH_REGEN: 2.0,
            StatKey.MOVE_SPEED: 6.9,
            StatKey.SPIRIT_LIFESTEAL: 0.0,
        },
        statWeights={
            StatKey.BULLETDAMAGE:0.3,
            StatKey.HEALTH:2.2,
            StatKey.SPIRITPOWER:1.2,
            StatKey.STAMINA:1.5,
            StatKey.AMMO:0.2,
        },
        typeWeights={
            ItemType.SUSTAIN:1.65,
            ItemType.GUN:1.00,
            ItemType.SPIRIT:1.15 }
    )

    abrams = Character(
        name='Abrams',
        characterType=CharacterType.DPS,
        currentSouls=2400,
        stats={
            StatKey.HEALTH: 810,
            StatKey.SPIRITPOWER: 0,
            StatKey.STAMINA: 3,
            StatKey.BULLETDAMAGE: 3.6,
            StatKey.AMMO: 9,
            StatKey.BPS: 1.59,
            StatKey.HEALTH_REGEN: 1.5,
            StatKey.MOVE_SPEED: 6.4,
            StatKey.SPIRIT_LIFESTEAL: 0.0,
        },
        statWeights={
            StatKey.BULLETDAMAGE:1.3,
            StatKey.HEALTH:2.2,
            StatKey.SPIRITPOWER:1.2,
            StatKey.STAMINA:1.5,
            StatKey.AMMO:1.2,
        },
        typeWeights={
            ItemType.SUSTAIN:1.65,
            ItemType.GUN:1.10,
            ItemType.SPIRIT:1.00 }
    )

#endregion
#region user setup


    sivert = User(
        character=pocket,
        kills=0,
        deaths=0,
        assists=0
    )

    tobias = User(
        character=infernus,
        kills=0,
        deaths=0,
        assists=0
    )

    iver = User(
        character=dynamo,
        kills=0,
        deaths=0,
        assists=0
    )

    aragorn = User(
        character=mokrill,
        kills=0,
        deaths=0,
        assists=0
    )

    gimli = User(
        character=shiv,
        kills=0,
        deaths=0,
        assists=0
    )

    gandalf = User(
        character=abrams,
        kills=0,
        deaths=0,
        assists=0
    )

    legolas = User(
        character=paige,
        kills=0,
        deaths=0,
        assists=0
    )

    frodo = User(
        character=mirage,
        kills=0,
        deaths=0,
        assists=0
    )

#endregion
#region item setup
    items = {
        'Titanic_mag': Item(
            name='Titanic Mag',
            price=1600,
            item_category=ItemCategory.GUN,
            item_type=ItemType.GUN,
            stats={
                StatKey.BULLETDAMAGE: (ItemMode.MULTIPLY, 1.12),
                StatKey.AMMO: (ItemMode.MULTIPLY, 1.9),
            }
        ),
        'Extra_health': Item(
            name='Extra Health',
            price=800,
            item_category=ItemCategory.HEALTH,
            item_type=ItemType.SUSTAIN,
            stats={
                StatKey.HEALTH: (ItemMode.ADD, 185.0),
            }
        ),
        'Extra_spirit': Item(
            name='Extra Spirit',
            price=800,
            item_category=ItemCategory.SPIRIT,
            item_type=ItemType.SPIRIT,
            stats={
                StatKey.SPIRITPOWER: (ItemMode.ADD, 10.0),
            }
        ),
        'Improved_spirit': Item(
            name='Improved Spirit',
            price=1600,
            item_category=ItemCategory.SPIRIT,
            item_type=ItemType.SPIRIT,
            stats={
                StatKey.SPIRITPOWER: (ItemMode.ADD, 18.0),
            }
        ),
        'Enduring_speed': Item(
            name='Enduring Speed',
            item_type=ItemType.MOVEMENT,
            price=1600,
            item_category=ItemCategory.HEALTH,

            stats={
                StatKey.MOVE_SPEED: (ItemMode.ADD, 2.0),
                StatKey.HEALTH_REGEN: (ItemMode.ADD, 2.0),
            }
        ),
        'Spirit_lifesteal': Item(
            name='Spirit Lifesteal',
            item_type=ItemType.SUSTAIN,
            price=1600,
            item_category=ItemCategory.HEALTH,
            stats={
                StatKey.SPIRITPOWER: (ItemMode.ADD, 6.0),
                StatKey.SPIRIT_LIFESTEAL: (ItemMode.ADD, 16.0 ),
                StatKey.HEALTH: (ItemMode.ADD, 70.0),
            }
        )
    }
#endregion
    """""
    infernus.print_stats()
    print("")

    print("Optimal first item:", calculate_item_to_buy(infernus, list(items.values()), debug=True).name)
    infernus.buyitem(calculate_item_to_buy(infernus, list(items.values())))
    for item in infernus.currentItems:
        print(item.name)

    print("Optimal second item:", calculate_item_to_buy(infernus, list(items.values()), debug=True).name)
    """

    #Check User Class Functionality
    sivert.add_to_team(Teams.ARCH_MOTHER), iver.add_to_team(Teams.ARCH_MOTHER), legolas.add_to_team(Teams.ARCH_MOTHER), aragorn.add_to_team(Teams.ARCH_MOTHER), tobias.add_to_team(Teams.HIDDEN_KING), gimli.add_to_team(Teams.HIDDEN_KING), gandalf.add_to_team(Teams.HIDDEN_KING), frodo.add_to_team(Teams.HIDDEN_KING),
    #User.check_team_characters(Teams.ARCH_MOTHER),  User.check_team_characters(Teams.HIDDEN_KING)

    #print(sivert.character.characterType)
    #print(sivert.character.typeWeights[ItemType.SUSTAIN])

    sivert.is_fed_calc()
    sivert.simulate_game()

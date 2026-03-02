from enum import Enum
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

Effect = Union[float, Tuple[ItemMode, float], Dict[str, Union[str, float]]]
class Item:
    def __init__(self, name, price, item_category, stats: Dict[int, Effect], item_type: ItemType):
        self.itemCategory = item_category
        self.name = name
        self.price = price
        self.stats: Dict[int, Effect] = stats
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

if __name__ == '__main__':
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

    items = {
        'Titanic_mag': Item(
            name='Titanic Mag',
            price=1600,
            item_category=ItemCategory.GUN,
            item_type=ItemType.GUN,
            stats={
                StatKey.BULLETDAMAGE.value: (ItemMode.MULTIPLY, 1.12),
                StatKey.AMMO.value: (ItemMode.MULTIPLY, 1.9),
            }
        ),
        'Extra_health': Item(
            name='Extra Health',
            price=800,
            item_category=ItemCategory.HEALTH,
            item_type=ItemType.SUSTAIN,
            stats={
                StatKey.HEALTH.value: (ItemMode.ADD, 185.0),
            }
        ),
        'Extra_spirit': Item(
            name='Extra Spirit',
            price=800,
            item_category=ItemCategory.SPIRIT,
            item_type=ItemType.SPIRIT,
            stats={
                StatKey.SPIRITPOWER.value: (ItemMode.ADD, 10.0),
            }
        ),
        'Improved_spirit': Item(
            name='Improved Spirit',
            price=1600,
            item_category=ItemCategory.SPIRIT,
            item_type=ItemType.SPIRIT,
            stats={
                StatKey.SPIRITPOWER.value: (ItemMode.ADD, 18.0),
            }
        ),
        'Enduring_speed': Item(
            name='Enduring Speed',
            item_type=ItemType.MOVEMENT,
            price=1600,
            item_category=ItemCategory.HEALTH,

            stats={
                StatKey.MOVE_SPEED.value: (ItemMode.ADD, 2.0),
                StatKey.HEALTH_REGEN.value: (ItemMode.ADD, 2.0),
            }
        ),
        'Spirit_lifesteal': Item(
            name='Spirit Lifesteal',
            item_type=ItemType.SUSTAIN,
            price=1600,
            item_category=ItemCategory.HEALTH,
            stats={
                StatKey.SPIRITPOWER.value: (ItemMode.ADD, 6.0),
                StatKey.SPIRIT_LIFESTEAL.value: (ItemMode.ADD, 16.0 ),
                StatKey.HEALTH.value: (ItemMode.ADD, 70.0),
            }
        )
    }

    infernus.print_stats()
    print("")

    print("Optimal first item:", calculate_item_to_buy(infernus, list(items.values()), debug=True).name)
    infernus.buyitem(calculate_item_to_buy(infernus, list(items.values())))
    for it in infernus.currentItems:
        print(it.name)

    print("Optimal second item:", calculate_item_to_buy(infernus, list(items.values()), debug=True).name)
from enum import Enum
from typing import Union, Tuple, Dict

class CharacterType(Enum):
    TANK = 1
    SUPPORT = 2
    DPS = 3

class ItemType(Enum):
    SPIRIT = 1
    HEALTH = 2
    GUN = 3

class StatKey(Enum):
    HEALTH = 0
    SPIRITPOWER = 1
    STAMINA = 2
    BULLETDAMAGE = 3
    AMMO = 4

class ItemMode(Enum):
    ADD = 1
    MULTIPLY = 2

Effect = Union[float, Tuple[ItemMode, float], Dict[str, Union[str, float]]]
class Item:
    def __init__(self, name, price, itemType, stats: Dict[int, Effect]):
        self.itemType = itemType
        self.name = name
        self.price = price
        self.stats: Dict[int, Effect] = stats


class Character:
    def __init__(
            self, name, health, spiritPower, stamina, bulletDamage, ammo, characterType, currentSouls=0, currentItems=None):
        if currentItems is None:
            currentItems = []
        self.currentItems = currentItems
        self.currentSouls = currentSouls
        self.name = name
        self.characterType = characterType
        self.stats = {
            StatKey.HEALTH : health,
            StatKey.SPIRITPOWER : spiritPower,
            StatKey.STAMINA : stamina,
            StatKey.BULLETDAMAGE : bulletDamage,
            StatKey.AMMO: ammo,
        }


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
        for key, value in self.stats.items():
            print(key.name,": ", value)

items = {
    'Titanic_mag': Item(
        name = 'Titanic Mag',
        price = 1600,
        itemType = ItemType.GUN,
        stats = {
            StatKey.BULLETDAMAGE.value: (ItemMode.MULTIPLY, 1.2),
            StatKey.AMMO.value: (ItemMode.MULTIPLY, 1.9),
        }
    ),
    'Extra_health': Item(
        name = 'Extra Health',
        price = 800,
        itemType = ItemType.HEALTH,
        stats = {
            StatKey.HEALTH.value: (ItemMode.ADD, 185.0),
        }
    ),
    'Extra_spirit': Item(
        name = 'Extra Spirit',
        price = 800,
        itemType = ItemType.SPIRIT,
        stats = {
            StatKey.SPIRITPOWER.value: (ItemMode.ADD, 10.0),
        }
    ),
}


if __name__ == '__main__':
    infernus = Character(
        name='Infernus',
        health = 800,
        spiritPower = 0,
        stamina =3,
        bulletDamage = 5.5,
        ammo = 27,
        characterType = CharacterType.DPS,
        currentSouls = 3200,
    )

    infernus.print_stats()

    infernus.buyitem(items['Extra_health'])
    infernus.buyitem(items['Titanic_mag'])
    infernus.buyitem(items['Extra_spirit'])
    for item in infernus.currentItems:
        print(item.name)

    infernus.print_stats()
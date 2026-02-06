"""
things to deal with users and their cards
"""
import db_lib

import gachalib.cards
import gachalib,gachalib.types

def sort_cards_by_id(a:list[gachalib.types.CardsInventory | gachalib.types.Card]) -> list[gachalib.types.CardsInventory | gachalib.types.Card]:
    return sorted(a, key=lambda b: b.card_id)

def sort_cards_by_rarity(a:list[gachalib.types.CardsInventory | gachalib.types.Card]) -> list[gachalib.types.CardsInventory | gachalib.types.Card]:
    if type(a) == gachalib.types.Card:
        return sorted(a, key=lambda b: gachalib.rarity_order[a.rarity])
    else:
        #didn't test this
        return sorted(a, key=lambda b: gachalib.rarity_order[gachalib.cards.get_card_by_id(card_id=b.card_id)[1].rarity])

def get_users_cards(user_id:int) -> tuple[bool, list[gachalib.types.CardsInventory]]:
    try:
        a = db_lib.read_data(f"SELECT id,card_id,evil FROM gacha_cards WHERE (user_id) = (?)", (user_id,))
        b = []

        for c in a:
            b.append( gachalib.types.CardsInventory(inv_id=c[0],card_id=c[1],user_id=user_id,evil=c[2]) )

        return (True,b)
    except IndexError:
        return (False,) # pyright: ignore[reportReturnType]
    
def get_users_cards_by_id_range(user_id:int, id_start:int,id_end:int) -> tuple:
    try:
        success, cards = get_users_cards(user_id)
        if success:
            return(True, cards[id_start-1:id_end])
        else:
            return (False,)
    except IndexError:
        return (False,)

def get_users_cards_by_card_id(user_id:int, card_id:int, evil:bool=False) -> tuple[bool, list[gachalib.types.CardsInventory]]:
    try:
        a = db_lib.read_data(f"SELECT id,card_id,evil FROM gacha_cards WHERE (user_id, card_id, evil) = (?,?,?)", (user_id, card_id, evil))
        b = []

        for c in a:
            b.append( gachalib.types.CardsInventory(inv_id=c[0],card_id=c[1],user_id=user_id,evil=c[2]) )
        
        return (True, b)
    except IndexError:
        return (False,) # pyright: ignore[reportReturnType]
    
def give_user_card(user_id:int,card_id:int,evil:bool) -> gachalib.types.CardsInventory:
    a = db_lib.read_data(f"SELECT id FROM gacha_cards;", ())
    if len(a) == 0:
        inv_id = 1
    else:
        inv_id = a[len(a)-1][0] + 1

    db_lib.write_data("INSERT INTO gacha_cards (id,card_id,user_id,evil) VALUES (?,?,?,?)", (inv_id,card_id,user_id,evil))
    return gachalib.types.CardsInventory(inv_id=inv_id,card_id=card_id,user_id=user_id)

def change_card_owner(user_id:int,inv_id:int) -> bool: # ?
    try:
        db_lib.write_data("UPDATE gacha_cards SET user_id = ? WHERE id = ?", (user_id, inv_id))
        return True
    except IndexError:
        return False
    

def ownsCard(id:int,uid:int,get_evil:bool=False) -> bool | tuple(bool, bool):
    a = db_lib.read_data(f"SELECT id, evil FROM gacha_cards WHERE (user_id,card_id,evil) = (?,?,?);", (uid,id,get_evil))
    found = not len(a) == 0
    if get_evil:
        if not found:
            return (False, False)
        if any(b[1] for b in a):
            return (True, True)
        return (True, False)
    return found
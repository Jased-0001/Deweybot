"""
things to deal with users and their cards
"""
import db_lib

import gachalib,gachalib.types


def get_users_cards(user_id:int) -> tuple:
    try:
        a = db_lib.read_data(f"SELECT id,card_id FROM gacha_cards WHERE (user_id) = (?)", (user_id,))
        b = []

        for c in a:
            b.append( gachalib.types.Cards_User(inv_id=a[0],card_id=a[1],user_id=user_id) )

        return (True,b)
    except IndexError:
        return (False,)
    
def give_user_card(user_id:int,card_id:int) -> gachalib.types.Cards_User:
    a = db_lib.read_data(f"SELECT id FROM gacha_cards;", ())
    if len(a) == 0:
        inv_id = 1
    else:
        inv_id = a[len(a)-1][0] + 1

    db_lib.write_data("INSERT INTO gacha_cards (id,card_id,user_id) VALUES (?,?,?)", (inv_id,card_id,user_id))
    return gachalib.types.Cards_User(inv_id=inv_id,card_id=card_id,user_id=user_id)
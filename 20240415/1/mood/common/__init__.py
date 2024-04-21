"""Module for managing common data for client and server module."""
import cowsay
import io

weapons = {'sword': 10,
           'spear': 15,
           'axe': 20}

TIME_INTERVAL_FOR_MOVING_MONSTER = 5
FIELD_SIZE = 10
READ_FROM_FILE_TIMEOUT = 3


jgsbat = cowsay.read_dot_cow(io.StringIO('''
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\\'--'//__
         (((""`  `"")))EOC
'''))

cows_dict = {'jgsbat': jgsbat}


def get_all_monster_names():
    """:return: list with names of all monsters."""
    return list(cowsay.list_cows()) + list(cows_dict)


def get_custom_monster_names():
    """:return: list with names of custom monsters."""
    return list(cows_dict)


def get_cowsay_msg(monster_name, msg):
    """
    Get message said by specific monster.

    :param monster_name: name of monster
    :type monster_name: str
    :param msg: message for cowsay
    :type msg: str
    :return: message said by specific monster
    """
    if monster_name in get_custom_monster_names():
        return cowsay.cowsay(msg, cowfile=cows_dict[monster_name])
    else:
        return cowsay.cowsay(msg, cow=monster_name)


def get_weapons():
    """:return: names of all available weapons."""
    return list(weapons)

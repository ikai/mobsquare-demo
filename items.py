# This file specifies the various items that can be used in MobSquare.
# It was much easier to do it this way than to persist them for dev purposes.
# In a real application, it might make sense t

STARTING_MONEY = 500
weapons = {}
armor_list = {}
mobsters = {}

weapons["bat"] = {
    "name" : "Baseball Bat",
    "image_url" : "",
    "level_req" : 1,
    "damage_bonus" : 1,
    "to_hit_bonus" : 0.1,
    "cost"  : 20
}

armor_list["leather_jacker"] = {
    "name" : "Leather Jacket",
    "image_url" : "",
    "level_req" : 1,
    "armor_bonus" : 1,
    "cost" : 80
}

mobsters["initiate"] = {
    "name" : "Initiate",
    "image_url" : "",
    "level" : 1,
    "cost" : 200,
    "base_damage" : 5,
    "base_hitpoints" : 20
}
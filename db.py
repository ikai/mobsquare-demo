import pymongo
import bson

# Instantiate a global connection to MongoDB
connection = pymongo.Connection()
database = connection.mobsq_db

def get_user(user_id):
    """ Helper method for fetching the user from a user_id """
    return database.profiles.find_one({"_id" : bson.objectid.ObjectId(user_id)})

def get_or_create_location_by_id(location_id):
    """
        Attempts to fetch location data from database. If it doesn't exist,
        create it.
    """    
    location_data = database.location.find_one({ "_id" : location_id})
    if location_data is None:
        location_data = {   "_id" : location_id, 
                            "guards": [], 
                            "owner" : None, 
                            "history" : [], 
                            "last_extort_time" : None 
                        }
        database.location.save(location_data, safe=True)
    return location_data
    
def get_locations(location_ids):
    """ 
        Given a list of location IDs, return a dictionary of id, location pairs
    """
    locations = {}
    for location in database.location.find({"_id" : { "$in" : location_ids }}):
        locations[location["_id"]] = location
    return locations
    
def save_profile(profile):
    """ Saves a dictionary to the profile collection """
    return database.profiles.save(profile, safe=True)
    
def save_location(location):
    """ Saves a dictionary to the location collection """
    return database.location.save(location, safe=True)

def save_inventory(inventory):
    """ Saves a dictionary to the inventory collection """
    return database.inventory.save(inventory, safe=True)

    
def get_inventory_for_user(user):
    """ 
        Fetches the inventory for user. Keys off the user's Facebook ID.
        
        Key the inventory for a given User off their Facebook ID, not their
        MongoDB ID because of the unfortunate choice we made of tying a session
        to a User object. 
    """
    inventory = database.inventory.find_one({ "_id" : user["id"] })
    if inventory is None:
        inventory = {   "_id" : user["id"], 
                        "weapons" : {}, 
                        "armor" : {}, 
                        "mobsters" : [], 
                        "money" : items.STARTING_MONEY 
                    }
    return inventory

    


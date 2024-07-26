from src.session.room import search_empty_rooms


def delete_empty_rooms():
    "Delete rooms with no linked users"
    for room in search_empty_rooms():
        room.delete()

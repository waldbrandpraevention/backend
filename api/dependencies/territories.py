


from database import territories_table


async def get_territories(orga_id):
    return territories_table.get_territories(orga_id)

async def get_territory_by_id(territory_id, orga_id):
    return territories_table.get_territory(territory_id, orga_id)

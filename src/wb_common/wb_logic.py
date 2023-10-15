SLICE_COUNT = 8

class wb_logic:
    async def search_adverts_by_keyword(res):
        wb_search_positions = None
        
        if res and res.get('pages') and res.get('pages')[0] and res.get('pages')[0].get('positions') and len(res.get('pages')[0].get('positions')) > 0:
            wb_search_positions = res.get('pages')[0].get('positions')[0:SLICE_COUNT]
        
        res = res['adverts'][0:SLICE_COUNT] if res.get('adverts') is not None else []
        result = []
        position = 0
        for advert in res:
            result.append({
                "price": advert['cpm'],
                "p_id": advert['id'],
                "position": position,
                "wb_search_position": wb_search_positions[position]
            })
        position +=1
        return result
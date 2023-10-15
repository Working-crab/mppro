import pytest
import aiohttp

from wb_common.wb_logic import wb_logic


@pytest.mark.asyncio
async def test_search_adverts_by_keyword_logic():
    SAMPLE_RESPONSE = {
        "pages": [
            {
                "positions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "page": 1,
                "count": 8
            }
        ],
        "adverts": [
            {
                "code":"",
                "advertId":123,
                "id":1,
                "cpm":1000,
                "subject":50
            },
            {
                "code":"",
                "advertId":345,
                "id":2,
                "cpm":100,
                "subject":10
            },
        ],
        "minCPM":150
    }


    result = await wb_logic.search_adverts_by_keyword(SAMPLE_RESPONSE)

    assert result is not None
    
    assert len(result) == 2
    assert result[0]["price"] == 1000
    assert result[0]["p_id"] == 1
    assert result[0]["position"] == 0
    assert result[0]["wb_search_position"] == 1


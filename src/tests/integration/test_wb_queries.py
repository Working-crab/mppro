import pytest

from wb_common.wb_queries import wb_queries


@pytest.mark.asyncio
async def test_search_integration_with_wb():
    keyword_to_test = "Платье"
    slice_count = 8
    response = await wb_queries.search_adverts_by_keyword(keyword_to_test)

    assert response is not None
    
    assert 'pages' in response
    assert len(response['pages']) > 0
    assert 'positions' in response['pages'][0]
    assert len(response['pages'][0]['positions']) > 0
    
    assert len(response['pages'][0]['positions']) <= slice_count
    
    if 'adverts' in response:
        adverts = response['adverts'][0:slice_count]
        for advert in adverts:
            assert 'cpm' in advert
            assert 'id' in advert
import pytest
import aiohttp

from wb_common.wb_queries import wb_queries


@pytest.mark.asyncio
async def test_search_integration_with_wb_separate():
    keyword_to_test = "Платье"
    slice_count = 8
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://catalog-ads.wildberries.ru/api/v5/search?keyword={keyword_to_test}') as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'pages' in data
            assert len(data['pages']) > 0
            assert 'positions' in data['pages'][0]
            assert len(data['pages'][0]['positions']) > 0
            
            assert len(data['pages'][0]['positions']) <= slice_count
            
            if 'adverts' in data:
                adverts = data['adverts'][0:slice_count]
                for advert in adverts:
                    assert 'cpm' in advert
                    assert 'id' in advert


@pytest.mark.asyncio
async def test_search_adverts_by_keyword_integration():
    keyword_to_test = "Платье"
    result = await wb_queries.search_adverts_by_keyword(keyword_to_test)
    
    # Проверяем, что результат не пустой
    assert result is not None
    assert isinstance(result, list)
    
    # Теперь проверяем структуру каждого элемента в ответе:
    for item in result:
        assert "price" in item
        assert "p_id" in item
        assert "position" in item
        assert "wb_search_position" in item

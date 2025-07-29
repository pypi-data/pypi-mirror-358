import pytest
from sharp_cocoro.cocoro import Cocoro


@pytest.mark.asyncio
@pytest.mark.vcr
async def test_login():
    """Test basic login functionality."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        # Test login
        result = await cocoro.login()
        assert isinstance(result, dict)
        assert result.get("errorCode") is None
        assert cocoro.is_authenticated is True


@pytest.mark.asyncio 
@pytest.mark.vcr
async def test_query_boxes():
    """Test querying device boxes."""
    cocoro = Cocoro(
        app_secret="pngtfljRoYsJE9NW7opn1t2cXA5MtZDKbwon368hs80",
        app_key="jXLhL_R8DKVlRX_HqsOXsOizfPPioGQUed2rKdNqFn8",
        service_name="iClub"
    )
    
    async with cocoro:
        await cocoro.login()
        
        # Test query boxes
        boxes = await cocoro.query_boxes()
        assert isinstance(boxes, list)
        
        # Print box info for debugging
        print(f"\nFound {len(boxes)} boxes:")
        for box in boxes:
            print(f"  - Box ID: {box.boxId}")
            print(f"    Devices: {len(box.echonetData)}")
            for device in box.echonetData:
                print(f"      - {device.labelData.name} ({device.labelData.deviceType})")
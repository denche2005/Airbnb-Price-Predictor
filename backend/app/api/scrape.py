from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.scraper.airbnb_scraper import scrape_listing
from app.ml.prediction_pipeline import predict

router = APIRouter()


class ScrapeRequest(BaseModel):
    url: str = Field(example="https://www.airbnb.com/rooms/12345")


@router.post("/scrape")
async def scrape_and_predict(req: ScrapeRequest):
    try:
        extracted = await scrape_listing(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        err_msg = str(e) or repr(e)
        tb = traceback.format_exc()
        print(f"[Scrape Error] {err_msg}\n{tb}", flush=True)
        raise HTTPException(
            status_code=422,
            detail=f"Scraping failed: {err_msg}. Try the manual form instead.",
        )

    scraped_flag = extracted.pop("_scraped", None)
    listing_id = extracted.pop("_listing_id", None)

    try:
        result = predict(extracted)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run the training pipeline first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result["extracted_data"] = extracted
    result["listing_id"] = listing_id
    return result

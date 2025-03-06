from fastapi import FastAPI
from search.main import app as searchApp

router = FastAPI()

router.include_router(searchApp)


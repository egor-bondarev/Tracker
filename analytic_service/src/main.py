
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_graphene3 import GraphQLApp
from src.schemas import schema

app = FastAPI()

app.add_route("/graphql", GraphQLApp(schema=schema.schema))

origins = [
    "http://localhost:3000",  # Frontend URL
    # Add other origins you want to allow
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

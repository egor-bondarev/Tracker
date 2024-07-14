
from fastapi import FastAPI
from starlette_graphene3 import GraphQLApp
from src.schemas import schema

app = FastAPI()

app.add_route("/graphql", GraphQLApp(schema=schema.schema))

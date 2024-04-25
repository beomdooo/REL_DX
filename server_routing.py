from shiny import App

# New imports
from starlette.applications import Starlette
from starlette.routing import Mount

from starlette.staticfiles import StaticFiles

# Our pages
from app_ui import main_page, server
from app_intro import intro_page, intro_server

# Make App instance from your pages
page_main = App(ui=main_page, server=server)
page_intro = App(ui=intro_page, server=intro_server)

# Use Starlette to construct routes
routes = [
    Mount("/main", app=page_main),
    Mount("", app=page_intro),
]

# Declare an app with Startlette
app = Starlette(routes=routes)

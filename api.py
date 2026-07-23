from aiohttp import web
import database as db


async def get_medicines(request):
    medicines = db.list_medicines()
    data = [
        {"id": m["id"], "name": m["name"], "description": m["description"], "photo_url": m["photo_url"]}
        for m in medicines
    ]
    return web.json_response(data)


async def get_company_info(request):
    return web.json_response({"text": db.get_company_info()})


@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


def create_app():
    db.init_db()
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/api/medicines", get_medicines)
    app.router.add_get("/api/company-info", get_company_info)
    app.router.add_route("OPTIONS", "/{tail:.*}", lambda r: web.Response())
    return app

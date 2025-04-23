from app import app

# This is the handler for Vercel serverless functions
def handler(request, response):
    return app(request, response)

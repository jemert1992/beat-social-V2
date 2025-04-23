"""
Entry point for Vercel serverless deployment.
This file imports the Flask app from app.py and provides a handler function for Vercel.
"""

from flask import Flask
import app

# This is the handler for Vercel serverless functions
def handler(request, response):
    return app.app(request, response)

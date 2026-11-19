"""
Serverless WSGI Entrypoint for Vercel, Netlify, and Cloud Run.
Exposes the Flask WSGI callable 'app' for serverless function runtimes.
"""

from dcode.web.app import app

# Standard WSGI callable for Vercel (@vercel/python) and AWS Lambda
handler = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

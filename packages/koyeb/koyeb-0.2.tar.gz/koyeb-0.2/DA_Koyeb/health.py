from . import __version__

status_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DELPHADEX - Koyeb</title>
    <style>
        body {{
            background-color: #121212;
            color: #00f7ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .card {{
            background-color: #1e1e1e;
            padding: 2rem 3rem;
            border-radius: 16px;
            box-shadow: 0 0 20px rgba(0, 247, 255, 0.4);
            text-align: center;
        }}
        .title {{
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }}
        .version {{
            font-size: 1.2rem;
            color: #cccccc;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="title">DELPHADEX Positive Health Emitter</div>
        <div class="version">Version {__version__}</div>
    </div>
</body>
</html>
"""

def emit_positive_health(host="0.0.0.0", port=8000, route="/"):
    from flask import Flask
    import threading
    
    app = Flask(__name__)
    
    @app.route(route)
    def ahh():
        return status_html, 200
        
    def run():
        app.run(host=host, port=port)
    
    thread = threading.Thread(target=run, daemon=True)
    
    thread.start()

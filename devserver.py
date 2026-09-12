"""本地开发服务器：开启 Jinja 模板热重载，改模板无需重启。

用法：venv/Scripts/python.exe devserver.py
"""
import os
import sys

os.environ.setdefault("FLASK_ENV", "development")

from app import create_app  # noqa: E402

app = create_app()
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)

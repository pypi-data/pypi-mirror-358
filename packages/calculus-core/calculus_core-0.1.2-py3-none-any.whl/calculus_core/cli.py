# calculus_core/cli.py
import os
import sys

import streamlit.web.cli as stcli


def run_app():
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(project_root, 'app.py')
    sys.argv = ['streamlit', 'run', app_path]
    stcli.main()


if __name__ == '__main__':
    run_app()

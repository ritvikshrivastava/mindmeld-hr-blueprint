# -*- coding: utf-8 -*-
"""This module defines the command line interface for this app. Use
`python -m <app_name>` to see available commands.
"""

if __name__ == '__main__':
    from . import app
    app.question_answerer.load_kb('hr_assistant_categories', 'user_data','./hr_assistant_categories/data/user_data.json')
    app.cli()
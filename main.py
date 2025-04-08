#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations


from app.api.database.create_american_law_db import create_american_law_db
from app.logger import logger
from app.configs import configs


def main():
    # american_law_db_path = configs.AMERICAN_LAW_DATA_DIR / 'american_law.db'
    # if not american_law_db_path.exists():
    #     logger.info("Creating American Law database...")
    create_american_law_db()
    # else:
    #     logger.info("American Law database already exists.")

if __name__ == '__main__':
    main()

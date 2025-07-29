# -*- coding: utf-8 -*-
##############################################################################
# author       # TecDroiD
# date         # 2025-05-28
# ---------------------------------------------------------------------------
# description  #
#              #
#              #
##############################################################################
import logging

def with_logger(cls):
    """
    Dekorator, der einer Klasse automatisch ein Logger-Attribut hinzufügt.
    """
    cls.logger = logging.getLogger(cls.__name__)
    if not logging.getLogger().handlers:
        # Füge Standard-Handler nur einmal hinzu
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s - %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)
    return cls

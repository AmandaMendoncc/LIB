"""Módulo para configuração centralizada do logger do projeto."""

import logging
import sys

def setup_logging():
    """
    Configura o logging para imprimir mensagens de nível INFO e acima para o console.

    Este setup básico direciona o output para sys.stdout e formata as mensagens
    para incluir timestamp, nome do logger, nível da mensagem e a mensagem em si.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout,
    )
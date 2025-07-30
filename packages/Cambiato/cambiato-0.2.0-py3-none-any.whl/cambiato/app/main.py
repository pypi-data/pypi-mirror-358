r"""The entry point of the Cambiato web app."""

# Standard library
import logging
from pathlib import Path

# Third party
import streamlit as st

# Local
from cambiato.app._pages import Pages

APP_PATH = Path(__file__)

logger = logging.getLogger(__name__)


def main() -> None:
    r"""The page router of the Cambiato web app."""

    # try:
    #     cm = load_config()
    # except exceptions.ConfigError as e:
    #     error_msg = f'Error loading configuration!\n{str(e)}'
    #     logger.error(error_msg)
    #     st.error(error_msg, icon=stp.ICON_ERROR)

    pages = [st.Page(page=Pages.HOME, title='Home', default=True)]
    page = st.navigation(pages, position='sidebar')
    page.run()


if __name__ == '__main__':
    main()

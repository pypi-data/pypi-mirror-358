import requests
import analyst_klondike
from analyst_klondike.features.message_box.actions import DisplayMessageBoxAction
from analyst_klondike.state.app_dispatch import app_dispatch


def _get_latest_app_version() -> str:
    response = requests.get(
        'https://pypi.org/pypi/analyst-klondike/json', timeout=5000)
    response.raise_for_status()
    data = response.json()
    latest_version = data['info']['version']
    return latest_version


def _is_outdated() -> bool:
    current_version = analyst_klondike.__version__
    latest_version = _get_latest_app_version()
    return _more(latest_version, current_version)


def _more(first_v: str, next_v: str) -> bool:
    av_tuple = first_v.split(".")
    msp_tuple = next_v.split(".")
    return av_tuple > msp_tuple


def close_app() -> None:
    # pylint: disable=import-outside-toplevel
    from analyst_klondike.ui.runner_app import get_app
    app = get_app()
    app.exit(0)


def display_message_if_outdated():
    isout = _is_outdated()
    current_version = analyst_klondike.__version__
    if isout:
        app_dispatch(
            DisplayMessageBoxAction(
                message=f"Доступна новая версия (текущая версия {current_version}) Обновите приложение. \n" +
                "Для этого закройте приложение и запустите команду: \n" +
                "[@click=app.copy_update_str_to_clipboard]uv tool upgrade analyst-klondike[/]",
                ok_button_callback=close_app)
        )

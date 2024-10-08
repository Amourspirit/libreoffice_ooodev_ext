from __future__ import annotations
from typing import Any, TYPE_CHECKING, cast
import uno
import unohelper

from com.sun.star.awt import XContainerWindowEventHandler
from com.sun.star.beans import PropertyChangeEvent  # struct
from com.sun.star.beans import XPropertyChangeListener

from ...basic_config import BasicConfig
from ...lo_util.resource_resolver import ResourceResolver

from ...lo_util.configuration import Configuration, SettingsT
from ...settings.settings import Settings
from ...oxt_logger import OxtLogger

if TYPE_CHECKING:
    from com.sun.star.awt import UnoControlDialog  # service
    from com.sun.star.awt import UnoControlCheckBoxModel


IMPLEMENTATION_NAME = f"{BasicConfig().lo_implementation_name}.OptPage"


class CheckBoxListener(unohelper.Base, XPropertyChangeListener):
    def __init__(self, handler: "OptionsDialogHandler"):
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("CheckBoxListener.__init__")
        self.handler = handler
        self._logger.debug("CheckBoxListener.__init__ done")

    def disposing(self, Source: Any):
        pass

    def propertyChange(self, evt: PropertyChangeEvent):
        self._logger.debug("CheckBoxListener.propertyChange")
        try:
            # state (evn.NewValue) will be 1 for true and 0 for false
            src = cast("UnoControlCheckBoxModel", evt.Source)
            if src.Name == "chkOooDev":
                self.handler.load_ooo_dev = self.handler.state_to_bool(cast(int, (evt.NewValue)))
        except Exception as err:
            self._logger.error(f"CheckBoxListener.propertyChange: {err}", exc_info=True)
            raise


class OptionsDialogHandler(unohelper.Base, XContainerWindowEventHandler):
    def __init__(self, ctx: Any):
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("OptionPage-OptionsDialogHandler.__init__")
        self.ctx = ctx
        self._config = BasicConfig()
        self._resource_resolver = ResourceResolver(self.ctx)
        self._config_node = f"/{self._config.lo_implementation_name}.Settings/Options"
        self._window_name = "options"
        self._settings = Settings()
        self._load_ooo_dev = False
        self._logger.debug("OptionPage-OptionsDialogHandler.__init__ done")

    # region XContainerWindowEventHandler
    def callHandlerMethod(self, xWindow: UnoControlDialog, EventObject: Any, MethodName: str):  # type: ignore
        self._logger.debug(f"OptionPage-OptionsDialogHandler.callHandlerMethod: {MethodName}")
        if MethodName == "external_event":
            try:
                self._handle_external_event(xWindow, EventObject)
            except Exception as e:
                print(e)
            return True

    def getSupportedMethodNames(self):
        return ("external_event",)

    # endregion XContainerWindowEventHandler

    def _handle_external_event(self, window: UnoControlDialog, ev_name: str):
        self._logger.debug(f"OptionPage-OptionsDialogHandler._handle_external_event: {ev_name}")
        if ev_name == "ok":
            self._save_data(window)
        elif ev_name == "back":
            self._load_data(window, "back")
        elif ev_name == "initialize":
            self._load_data(window, "initialize")
        return True

    def _save_data(self, window: UnoControlDialog):
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug(f"OptionPage-OptionsDialogHandler._save_data name: {name}")
        if name != self._window_name:
            return
        settings: SettingsT = {
            "names": ("OptionLoadOooDev",),
            "values": (self.load_ooo_dev,),  # type: ignore
        }
        self._logger.debug(f"OptionPage-OptionsDialogHandler._save_data settings: {settings}")
        self._config_writer(settings)

    def _load_data(self, window: UnoControlDialog, ev_name: str):
        # sourcery skip: extract-method
        name = cast(str, window.getModel().Name)  # type: ignore
        self._logger.debug(f"OptionPage-OptionsDialogHandler._load_data name: {name}")
        self._logger.debug(f"OptionPage-OptionsDialogHandler._load_data ev_name: {ev_name}")
        if name != self._window_name:
            return
        try:
            settings = self._settings.current_settings
            if settings:
                self.load_ooo_dev = bool(settings["OptionLoadOooDev"])

            controls = {
                "chkOooDev": "OptionLoadOooDev",
            }

            if ev_name == "initialize":
                listener = CheckBoxListener(self)
                for control in window.Controls:  # type: ignore
                    model = control.Model
                    model.Label = self._resource_resolver.resolve_string(model.Label)
                    ctl_value = controls.get(model.Name)
                    if ctl_value and control.supportsService("com.sun.star.awt.UnoControlCheckBox"):
                        model.State = self.bool_to_state(settings.get(ctl_value, False))
                        model.addPropertyChangeListener("State", listener)

        except Exception as err:
            self._logger.error(f"OptionPage-OptionsDialogHandler._load_data: {err}", exc_info=True)
            raise err
        return

    def state_to_bool(self, state: int) -> bool:
        return bool(state)

    def bool_to_state(self, value: bool) -> int:
        return int(value)

    def _config_writer(self, settings: SettingsT):
        try:
            cfg = Configuration()
            cfg.save_configuration(self._config_node, settings)
        except Exception as e:
            raise e

    @property
    def resource_resolver(self) -> ResourceResolver:
        return self._resource_resolver

    @property
    def load_ooo_dev(self) -> bool:
        return self._load_ooo_dev

    @load_ooo_dev.setter
    def load_ooo_dev(self, value: bool):
        self._load_ooo_dev = value

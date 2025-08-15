# src/ui_service_model.py
from typing import Tuple, Dict
from AppKit import (
    NSAlert, NSView, NSPopUpButton, NSTextField, NSMakeRect
)
from Foundation import NSObject
import objc
from .services import list_services_models

OK_RETURN = 1000

def _label(frame, text):
    lbl = NSTextField.alloc().initWithFrame_(frame)
    lbl.setBezeled_(False); lbl.setDrawsBackground_(False)
    lbl.setEditable_(False); lbl.setSelectable_(False)
    lbl.setStringValue_(text); return lbl

class _Controller(NSObject):
    def initWithMaps_(self, model_map):
        self = objc.super(_Controller, self).init()
        if self is None: return None
        self.model_map = model_map
        self.servicePopup = None
        self.modelPopup = None
        return self

    def serviceChanged_(self, _sender):
        service = self.servicePopup.titleOfSelectedItem()
        self._reload_models(service)

    def _reload_models(self, service):
        self.modelPopup.removeAllItems()
        models = list(self.model_map.get(service, {}).keys()) or ["web"]
        self.modelPopup.addItemsWithTitles_(models)

def show_service_model_dialog(current_service: str, current_model: str) -> Tuple[bool, str, str]:
    """Returns (ok, service, model)"""
    model_map: Dict = list_services_models()  # {service: {model: meta}}
    services = list(model_map.keys())
    if not services:
        from .pricing import PRICING_PATH
        raise RuntimeError(f"No services found in pricing.json. Please edit {PRICING_PATH} via 'Manage Pricing…'")
        
    alert = NSAlert.alloc().init()
    alert.setMessageText_("Service & Model")
    alert.setInformativeText_("Choose a provider and model. Models update when you change service.")
    alert.addButtonWithTitle_("Save"); alert.addButtonWithTitle_("Cancel")

    w, h = 420, 110
    acc = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, w, h))
    acc.addSubview_(_label(NSMakeRect(0, h-24, 70, 18), "Service:"))
    acc.addSubview_(_label(NSMakeRect(0, h-54, 70, 18), "Model:"))

    servicePopup = NSPopUpButton.alloc().initWithFrame_pullsDown_(NSMakeRect(80, h-28, 320, 22), False)
    servicePopup.addItemsWithTitles_(services)
    if current_service in services:
        servicePopup.selectItemWithTitle_(current_service)

    modelPopup = NSPopUpButton.alloc().initWithFrame_pullsDown_(NSMakeRect(80, h-58, 320, 22), False)

    controller = _Controller.alloc().initWithMaps_(model_map)
    controller.servicePopup = servicePopup
    controller.modelPopup = modelPopup

    servicePopup.setTarget_(controller)
    servicePopup.setAction_("serviceChanged:")
    acc.addSubview_(servicePopup); acc.addSubview_(modelPopup)

    alert.setAccessoryView_(acc)
    # Initialize models for the preselected service
    controller._reload_models(servicePopup.titleOfSelectedItem())
    if current_model in list(model_map.get(current_service, {}).keys()):
        modelPopup.selectItemWithTitle_(current_model)

    res = alert.runModal()
    if res != OK_RETURN:
        return False, current_service, current_model

    return True, servicePopup.titleOfSelectedItem(), modelPopup.titleOfSelectedItem()
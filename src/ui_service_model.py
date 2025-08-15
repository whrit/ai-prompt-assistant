# src/ui_service_model.py
from typing import Tuple, Dict
from AppKit import (
    NSView, NSTextField, NSMakeRect, NSSearchField, NSStackView,
    NSPanel, NSWindowStyleMaskTitled, NSWindowStyleMaskClosable, NSWindowStyleMaskResizable,
    NSVisualEffectView, NSVisualEffectMaterialSidebar, NSVisualEffectBlendingModeBehindWindow,
    NSPopUpButton, NSButton, NSApp
)
from Foundation import NSObject
import objc
from .services import list_services_models
from .settings_manager import SettingsManager
from .storage import load_config, save_config
from .debugging import log_debug, log_exception

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
        self.filtered = model_map
        self.servicePopup = None
        self.modelPopup = None
        self.search = None
        self.metaLabel = None
        return self

    def serviceChanged_(self, _sender):
        service = self.servicePopup.titleOfSelectedItem()
        log_debug("Service changed", service=service)
        self._reload_models(service)

    def controlTextDidChange_(self, _):
        term = (self.search.stringValue() or "").lower()
        log_debug("Search changed", term=term)
        if not term:
            self.filtered = self.model_map
        else:
            new = {}
            for prov, models in self.model_map.items():
                if term in prov.lower():
                    new[prov] = models
                    continue
                filt = {m: meta for m, meta in models.items() if term in m.lower()}
                if filt:
                    new[prov] = filt
            self.filtered = new
        self._reload_models(self.servicePopup.titleOfSelectedItem())

    def _reload_models(self, service):
        self.modelPopup.removeAllItems()
        models = list(self.filtered.get(service, {}).keys()) or ["web"]
        log_debug("Reload models", service=service, models=models)
        self.modelPopup.addItemsWithTitles_(models)
        try:
            self._update_meta(service, self.modelPopup.titleOfSelectedItem())
        except Exception:
            log_exception("_reload_models._update_meta")

    def modelChanged_(self, _sender):
        try:
            self._update_meta(self.servicePopup.titleOfSelectedItem(), self.modelPopup.titleOfSelectedItem())
        except Exception:
            log_exception("modelChanged")

    def _update_meta(self, service, model):
        if not self.metaLabel:
            return
        meta = (self.filtered.get(service, {}) or {}).get(model, {})
        ctx = meta.get("ctx", "?")
        price_in = meta.get("in", "?")
        price_out = meta.get("out", "?")
        try:
            price_in = f"{float(price_in):.5f}"
        except Exception:
            price_in = str(price_in)
        try:
            price_out = f"{float(price_out):.5f}"
        except Exception:
            price_out = str(price_out)
        self.metaLabel.setStringValue_(f"Context: {ctx} • $in: {price_in}/1K • $out: {price_out}/1K")
        log_debug("Meta updated", service=service, model=model, ctx=ctx, price_in=price_in, price_out=price_out)


def show_service_model_dialog(current_service: str, current_model: str) -> Tuple[bool, str, str]:
    """Returns (ok, service, model)"""
    log_debug("Open Service & Model dialog", current_service=current_service, current_model=current_model)
    model_map: Dict = list_services_models()  # {service: {model: meta}}
    services = list(model_map.keys())
    if not services:
        from .pricing import PRICING_PATH
        log_debug("No services in pricing.json", path=str(PRICING_PATH))
        raise RuntimeError(f"No services found in pricing.json. Please edit {PRICING_PATH} via 'Manage Pricing…'")

    # Build panel
    cfg = load_config()
    last_size = (cfg.get("ui", {}).get("svc_model_size") or [520, 240])
    panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(((0,0),(last_size[0], last_size[1])), NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskResizable, 2, False)
    sm = SettingsManager()
    panel.setTitle_(sm.get_string("svc_model.title", "Service & Model"))
    vib = NSVisualEffectView.alloc().initWithFrame_(NSMakeRect(0,0,last_size[0], last_size[1]))
    vib.setMaterial_(NSVisualEffectMaterialSidebar)
    vib.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
    vib.setState_(1)

    stack = NSStackView.alloc().initWithFrame_(NSMakeRect(0,0,last_size[0], last_size[1]))
    stack.setOrientation_(1); stack.setAlignment_(1); stack.setSpacing_(8); stack.setEdgeInsets_((12,12,12,12))
    stack.setTranslatesAutoresizingMaskIntoConstraints_(False)
    vib.addSubview_(stack)

    controller = _Controller.alloc().initWithMaps_(model_map)

    # Search field
    controller.search = NSSearchField.alloc().initWithFrame_(NSMakeRect(0,0,10,24))
    controller.search.setPlaceholderString_(sm.get_string("svc_model.search_placeholder", "Search services/models"))
    controller.search.setDelegate_(controller)

    # Popups
    servicePopup = NSPopUpButton.alloc().initWithFrame_pullsDown_(NSMakeRect(0,0,10,24), False)
    servicePopup.addItemsWithTitles_(services)
    if current_service in services:
        servicePopup.selectItemWithTitle_(current_service)
    modelPopup = NSPopUpButton.alloc().initWithFrame_pullsDown_(NSMakeRect(0,0,10,24), False)

    controller.servicePopup = servicePopup
    controller.modelPopup = modelPopup
    controller.metaLabel = None  # set after creation
    servicePopup.setTarget_(controller); servicePopup.setAction_("serviceChanged:")
    modelPopup.setTarget_(controller); modelPopup.setAction_("modelChanged:")

    # Metadata label
    metaLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(0,0,10,18))
    metaLabel.setBezeled_(False); metaLabel.setDrawsBackground_(False)
    metaLabel.setEditable_(False); metaLabel.setSelectable_(False)
    controller.metaLabel = metaLabel

    # Buttons
    saveBtn = NSButton.alloc().initWithFrame_(NSMakeRect(0,0,80,30))
    saveBtn.setTitle_(sm.get_string("common.save", "Save"))
    cancelBtn = NSButton.alloc().initWithFrame_(NSMakeRect(0,0,80,30))
    cancelBtn.setTitle_(sm.get_string("common.cancel", "Cancel"))
    editPricingBtn = NSButton.alloc().initWithFrame_(NSMakeRect(0,0,140,30))
    editPricingBtn.setTitle_(sm.get_string("svc_model.edit_pricing", "Edit pricing.json…"))

    # Assemble
    stack.addView_inGravity_(controller.search, 1)
    stack.addView_inGravity_(servicePopup, 1)
    stack.addView_inGravity_(modelPopup, 1)
    stack.addView_inGravity_(metaLabel, 1)
    stack.addView_inGravity_(editPricingBtn, 1)
    stack.addView_inGravity_(saveBtn, 1)
    stack.addView_inGravity_(cancelBtn, 1)
    vib.addConstraint_(stack.topAnchor().constraintEqualToAnchor_constant_(vib.topAnchor(), 12))
    vib.addConstraint_(stack.leadingAnchor().constraintEqualToAnchor_constant_(vib.leadingAnchor(), 12))
    vib.addConstraint_(stack.trailingAnchor().constraintEqualToAnchor_constant_(vib.trailingAnchor(), -12))
    vib.addConstraint_(stack.bottomAnchor().constraintEqualToAnchor_constant_(vib.bottomAnchor(), -12))
    panel.setContentView_(vib)

    # Init models
    controller._reload_models(servicePopup.titleOfSelectedItem())
    if current_model in list(model_map.get(current_service, {}).keys()):
        modelPopup.selectItemWithTitle_(current_model)
        controller._update_meta(servicePopup.titleOfSelectedItem(), current_model)

    # Show modal
    NSApp().activateIgnoringOtherApps_(True)
    panel.makeKeyAndOrderFront_(None)
    decided = {"ok": False}
    # Wire actions to controller so PyObjC can dispatch selectors
    def _save(_):
        decided["ok"] = True
        try:
            f = panel.frame().size
            ui = cfg.get("ui", {})
            ui["svc_model_size"] = [int(f.width), int(f.height)]
            cfg["ui"] = ui
            save_config(cfg)
            log_debug("Service & Model save with size", width=int(f.width), height=int(f.height))
        except Exception:
            log_exception("svc_model._save")
        panel.close()
    def _cancel(_):
        decided["ok"] = False
        try:
            f = panel.frame().size
            ui = cfg.get("ui", {})
            ui["svc_model_size"] = [int(f.width), int(f.height)]
            cfg["ui"] = ui
            save_config(cfg)
            log_debug("Service & Model cancel with size", width=int(f.width), height=int(f.height))
        except Exception:
            log_exception("svc_model._cancel")
        panel.close()
    def _edit_pricing(_):
        from .pricing import PRICING_PATH
        import subprocess
        try:
            subprocess.run(["open", str(PRICING_PATH)], check=False)
            log_debug("Open pricing.json", path=str(PRICING_PATH))
        except Exception:
            log_exception("svc_model._edit_pricing")
    # Attach as attributes on controller and expose selectors
    controller._do_save = _save
    controller._do_cancel = _cancel
    controller._do_edit_pricing = _edit_pricing
    def doSave_(self, sender): controller._do_save(sender)
    def doCancel_(self, sender): controller._do_cancel(sender)
    def doEditPricing_(self, sender): controller._do_edit_pricing(sender)
    controller.doSave_ = doSave_.__get__(controller, _Controller)
    controller.doCancel_ = doCancel_.__get__(controller, _Controller)
    controller.doEditPricing_ = doEditPricing_.__get__(controller, _Controller)
    saveBtn.setTarget_(controller); saveBtn.setAction_("doSave:")
    cancelBtn.setTarget_(controller); cancelBtn.setAction_("doCancel:")
    editPricingBtn.setTarget_(controller); editPricingBtn.setAction_("doEditPricing:")

    import time
    t0 = time.time()
    while panel.isVisible() and (time.time() - t0) < 30:
        time.sleep(0.02)

    if not decided["ok"]:
        return False, current_service, current_model

    return True, servicePopup.titleOfSelectedItem(), modelPopup.titleOfSelectedItem()
import traceback

from pyqtgraph.exporters import MatplotlibExporter

from bec_widgets.utils.error_popups import SafeSlot, WarningPopupUtility
from bec_widgets.utils.toolbar import MaterialIconAction, SwitchableToolBarAction, ToolbarBundle


class PlotExportBundle(ToolbarBundle):
    """
    A bundle of actions that are hooked in this constructor itself,
    so that you can immediately connect the signals and toggle states.

    This bundle is for a toolbar that controls exporting a plot.
    """

    def __init__(self, bundle_id="mouse_interaction", target_widget=None, **kwargs):
        super().__init__(bundle_id=bundle_id, actions=[], **kwargs)
        self.target_widget = target_widget

        # Create each MaterialIconAction with a parent
        # so the signals can fire even if the toolbar isn't added yet.
        save = MaterialIconAction(
            icon_name="save", tooltip="Open Export Dialog", parent=self.target_widget
        )
        matplotlib = MaterialIconAction(
            icon_name="photo_library", tooltip="Open Matplotlib Dialog", parent=self.target_widget
        )

        switch_export_action = SwitchableToolBarAction(
            actions={"save": save, "matplotlib": matplotlib},
            initial_action="save",
            tooltip="Switchable Action",
            checkable=False,
            parent=self,
        )

        # Add them to the bundle
        self.add_action("export_switch", switch_export_action)

        # Immediately connect signals
        save.action.triggered.connect(self.export_dialog)
        matplotlib.action.triggered.connect(self.matplotlib_dialog)

    @SafeSlot()
    def export_dialog(self):
        """
        Open the export dialog for the plot widget.
        """
        if self.target_widget:
            scene = self.target_widget.plot_item.scene()
            scene.contextMenuItem = self.target_widget.plot_item
            scene.showExportDialog()

    @SafeSlot()
    def matplotlib_dialog(self):
        """
        Export the plot widget to Matplotlib.
        """
        if self.target_widget:
            try:
                import matplotlib as mpl

                MatplotlibExporter(self.target_widget.plot_item).export()
            except ModuleNotFoundError:
                warning_util = WarningPopupUtility()
                warning_util.show_warning(
                    title="Matplotlib not installed",
                    message="Matplotlib is required for this feature.",
                    detailed_text="Please install matplotlib in your Python environment by using 'pip install matplotlib'.",
                )
                return
            except TypeError:
                warning_util = WarningPopupUtility()
                error_msg = traceback.format_exc()
                warning_util.show_warning(
                    title="Matplotlib TypeError",
                    message="Matplotlib exporter could not resolve the plot item.",
                    detailed_text=error_msg,
                )
                return

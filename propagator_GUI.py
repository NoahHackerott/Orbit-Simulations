"""
Orbital Propagator GUI (written by Sonnet 5)
=======================
A professional PySide6 front-end for a custom orbital propagator.

WHERE TO PLUG IN YOUR PROPAGATOR
---------------------------------
Search this file for "HOOK YOUR PROPAGATOR HERE". Replace the
`run_propagation_stub()` function with a call into your own module.

The GUI collects every toggle/setting into a single `config` dict
(see `MainWindow.build_config()` for its exact shape) and hands it to
whatever callable you assign to `PROPAGATE_FN`. Your function must
return a `results` dict with this shape (see docstring on
`run_propagation_stub` for full details):

    {
        "success": bool,
        "message": str,
        "times": np.ndarray, shape (N,)      # seconds from epoch
        "states": np.ndarray, shape (N, 6)   # [rx,ry,rz,vx,vy,vz] km, km/s
        "elements": dict[str, np.ndarray] | None   # optional osculating els
    }

Dependencies: PySide6, matplotlib, numpy
"""

import sys
import traceback
from dataclasses import dataclass, field

import numpy as np

from PySide6.QtCore import Qt, QThread, Signal, QDateTime, QTimer
from PySide6.QtGui import QFont, QColor, QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QSpinBox,
    QGroupBox,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QStackedWidget,
    QTabWidget,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QTextEdit,
    QPlainTextEdit,
    QDateTimeEdit,
    QFrame,
    QSizePolicy,
    QStatusBar,
    QToolBar,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3d projection)


# ======================================================================
# THEME / STYLESHEET
# ======================================================================

ACCENT = "#3ecbff"
ACCENT_DIM = "#1b6f8c"
BG_DARK = "#0d1117"
BG_PANEL = "#141a24"
BG_FIELD = "#1c2430"
BORDER = "#2a3444"
TEXT_MAIN = "#e6edf3"
TEXT_DIM = "#8b98a9"
WARN = "#ff9f1c"
OK = "#3ecb8f"

STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
}}
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_MAIN};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 12px;
}}
QLabel#HeaderTitle {{
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 2px;
    color: {ACCENT};
}}
QLabel#HeaderSubtitle {{
    color: {TEXT_DIM};
    font-size: 11px;
}}
QFrame#HeaderDivider {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 14px;
    padding: 10px 8px 8px 8px;
    background-color: {BG_PANEL};
    font-weight: 600;
    color: {TEXT_MAIN};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: {ACCENT};
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background-color: {BG_PANEL};
    top: -1px;
}}
QTabBar::tab {{
    background-color: {BG_DARK};
    color: {TEXT_DIM};
    padding: 8px 14px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {BG_PANEL};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover {{
    color: {TEXT_MAIN};
}}
QPushButton {{
    background-color: {BG_FIELD};
    color: {TEXT_MAIN};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    border: 1px solid {ACCENT_DIM};
    color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT_DIM};
}}
QPushButton#RunButton {{
    background-color: {ACCENT};
    color: {BG_DARK};
    font-weight: 700;
    font-size: 13px;
    padding: 10px;
    border: none;
    border-radius: 6px;
}}
QPushButton#RunButton:hover {{
    background-color: #63d8ff;
}}
QPushButton#RunButton:disabled {{
    background-color: {BG_FIELD};
    color: {TEXT_DIM};
}}
QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit, QDateTimeEdit {{
    background-color: {BG_FIELD};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 6px;
    color: {TEXT_MAIN};
    selection-background-color: {ACCENT_DIM};
}}
QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 18px;
}}
QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background-color: {BG_FIELD};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
}}
QTableWidget {{
    background-color: {BG_FIELD};
    border: 1px solid {BORDER};
    gridline-color: {BORDER};
    selection-background-color: {ACCENT_DIM};
}}
QHeaderView::section {{
    background-color: {BG_PANEL};
    color: {TEXT_DIM};
    padding: 4px;
    border: 1px solid {BORDER};
}}
QPlainTextEdit, QTextEdit {{
    background-color: #0a0e14;
    color: {OK};
    border: 1px solid {BORDER};
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
}}
QScrollArea {{
    border: none;
}}
QScrollBar:vertical {{
    background: {BG_DARK};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT_DIM};
}}
QStatusBar {{
    background-color: {BG_PANEL};
    color: {TEXT_DIM};
    border-top: 1px solid {BORDER};
}}
QSplitter::handle {{
    background-color: {BG_DARK};
    width: 4px;
}}
"""


# ======================================================================
# SMALL HELPERS
# ======================================================================

def make_spin(minimum, maximum, value, decimals=4, step=1.0, suffix=""):
    box = QDoubleSpinBox()
    box.setRange(minimum, maximum)
    box.setDecimals(decimals)
    box.setValue(value)
    box.setSingleStep(step)
    if suffix:
        box.setSuffix(" " + suffix)
    return box


# ======================================================================
# PANEL: INITIAL STATE
# ======================================================================

class InitialStatePanel(QWidget):
    """Lets the user pick how they specify the initial orbital state."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        top = QFormLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(
            ["Keplerian Elements", "Cartesian State Vector", "TLE (Two-Line Element)"]
        )
        top.addRow("Input Method", self.mode_combo)

        self.epoch_edit = QDateTimeEdit(QDateTime.currentDateTimeUtc())
        self.epoch_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss 'UTC'")
        self.epoch_edit.setCalendarPopup(True)
        top.addRow("Epoch", self.epoch_edit)
        layout.addLayout(top)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_keplerian_page())
        self.stack.addWidget(self._build_cartesian_page())
        self.stack.addWidget(self._build_tle_page())
        layout.addWidget(self.stack)
        layout.addStretch()

        self.mode_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)

    def _build_keplerian_page(self):
        page = QWidget()
        form = QFormLayout(page)
        self.sma = make_spin(100, 1_000_000, 7000.0, 3, 10, "km")
        self.ecc = make_spin(0.0, 0.999, 0.001, 5, 0.001)
        self.inc = make_spin(0.0, 180.0, 28.5, 3, 0.1, "deg")
        self.raan = make_spin(0.0, 360.0, 0.0, 3, 0.1, "deg")
        self.argp = make_spin(0.0, 360.0, 0.0, 3, 0.1, "deg")
        self.ta = make_spin(0.0, 360.0, 0.0, 3, 0.1, "deg")
        form.addRow("Semi-major Axis", self.sma)
        form.addRow("Eccentricity", self.ecc)
        form.addRow("Inclination", self.inc)
        form.addRow("RAAN", self.raan)
        form.addRow("Argument of Perigee", self.argp)
        form.addRow("True Anomaly", self.ta)
        return page

    def _build_cartesian_page(self):
        page = QWidget()
        form = QFormLayout(page)
        self.rx = make_spin(-1e7, 1e7, 7000.0, 3, 1, "km")
        self.ry = make_spin(-1e7, 1e7, 0.0, 3, 1, "km")
        self.rz = make_spin(-1e7, 1e7, 0.0, 3, 1, "km")
        self.vx = make_spin(-50.0, 50.0, 0.0, 5, 0.1, "km/s")
        self.vy = make_spin(-50.0, 50.0, 7.5, 5, 0.1, "km/s")
        self.vz = make_spin(-50.0, 50.0, 0.0, 5, 0.1, "km/s")
        form.addRow("Position X", self.rx)
        form.addRow("Position Y", self.ry)
        form.addRow("Position Z", self.rz)
        form.addRow("Velocity X", self.vx)
        form.addRow("Velocity Y", self.vy)
        form.addRow("Velocity Z", self.vz)
        return page

    def _build_tle_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        mono = QFont("Consolas", 10)
        layout.addWidget(QLabel("Line 1"))
        self.tle1 = QLineEdit()
        self.tle1.setFont(mono)
        self.tle1.setPlaceholderText("1 25544U 98067A   24001.50000000  .00016717  00000-0  ...")
        layout.addWidget(self.tle1)
        layout.addWidget(QLabel("Line 2"))
        self.tle2 = QLineEdit()
        self.tle2.setFont(mono)
        self.tle2.setPlaceholderText("2 25544  51.6416 247.4627 0006703 130.5360 325.0288 ...")
        layout.addWidget(self.tle2)
        layout.addStretch()
        return page

    def get_config(self) -> dict:
        mode = self.mode_combo.currentText()
        cfg = {"mode": mode, "epoch_utc": self.epoch_edit.dateTime().toUTC().toString(Qt.ISODate)}
        if mode == "Keplerian Elements":
            cfg["elements"] = {
                "sma_km": self.sma.value(),
                "ecc": self.ecc.value(),
                "inc_deg": self.inc.value(),
                "raan_deg": self.raan.value(),
                "argp_deg": self.argp.value(),
                "ta_deg": self.ta.value(),
            }
        elif mode == "Cartesian State Vector":
            cfg["state_vector"] = {
                "r_km": [self.rx.value(), self.ry.value(), self.rz.value()],
                "v_km_s": [self.vx.value(), self.vy.value(), self.vz.value()],
            }
        else:
            cfg["tle"] = {"line1": self.tle1.text(), "line2": self.tle2.text()}
        return cfg


# ======================================================================
# PANEL: FORCE MODEL / PERTURBATIONS
# ======================================================================

class ForceModelPanel(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)

        # --- Gravity ---
        grav_box = QGroupBox("Gravity Model")
        grav_form = QFormLayout(grav_box)
        self.j2_check = QCheckBox("J2 (Earth Oblateness)")
        self.j2_check.setChecked(True)
        self.j3_check = QCheckBox("J3")
        self.higher_order_check = QCheckBox("Higher-order Geopotential")
        self.degree_spin = QSpinBox()
        self.degree_spin.setRange(2, 70)
        self.degree_spin.setValue(8)
        self.order_spin = QSpinBox()
        self.order_spin.setRange(0, 70)
        self.order_spin.setValue(8)
        self.degree_spin.setEnabled(False)
        self.order_spin.setEnabled(False)
        self.higher_order_check.toggled.connect(self.degree_spin.setEnabled)
        self.higher_order_check.toggled.connect(self.order_spin.setEnabled)
        grav_form.addRow(self.j2_check)
        grav_form.addRow(self.j3_check)
        grav_form.addRow(self.higher_order_check)
        grav_form.addRow("  Degree", self.degree_spin)
        grav_form.addRow("  Order", self.order_spin)
        outer.addWidget(grav_box)

        # --- Atmospheric Drag ---
        drag_box = QGroupBox("Atmospheric Drag")
        drag_box.setCheckable(True)
        drag_box.setChecked(False)
        self.drag_box = drag_box
        drag_form = QFormLayout(drag_box)
        self.cd = make_spin(0.5, 4.0, 2.2, 2, 0.1)
        self.drag_area = make_spin(0.001, 1000.0, 10.0, 3, 0.1, "m^2")
        self.mass = make_spin(0.1, 1_000_000.0, 500.0, 1, 10, "kg")
        self.atm_model = QComboBox()
        self.atm_model.addItems(["Exponential", "NRLMSISE-00", "Jacchia-Bowman 2008"])
        drag_form.addRow("Drag Coefficient (Cd)", self.cd)
        drag_form.addRow("Reference Area", self.drag_area)
        drag_form.addRow("Mass", self.mass)
        drag_form.addRow("Atmosphere Model", self.atm_model)
        outer.addWidget(drag_box)

        # --- SRP ---
        srp_box = QGroupBox("Solar Radiation Pressure")
        srp_box.setCheckable(True)
        srp_box.setChecked(False)
        self.srp_box = srp_box
        srp_form = QFormLayout(srp_box)
        self.cr = make_spin(0.0, 2.0, 1.3, 2, 0.1)
        self.srp_area = make_spin(0.001, 1000.0, 10.0, 3, 0.1, "m^2")
        self.eclipse_check = QCheckBox("Model Earth Shadow / Eclipses")
        self.eclipse_check.setChecked(True)
        srp_form.addRow("Reflectivity (Cr)", self.cr)
        srp_form.addRow("Reference Area", self.srp_area)
        srp_form.addRow(self.eclipse_check)
        outer.addWidget(srp_box)

        # --- Third body ---
        third_box = QGroupBox("Third-Body Gravity")
        third_box.setCheckable(True)
        third_box.setChecked(False)
        self.third_box = third_box
        third_form = QFormLayout(third_box)
        self.sun_check = QCheckBox("Sun")
        self.moon_check = QCheckBox("Moon")
        self.sun_check.setChecked(True)
        self.moon_check.setChecked(True)
        third_form.addRow(self.sun_check)
        third_form.addRow(self.moon_check)
        outer.addWidget(third_box)

        outer.addStretch()

    def get_config(self) -> dict:
        return {
            "j2": self.j2_check.isChecked(),
            "j3": self.j3_check.isChecked(),
            "higher_order_gravity": {
                "enabled": self.higher_order_check.isChecked(),
                "degree": self.degree_spin.value(),
                "order": self.order_spin.value(),
            },
            "drag": {
                "enabled": self.drag_box.isChecked(),
                "cd": self.cd.value(),
                "area_m2": self.drag_area.value(),
                "mass_kg": self.mass.value(),
                "atm_model": self.atm_model.currentText(),
            },
            "srp": {
                "enabled": self.srp_box.isChecked(),
                "cr": self.cr.value(),
                "area_m2": self.srp_area.value(),
                "model_eclipses": self.eclipse_check.isChecked(),
            },
            "third_body": {
                "enabled": self.third_box.isChecked(),
                "sun": self.sun_check.isChecked(),
                "moon": self.moon_check.isChecked(),
            },
        }


# ======================================================================
# PANEL: PROPAGATOR / INTEGRATOR
# ======================================================================

class PropagatorPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        box = QGroupBox("Integrator")
        form = QFormLayout(box)
        self.integrator_combo = QComboBox()
        self.integrator_combo.addItems(
            ["RK4 (fixed step)", "RK45 / Dormand-Prince (adaptive)", "DOP853 (adaptive)", "Cowell (variable step)"]
        )
        self.step_size = make_spin(0.01, 100000.0, 30.0, 2, 1.0, "s")
        self.rel_tol = make_spin(1e-14, 1e-2, 1e-10, 14, 0, "")
        self.abs_tol = make_spin(1e-14, 1e-2, 1e-12, 14, 0, "")
        form.addRow("Method", self.integrator_combo)
        form.addRow("Fixed Step Size", self.step_size)
        form.addRow("Relative Tolerance", self.rel_tol)
        form.addRow("Absolute Tolerance", self.abs_tol)
        layout.addWidget(box)

        self.integrator_combo.currentIndexChanged.connect(self._sync_enabled)

        span_box = QGroupBox("Propagation Span")
        span_form = QFormLayout(span_box)
        self.duration = make_spin(0.001, 1_000_000.0, 1.0, 3, 0.5)
        self.duration_unit = QComboBox()
        self.duration_unit.addItems(["seconds", "minutes", "hours", "days"])
        self.duration_unit.setCurrentText("days")
        self.output_step = make_spin(0.1, 1_000_000.0, 60.0, 2, 10.0, "s")
        span_form.addRow("Duration", self.duration)
        span_form.addRow("Duration Unit", self.duration_unit)
        span_form.addRow("Output Sampling Step", self.output_step)
        layout.addWidget(span_box)

        frame_box = QGroupBox("Frame & Central Body")
        frame_form = QFormLayout(frame_box)
        self.frame_combo = QComboBox()
        self.frame_combo.addItems(["ECI (J2000 / GCRF)", "ECEF (ITRF)"])
        self.body_combo = QComboBox()
        self.body_combo.addItems(["Earth"])
        frame_form.addRow("Output Frame", self.frame_combo)
        frame_form.addRow("Central Body", self.body_combo)
        layout.addWidget(frame_box)

        layout.addStretch()
        self._sync_enabled()

    def _sync_enabled(self):
        fixed = self.integrator_combo.currentText().startswith("RK4 ")
        self.step_size.setEnabled(fixed)
        self.rel_tol.setEnabled(not fixed)
        self.abs_tol.setEnabled(not fixed)

    def get_config(self) -> dict:
        return {
            "integrator": self.integrator_combo.currentText(),
            "fixed_step_s": self.step_size.value(),
            "rel_tol": self.rel_tol.value(),
            "abs_tol": self.abs_tol.value(),
            "duration": self.duration.value(),
            "duration_unit": self.duration_unit.currentText(),
            "output_step_s": self.output_step.value(),
            "frame": self.frame_combo.currentText(),
            "central_body": self.body_combo.currentText(),
        }


# ======================================================================
# PANEL: MANEUVERS
# ======================================================================

class ManeuverPanel(QWidget):
    COLUMNS = ["Time (s from epoch)", "Duration (s)", "\u0394Vx (km/s)", "\u0394Vy (km/s)", "\u0394Vz (km/s)", "Frame"]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.enable_check = QCheckBox("Enable Thrust Maneuvers")
        layout.addWidget(self.enable_check)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEnabled(False)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Maneuver")
        self.remove_btn = QPushButton("\u2212 Remove Selected")
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.remove_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        note = QLabel(
            "Tip: Impulsive burns can use a very short Duration (e.g. 0.001 s). "
            "\u0394V components are expressed in the selected Frame."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {TEXT_DIM};")
        layout.addWidget(note)
        layout.addStretch()

        self.enable_check.toggled.connect(self.table.setEnabled)
        self.enable_check.toggled.connect(self.add_btn.setEnabled)
        self.enable_check.toggled.connect(self.remove_btn.setEnabled)
        self.add_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)

        self.add_btn.clicked.connect(self.add_row)
        self.remove_btn.clicked.connect(self.remove_selected)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        defaults = ["0.0", "0.001", "0.0", "0.0", "0.0"]
        for col, val in enumerate(defaults):
            self.table.setItem(row, col, QTableWidgetItem(val))
        frame_combo = QComboBox()
        frame_combo.addItems(["RTN (Radial-Transverse-Normal)", "Inertial (ECI)", "VNB (Velocity-Normal-Binormal)"])
        self.table.setCellWidget(row, 5, frame_combo)

    def remove_selected(self):
        for idx in sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True):
            self.table.removeRow(idx)

    def get_config(self) -> dict:
        maneuvers = []
        for row in range(self.table.rowCount()):
            try:
                t = float(self.table.item(row, 0).text())
                dur = float(self.table.item(row, 1).text())
                dvx = float(self.table.item(row, 2).text())
                dvy = float(self.table.item(row, 3).text())
                dvz = float(self.table.item(row, 4).text())
            except (AttributeError, ValueError):
                continue
            frame_widget = self.table.cellWidget(row, 5)
            frame = frame_widget.currentText() if frame_widget else "RTN"
            maneuvers.append(
                {"time_s": t, "duration_s": dur, "dv_km_s": [dvx, dvy, dvz], "frame": frame}
            )
        return {"enabled": self.enable_check.isChecked(), "maneuvers": maneuvers}


# ======================================================================
# PANEL: OUTPUT OPTIONS
# ======================================================================

class OutputPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        plot_box = QGroupBox("Visualization")
        plot_form = QVBoxLayout(plot_box)
        self.plot_3d = QCheckBox("3D Trajectory Plot")
        self.plot_3d.setChecked(True)
        self.plot_ground_track = QCheckBox("Ground Track")
        self.plot_ground_track.setChecked(True)
        self.plot_elements = QCheckBox("Osculating Elements vs. Time")
        plot_form.addWidget(self.plot_3d)
        plot_form.addWidget(self.plot_ground_track)
        plot_form.addWidget(self.plot_elements)
        layout.addWidget(plot_box)

        export_box = QGroupBox("Ephemeris Export")
        export_box.setCheckable(True)
        export_box.setChecked(False)
        self.export_box = export_box
        export_form = QFormLayout(export_box)
        self.export_format = QComboBox()
        self.export_format.addItems(["CSV", "TXT (fixed width)", "JSON"])
        self.export_path = QLineEdit("ephemeris_output")
        export_form.addRow("Format", self.export_format)
        export_form.addRow("File Name (no ext.)", self.export_path)
        layout.addWidget(export_box)

        log_box = QGroupBox("Diagnostics")
        log_form = QVBoxLayout(log_box)
        self.verbose_log = QCheckBox("Verbose Log Output")
        self.verbose_log.setChecked(True)
        self.show_stats = QCheckBox("Show Summary Statistics")
        self.show_stats.setChecked(True)
        log_form.addWidget(self.verbose_log)
        log_form.addWidget(self.show_stats)
        layout.addWidget(log_box)

        layout.addStretch()

    def get_config(self) -> dict:
        return {
            "plot_3d": self.plot_3d.isChecked(),
            "plot_ground_track": self.plot_ground_track.isChecked(),
            "plot_elements": self.plot_elements.isChecked(),
            "export": {
                "enabled": self.export_box.isChecked(),
                "format": self.export_format.currentText(),
                "filename": self.export_path.text(),
            },
            "verbose_log": self.verbose_log.isChecked(),
            "show_stats": self.show_stats.isChecked(),
        }


# ======================================================================
# HOOK YOUR PROPAGATOR HERE
# ======================================================================

def run_propagation_stub(config: dict, log_fn=print) -> dict:
    """
    Placeholder propagator. Replace the body of this function with a call
    into your own propagator module, e.g.:

        from my_propagator import propagate
        def run_propagation_stub(config, log_fn=print):
            return propagate(config, log=log_fn)

    `config` is exactly what MainWindow.build_config() produces -- a plain
    dict containing everything the user toggled in the GUI (initial state,
    force model flags/params, integrator settings, maneuvers, output
    options). Inspect it with a debugger or `log_fn(config)` the first time
    you wire this up.

    Your function must return a dict shaped like:

        {
            "success": bool,
            "message": str,                     # shown in status bar / log
            "times": np.ndarray (N,)             # seconds from epoch
            "states": np.ndarray (N, 6)          # rx,ry,rz,vx,vy,vz [km, km/s]
            "elements": {                        # optional, for elements plot
                "sma_km": np.ndarray (N,),
                "ecc": np.ndarray (N,),
                "inc_deg": np.ndarray (N,),
                ...
            } or None
        }
    """
    log_fn("[stub] No propagator module connected yet -- generating a demo orbit.")
    mu = 398600.4418  # km^3/s^2, Earth
    elements = config["initial_state"].get("elements")
    sma = elements["sma_km"] if elements else 7000.0
    ecc = elements["ecc"] if elements else 0.001
    inc = np.radians(elements["inc_deg"]) if elements else np.radians(28.5)

    duration_s = _duration_seconds(config["propagator"])
    step_s = config["propagator"]["output_step_s"]
    n = max(2, int(duration_s / step_s))
    t = np.linspace(0, duration_s, n)

    period = 2 * np.pi * np.sqrt(sma**3 / mu)
    theta = 2 * np.pi * t / period
    r = sma * (1 - ecc**2) / (1 + ecc * np.cos(theta))

    x = r * np.cos(theta)
    y = r * np.sin(theta) * np.cos(inc)
    z = r * np.sin(theta) * np.sin(inc)
    states = np.zeros((n, 6))
    states[:, 0], states[:, 1], states[:, 2] = x, y, z
    vmag = np.sqrt(mu * (2 / np.maximum(r, 1e-6) - 1 / sma))
    states[:, 3] = -vmag * np.sin(theta)
    states[:, 4] = vmag * np.cos(theta) * np.cos(inc)
    states[:, 5] = vmag * np.cos(theta) * np.sin(inc)

    return {
        "success": True,
        "message": f"Demo propagation complete: {n} samples over {duration_s:,.0f} s.",
        "times": t,
        "states": states,
        "elements": None,
    }


def _duration_seconds(prop_cfg: dict) -> float:
    factor = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}[prop_cfg["duration_unit"]]
    return prop_cfg["duration"] * factor


# Point this at your real function once it's ready.
PROPAGATE_FN = run_propagation_stub


# ======================================================================
# BACKGROUND WORKER (keeps the UI responsive during propagation)
# ======================================================================

class PropagationWorker(QThread):
    log = Signal(str)
    finished_ok = Signal(dict)
    finished_error = Signal(str)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    def run(self):
        try:
            results = PROPAGATE_FN(self.config, log_fn=self.log.emit)
            if not results.get("success", False):
                self.finished_error.emit(results.get("message", "Propagation reported failure."))
                return
            self.finished_ok.emit(results)
        except Exception:
            self.finished_error.emit(traceback.format_exc())


# ======================================================================
# VISUALIZATION PANEL (right-hand side)
# ======================================================================

class VisualizationPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 3D trajectory tab
        self.fig_3d = Figure(figsize=(5, 4), facecolor=BG_PANEL)
        self.canvas_3d = FigureCanvas(self.fig_3d)
        self.ax_3d = self.fig_3d.add_subplot(111, projection="3d")
        self._style_3d_axes()
        self.tabs.addTab(self.canvas_3d, "3D Trajectory")

        # Ground track tab
        self.fig_gt = Figure(figsize=(5, 3), facecolor=BG_PANEL)
        self.canvas_gt = FigureCanvas(self.fig_gt)
        self.ax_gt = self.fig_gt.add_subplot(111)
        self._style_2d_axes(self.ax_gt, "Ground Track", "Longitude (deg)", "Latitude (deg)")
        self.tabs.addTab(self.canvas_gt, "Ground Track")

        # Elements tab
        self.fig_el = Figure(figsize=(5, 3), facecolor=BG_PANEL)
        self.canvas_el = FigureCanvas(self.fig_el)
        self.ax_el = self.fig_el.add_subplot(111)
        self._style_2d_axes(self.ax_el, "Osculating Elements", "Time (s)", "Value")
        self.tabs.addTab(self.canvas_el, "Elements")

        # Log tab
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.tabs.addTab(self.log_view, "Log")

    def _style_3d_axes(self):
        self.ax_3d.set_facecolor(BG_PANEL)
        self.ax_3d.set_xlabel("X (km)", color=TEXT_DIM)
        self.ax_3d.set_ylabel("Y (km)", color=TEXT_DIM)
        self.ax_3d.set_zlabel("Z (km)", color=TEXT_DIM)
        self.ax_3d.tick_params(colors=TEXT_DIM)
        self.ax_3d.set_title("Trajectory", color=TEXT_MAIN)

    def _style_2d_axes(self, ax, title, xlabel, ylabel):
        ax.set_facecolor(BG_PANEL)
        ax.set_title(title, color=TEXT_MAIN)
        ax.set_xlabel(xlabel, color=TEXT_DIM)
        ax.set_ylabel(ylabel, color=TEXT_DIM)
        ax.tick_params(colors=TEXT_DIM)
        for spine in ax.spines.values():
            spine.set_color(BORDER)
        ax.grid(True, color=BORDER, linewidth=0.5, alpha=0.5)

    def append_log(self, text: str):
        self.log_view.appendPlainText(text)

    def plot_results(self, results: dict, opts: dict):
        states = results["states"]
        times = results["times"]

        if opts.get("plot_3d", True):
            self.ax_3d.clear()
            self._style_3d_axes()
            self.ax_3d.plot(states[:, 0], states[:, 1], states[:, 2], color=ACCENT, linewidth=1.2)
            self._draw_earth(self.ax_3d)
            self.canvas_3d.draw()

        if opts.get("plot_ground_track", True):
            self.ax_gt.clear()
            self._style_2d_axes(self.ax_gt, "Ground Track", "Longitude (deg)", "Latitude (deg)")
            r = states[:, :3]
            lon = np.degrees(np.arctan2(r[:, 1], r[:, 0]))
            lat = np.degrees(np.arctan2(r[:, 2], np.sqrt(r[:, 0] ** 2 + r[:, 1] ** 2)))
            self.ax_gt.scatter(lon, lat, s=3, color=ACCENT)
            self.ax_gt.set_xlim(-180, 180)
            self.ax_gt.set_ylim(-90, 90)
            self.canvas_gt.draw()

        if opts.get("plot_elements", False) and results.get("elements"):
            self.ax_el.clear()
            self._style_2d_axes(self.ax_el, "Osculating Elements", "Time (s)", "Value")
            for name, series in results["elements"].items():
                self.ax_el.plot(times, series, linewidth=1.0, label=name)
            self.ax_el.legend(facecolor=BG_PANEL, labelcolor=TEXT_MAIN, fontsize=8)
            self.canvas_el.draw()

        self.tabs.setCurrentIndex(0)

    @staticmethod
    def _draw_earth(ax, radius=6378.137):
        u = np.linspace(0, 2 * np.pi, 24)
        v = np.linspace(0, np.pi, 16)
        x = radius * np.outer(np.cos(u), np.sin(v))
        y = radius * np.outer(np.sin(u), np.sin(v))
        z = radius * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_wireframe(x, y, z, color=ACCENT_DIM, linewidth=0.3, alpha=0.5)


# ======================================================================
# MAIN WINDOW
# ======================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbital Propagator")
        self.resize(1400, 860)
        self.worker = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 12, 14, 8)
        root.setSpacing(8)

        root.addLayout(self._build_header())

        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, stretch=1)

        splitter.addWidget(self._build_left_panel())
        self.viz_panel = VisualizationPanel()
        splitter.addWidget(self.viz_panel)
        splitter.setSizes([440, 960])

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready.")

    # ---------------------------------------------------------- header --
    def _build_header(self):
        header = QVBoxLayout()
        row = QHBoxLayout()
        title = QLabel("ORBITAL PROPAGATOR")
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Mission configuration & trajectory analysis")
        subtitle.setObjectName("HeaderSubtitle")
        text_col = QVBoxLayout()
        text_col.addWidget(title)
        text_col.addWidget(subtitle)
        row.addLayout(text_col)
        row.addStretch()
        header.addLayout(row)

        divider = QFrame()
        divider.setObjectName("HeaderDivider")
        divider.setFrameShape(QFrame.HLine)
        header.addWidget(divider)
        return header

    # ------------------------------------------------------ left panel --
    def _build_left_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.initial_state_panel = InitialStatePanel()
        self.force_model_panel = ForceModelPanel()
        self.propagator_panel = PropagatorPanel()
        self.maneuver_panel = ManeuverPanel()
        self.output_panel = OutputPanel()

        self.tabs.addTab(self._scrollable(self.initial_state_panel), "Initial State")
        self.tabs.addTab(self._scrollable(self.force_model_panel), "Force Model")
        self.tabs.addTab(self._scrollable(self.propagator_panel), "Propagator")
        self.tabs.addTab(self._scrollable(self.maneuver_panel), "Maneuvers")
        self.tabs.addTab(self._scrollable(self.output_panel), "Output")
        layout.addWidget(self.tabs, stretch=1)

        self.run_btn = QPushButton("\u25B6  RUN PROPAGATION")
        self.run_btn.setObjectName("RunButton")
        self.run_btn.clicked.connect(self.run_propagation)
        layout.addWidget(self.run_btn)

        return container

    @staticmethod
    def _scrollable(widget: QWidget) -> QScrollArea:
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(widget)
        return area

    # ------------------------------------------------------- config ----
    def build_config(self) -> dict:
        return {
            "initial_state": self.initial_state_panel.get_config(),
            "force_model": self.force_model_panel.get_config(),
            "propagator": self.propagator_panel.get_config(),
            "maneuvers": self.maneuver_panel.get_config(),
            "output": self.output_panel.get_config(),
        }

    # ------------------------------------------------------- actions ---
    def run_propagation(self):
        config = self.build_config()
        self.viz_panel.append_log("Launching propagation...")
        self.status.showMessage("Propagating...")
        self.run_btn.setEnabled(False)
        self.run_btn.setText("RUNNING...")

        self.worker = PropagationWorker(config)
        self.worker.log.connect(self.viz_panel.append_log)
        self.worker.finished_ok.connect(self._on_success)
        self.worker.finished_error.connect(self._on_error)
        self.worker.finished.connect(self._on_worker_done)
        self.worker.start()

    def _on_success(self, results: dict):
        self.viz_panel.append_log(results.get("message", "Done."))
        self.status.showMessage(results.get("message", "Propagation complete."), 8000)
        self.viz_panel.plot_results(results, self.output_panel.get_config())

    def _on_error(self, message: str):
        self.viz_panel.append_log("ERROR:\n" + message)
        self.status.showMessage("Propagation failed -- see Log tab.", 8000)

    def _on_worker_done(self):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("\u25B6  RUN PROPAGATION")


# ======================================================================
# ENTRY POINT
# ======================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
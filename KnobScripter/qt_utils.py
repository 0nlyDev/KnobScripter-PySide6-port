# -*- coding: utf-8 -*-
"""
qt_utils.py

Handles compatibility between PySide (Nuke < 11), PySide2 (Nuke 11-15), and PySide6 (Nuke 16+).
"""
import sys

try:
    import nuke
except ImportError:
    nuke = None


def _apply_qt_compat_shims(QtCore, QtGui, QtWidgets, Qt):
    if not hasattr(QtWidgets, "QAction") and hasattr(QtGui, "QAction"):
        QtWidgets.QAction = QtGui.QAction
    if not hasattr(QtWidgets, "QShortcut") and hasattr(QtGui, "QShortcut"):
        QtWidgets.QShortcut = QtGui.QShortcut

    if hasattr(QtWidgets, "QApplication") and hasattr(QtWidgets.QApplication, "exec") and not hasattr(QtWidgets.QApplication, "exec_"):
        QtWidgets.QApplication.exec_ = QtWidgets.QApplication.exec
    if hasattr(QtWidgets, "QDialog") and hasattr(QtWidgets.QDialog, "exec") and not hasattr(QtWidgets.QDialog, "exec_"):
        QtWidgets.QDialog.exec_ = QtWidgets.QDialog.exec
    if hasattr(QtWidgets, "QMessageBox") and hasattr(QtWidgets.QMessageBox, "exec") and not hasattr(QtWidgets.QMessageBox, "exec_"):
        QtWidgets.QMessageBox.exec_ = QtWidgets.QMessageBox.exec

    if hasattr(QtGui, "QFontMetrics") and hasattr(QtGui.QFontMetrics, "horizontalAdvance") and not hasattr(QtGui.QFontMetrics, "width"):
        QtGui.QFontMetrics.width = QtGui.QFontMetrics.horizontalAdvance

    if hasattr(QtWidgets, "QLayout") and hasattr(QtWidgets.QLayout, "setContentsMargins") and not hasattr(QtWidgets.QLayout, "setMargin"):
        def _setMargin(self, margin):
            self.setContentsMargins(margin, margin, margin, margin)

        QtWidgets.QLayout.setMargin = _setMargin

    if hasattr(QtGui, "QTextDocument"):
        td = QtGui.QTextDocument
        if not hasattr(td, "FindCaseSensitively"):
            if hasattr(td, "FindFlag") and hasattr(td.FindFlag, "FindCaseSensitively"):
                td.FindCaseSensitively = td.FindFlag.FindCaseSensitively
        if not hasattr(td, "FindBackward"):
            if hasattr(td, "FindFlag") and hasattr(td.FindFlag, "FindBackward"):
                td.FindBackward = td.FindFlag.FindBackward
        if not hasattr(td, "FindFlags"):
            def _FindFlags():
                try:
                    return td.FindFlag(0)
                except Exception:
                    return 0

            td.FindFlags = staticmethod(_FindFlags)

    def _qt_enum_fallback(name, container_attr, value_attr):
        value = None
        if hasattr(Qt, name):
            value = getattr(Qt, name)
        else:
            container = getattr(Qt, container_attr, None)
            if container is None:
                return
            value = getattr(container, value_attr, None)
            if value is None:
                return
        try:
            if not hasattr(Qt, name):
                setattr(Qt, name, value)
        except Exception:
            pass
        try:
            if hasattr(QtCore, "Qt") and not hasattr(QtCore.Qt, name):
                setattr(QtCore.Qt, name, value)
        except Exception:
            return

    _qt_enum_fallback("CaseSensitive", "CaseSensitivity", "CaseSensitive")
    _qt_enum_fallback("CaseInsensitive", "CaseSensitivity", "CaseInsensitive")
    _qt_enum_fallback("ClickFocus", "FocusPolicy", "ClickFocus")
    _qt_enum_fallback("NoFocus", "FocusPolicy", "NoFocus")
    _qt_enum_fallback("TabFocus", "FocusPolicy", "TabFocus")
    _qt_enum_fallback("StrongFocus", "FocusPolicy", "StrongFocus")
    _qt_enum_fallback("Vertical", "Orientation", "Vertical")
    _qt_enum_fallback("Horizontal", "Orientation", "Horizontal")
    _qt_enum_fallback("WindowStaysOnTopHint", "WindowType", "WindowStaysOnTopHint")
    _qt_enum_fallback("FramelessWindowHint", "WindowType", "FramelessWindowHint")
    _qt_enum_fallback("Popup", "WindowType", "Popup")
    _qt_enum_fallback("NoTextInteraction", "TextInteractionFlag", "NoTextInteraction")
    _qt_enum_fallback("LeftButton", "MouseButton", "LeftButton")
    _qt_enum_fallback("RightButton", "MouseButton", "RightButton")
    _qt_enum_fallback("MiddleButton", "MouseButton", "MiddleButton")
    _qt_enum_fallback("NoPen", "PenStyle", "NoPen")
    _qt_enum_fallback("ScrollBarAlwaysOff", "ScrollBarPolicy", "ScrollBarAlwaysOff")
    _qt_enum_fallback("WA_TransparentForMouseEvents", "WidgetAttribute", "WA_TransparentForMouseEvents")
    _qt_enum_fallback("AlignLeft", "AlignmentFlag", "AlignLeft")
    _qt_enum_fallback("AlignRight", "AlignmentFlag", "AlignRight")
    _qt_enum_fallback("AlignTop", "AlignmentFlag", "AlignTop")
    _qt_enum_fallback("AlignVCenter", "AlignmentFlag", "AlignVCenter")
    _qt_enum_fallback("AlignHCenter", "AlignmentFlag", "AlignHCenter")


def text_document_find_flags(match_case=False, backwards=False):
    td = getattr(QtGui, "QTextDocument", None)
    if td is None:
        return 0

    try:
        flags = td.FindFlags()
    except Exception:
        try:
            flags = td.FindFlag(0)
        except Exception:
            flags = 0

    if backwards:
        if hasattr(td, "FindBackward"):
            flags = flags | td.FindBackward
        elif hasattr(td, "FindFlag") and hasattr(td.FindFlag, "FindBackward"):
            flags = flags | td.FindFlag.FindBackward

    if match_case:
        if hasattr(td, "FindCaseSensitively"):
            flags = flags | td.FindCaseSensitively
        elif hasattr(td, "FindFlag") and hasattr(td.FindFlag, "FindCaseSensitively"):
            flags = flags | td.FindFlag.FindCaseSensitively

    return flags


if nuke is not None and hasattr(nuke, "NUKE_VERSION_MAJOR") and nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtGui, QtGui as QtWidgets
    from PySide.QtCore import Qt
elif nuke is not None and hasattr(nuke, "NUKE_VERSION_MAJOR") and nuke.NUKE_VERSION_MAJOR < 16:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Qt
else:
    # Nuke 16+ uses PySide6
    from PySide6 import QtWidgets, QtGui, QtCore
    from PySide6.QtCore import Qt
    
    # Compatibility fixes for PySide6
    
    if not hasattr(QtCore, "QRegExp"):
        # Wrapper using QRegularExpression
        class WrapperQRegExp(QtCore.QRegularExpression):
            def __init__(self, pattern="", cs=None, syntax=QtCore.QRegularExpression.PatternOption.NoPatternOption):
                super().__init__(pattern, syntax)
                self._last_match = None
            
            def indexIn(self, text, offset=0):
                self._last_match = self.match(text, offset)
                return self._last_match.capturedStart()
            
            def pos(self, nth=0):
                if self._last_match:
                    return self._last_match.capturedStart(nth)
                return -1
            
            def cap(self, nth=0):
                if self._last_match:
                    return self._last_match.captured(nth)
                return ""
            
            def matchedLength(self):
                if self._last_match:
                    return self._last_match.capturedLength()
                return -1
                
        QtCore.QRegExp = WrapperQRegExp
            
    # TextEdit/PlainTextEdit tab stop compatibility
    for cls in [QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit]:
        if not hasattr(cls, "setTabStopWidth") and hasattr(cls, "setTabStopDistance"):
            cls.setTabStopWidth = cls.setTabStopDistance
        if not hasattr(cls, "tabStopWidth") and hasattr(cls, "tabStopDistance"):
            cls.tabStopWidth = cls.tabStopDistance

    _apply_qt_compat_shims(QtCore=QtCore, QtGui=QtGui, QtWidgets=QtWidgets, Qt=Qt)

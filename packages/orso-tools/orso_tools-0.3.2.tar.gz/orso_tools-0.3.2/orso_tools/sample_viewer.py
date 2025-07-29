import os

from orsopy.fileio import ComplexValue, Value
from orsopy.fileio import model_language as ml
from PySide6 import QtCore, QtSvgWidgets


class SampleViewer(QtSvgWidgets.QSvgWidget):
    def __init__(self, parent=None):
        super(SampleViewer, self).__init__(parent)

    COLORS = ["#ffaaaa", "#aaffaa", "#aaaaff", "#ff00ff", "#00ffff"]

    def no_sample(self):
        svg = """<svg width="100" height="100" viewbox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <text x="50" y="8" fill="black" font-size="6" text-anchor="middle">No sample model in dataset.</text>
        </svg>"""
        self.renderer().load(QtCore.QByteArray(svg))
        self.renderer().setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def preparing_sample(self):
        svg = """<svg width="100" height="100" viewbox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <text x="50" y="8" fill="black" font-size="6" text-anchor="middle">Evaluating model...</text>
        </svg>"""
        self.renderer().load(QtCore.QByteArray(svg))
        self.renderer().setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def show_sample_model(self, model: "ml.SampleModel"):
        items = model.resolve_stack()

        pos, height, svg_inside = self.build_substack(10, 10, 0, items)

        svg = f"""<svg width="100" height="{height}" viewbox="0 0 {height} 100" xmlns="http://www.w3.org/2000/svg">
        <text x="50" y="8" fill="black" font-size="6" text-anchor="middle">Sample Model:</text>
        {svg_inside}
</svg>"""
        self.renderer().load(QtCore.QByteArray(svg))
        self.renderer().setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def build_substack(self, pos, height, indent, items):
        svg_inside = ""
        for item in items:
            if isinstance(item, ml.Layer):
                width = 100 - 5 - indent * 1.2
                svg_inside += f"""
    <rect width="{width}" height="18" x="{indent + 5}" y="{pos + 1}" rx="2" ry="2" fill="#cccccc" />
    <text x="{indent + 10}" y="{pos + 8}" fill="black" font-size="4">Layer {item.original_name or ''}</text>
    <text x="{indent + 20}" y="{pos + 13}" fill="black" font-size="3">
        thickness={item.thickness.magnitude} {item.thickness.unit}
        | roughness={item.roughness.magnitude} {item.roughness.unit}
    </text>"""
                pos += 20
                height += 20
            elif isinstance(item, ml.SubStack):
                new_pos, new_height, svg_substack = self.build_substack(pos + 7, height + 8, indent + 5, item.sequence)
                width = 100 - 5 - indent * 1.1
                pre_str = ""
                post_str = ""
                if item.repetitions != 1:
                    pre_str = f"{item.repetitions} X "
                if getattr(item, "environment", None) is not None:
                    post_str = f" in {item.environment.original_name or repr(item.environment)}"

                svg_inside += f"""
    <rect width="{width}" height="{new_height - height}" x="{indent + 5}" y="{pos}" rx="2" ry="2"
        fill="{self.COLORS[(indent // 5) % len(self.COLORS)]}" />
    <text x="{indent + 10}" y="{pos + 6}" fill="black" font-size="4">
        {pre_str}SubStack {item.original_name or ''}{post_str}
    </text>"""

                svg_inside += svg_substack
                pos = new_pos + 1
                height = new_height
            elif isinstance(item, ml.SubStackType):
                width = 100 - 5 - indent * 1.2
                parameter_text = ""
                param_height = 0
                for param, value in item.to_dict().items():
                    if param in ["sub_stack_class", "original_name"]:
                        continue
                    obj = getattr(item, param)
                    value_str = repr(obj)
                    if isinstance(obj, Value):
                        value_str = f"{obj.magnitude} {obj.unit}"
                    elif isinstance(obj, ComplexValue):
                        value_str = f"{obj.real}+{obj.imag}i {obj.unit}"
                    elif isinstance(obj, ml.Material):
                        value_str = getattr(obj, "original_name", obj.formula)
                    parameter_text += f"""
    <text x="{indent + 12}" y="{pos + 13 + param_height}" fill="black" font-size="3">{param}={value_str}</text>"""
                    param_height += 3
                svg_inside += f"""
    <rect width="{width}" height="{10 + param_height}" x="{indent + 5}" y="{pos + 1}" rx="2" ry="2" fill="#ffffaa" />
    <text x="{indent + 10}" y="{pos + 8}" fill="black" font-size="4">
        {item.__class__.__name__} {item.original_name or ''}
    </text>"""
                svg_inside += parameter_text
                pos += 12 + param_height
                height += 12 + param_height

        return pos, height, svg_inside

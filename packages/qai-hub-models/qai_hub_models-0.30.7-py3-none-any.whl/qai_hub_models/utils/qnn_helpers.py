# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from __future__ import annotations

import json
from pathlib import Path

from qai_hub.client import Model, SourceModelType


def onnx_elem_type_to_str(elem_type: int) -> str:
    if elem_type == 1:
        return "float32"
    elif elem_type == 2:
        return "uint8"
    elif elem_type == 3:
        return "int8"
    elif elem_type == 6:
        return "int8"
    elif elem_type == 10:
        return "float16"
    raise ValueError("Unsupported elem_type.")


def load_encodings(output_path: Path, model_name: str) -> dict:
    encodings_file = output_path / f"{model_name}.aimet" / f"{model_name}.encodings"
    with open(encodings_file) as f:
        encodings = json.load(f)
    return encodings["activation_encodings"]


def is_qnn_hub_model(model: Model):
    return model.model_type in [
        SourceModelType.QNN_CONTEXT_BINARY,
        SourceModelType.QNN_LIB_AARCH64_ANDROID,
        SourceModelType.QNN_LIB_X86_64_LINUX,
    ]

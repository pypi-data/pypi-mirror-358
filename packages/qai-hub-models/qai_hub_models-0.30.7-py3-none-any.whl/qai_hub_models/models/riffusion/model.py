# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from __future__ import annotations

from qai_hub_models.utils.asset_loaders import CachedWebModelAsset
from qai_hub_models.utils.base_model import (
    BasePrecompiledModel,
    CollectionModel,
    PrecompiledCollectionModel,
)
from qai_hub_models.utils.input_spec import InputSpec

MODEL_ID = __name__.split(".")[-2]
MODEL_ASSET_VERSION = 1
TEXT_ENCODER = "text_encoder.serialized.bin"
UNET_DIFFUSER = "unet.serialized.bin"
VAE_DECODER = "vae_decoder.serialized.bin"


class ClipVITTextEncoder(BasePrecompiledModel):
    """
    CLIP-ViT based Text Encoder.

    Pre-trained, quantized (int8 weight, uint16 activations)
    and compiled into serialized binary for Qualcomm Snapdragon Gen2+.
    """

    @classmethod
    def from_precompiled(cls) -> ClipVITTextEncoder:
        text_encoder_path = CachedWebModelAsset.from_asset_store(
            MODEL_ID, MODEL_ASSET_VERSION, TEXT_ENCODER
        ).fetch()
        return ClipVITTextEncoder(text_encoder_path)

    @staticmethod
    def get_input_spec() -> InputSpec:
        return {"input_1": ((1, 77), "int32")}

    @staticmethod
    def get_output_names() -> list[str]:
        return ["embeddings"]


class Unet(BasePrecompiledModel):
    """
    UNet model to denoise image in latent space.

    Pre-trained, quantized (int8 weight, uint16 activations)
    and compiled into serialized binary for Qualcomm Snapdragon Gen2+.
    """

    @classmethod
    def from_precompiled(cls) -> Unet:
        model_path = CachedWebModelAsset.from_asset_store(
            MODEL_ID, MODEL_ASSET_VERSION, UNET_DIFFUSER
        ).fetch()
        return Unet(model_path)

    @staticmethod
    def get_input_spec() -> InputSpec:
        return {
            "input_1": ((1, 64, 64, 4), "float32"),
            "input_2": ((1, 1280), "float32"),
            "input_3": ((1, 77, 768), "float32"),
        }

    @staticmethod
    def get_output_names() -> list[str]:
        return ["noise"]


class VAEDecoder(BasePrecompiledModel):
    """
    Decodes image from latent into output generated image.

    Pre-trained, quantized (int8 weight, uint16 activations)
    and compiled into serialized binary for Qualcomm Snapdragon Gen2+.
    """

    @classmethod
    def from_precompiled(cls) -> VAEDecoder:
        model_path = CachedWebModelAsset.from_asset_store(
            MODEL_ID, MODEL_ASSET_VERSION, VAE_DECODER
        ).fetch()
        return VAEDecoder(model_path)

    @staticmethod
    def get_input_spec() -> InputSpec:
        return {"input_1": ((1, 64, 64, 4), "float32")}

    @staticmethod
    def get_output_names() -> list[str]:
        return ["output_image"]


@CollectionModel.add_component(ClipVITTextEncoder)
@CollectionModel.add_component(Unet)
@CollectionModel.add_component(VAEDecoder)
class Riffusion(PrecompiledCollectionModel):
    """
    All three models are pre-trained, quantized (int8 weight, uint16 activations)
    and compiled into serialized binary for Qualcomm Snapdragon Gen2+.
    """

    pass

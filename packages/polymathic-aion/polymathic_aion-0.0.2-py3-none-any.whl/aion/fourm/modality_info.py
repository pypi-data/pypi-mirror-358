# Copyright 2024 EPFL and Apple Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from functools import partial
import hashlib

from .modality_transforms import TokTransform
from .decoder_embeddings import ImageTokenDecoderEmbedding, SequenceDecoderEmbedding
from .encoder_embeddings import (
    ImageTokenEncoderEmbedding,
    SequenceEncoderEmbedding,
)


def generate_uint15_hash(seed_str):
    """Generates a hash of the seed string as an unsigned int15 integer"""
    return int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest(), 16) % (2**15)


MODALITY_INFO = {
    # HSC modalities
    "tok_image_hsc": {
        "input_size": 96,
        "patch_size": 4,
        "vocab_size": 4375,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding,
            vocab_size=4375,
            patch_size=4,
            image_size=(96, 96),
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding,
            vocab_size=4375,
            patch_size=4,
            image_size=(96, 96),
        ),
        "min_tokens": 0,
        "max_tokens": None,
        "type": "img",
        "id": generate_uint15_hash("tok_image_hsc"),
        "pretokenized": True,
    },
    "tok_mag_g": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_mag_g"),
        "pretokenized": True,
    },
    "tok_mag_r": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_mag_r"),
        "pretokenized": True,
    },
    "tok_mag_i": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_mag_i"),
        "pretokenized": True,
    },
    "tok_mag_z": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_mag_z"),
        "pretokenized": True,
    },
    "tok_mag_y": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_mag_y"),
        "pretokenized": True,
    },
    "tok_a_g": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_a_g"),
        "pretokenized": True,
    },
    "tok_a_r": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_a_r"),
        "pretokenized": True,
    },
    "tok_a_i": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_a_i"),
        "pretokenized": True,
    },
    "tok_a_z": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_a_z"),
        "pretokenized": True,
    },
    "tok_a_y": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_a_y"),
        "pretokenized": True,
    },
    "tok_shape11": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_shape11"),
        "pretokenized": True,
    },
    "tok_shape12": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_shape12"),
        "pretokenized": True,
    },
    "tok_shape22": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_shape22"),
        "pretokenized": True,
    },
    # Legacy survey modalities
    "tok_image": {
        "input_size": 96,
        "patch_size": 4,
        "vocab_size": 4375,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding,
            vocab_size=4375,
            patch_size=4,
            image_size=(96, 96),
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding,
            vocab_size=4375,
            patch_size=4,
            image_size=(96, 96),
        ),
        "min_tokens": 0,
        "max_tokens": None,
        "type": "img",
        "id": generate_uint15_hash("tok_image"),
        "pretokenized": True,
    },
    "tok_segmap": {
        "input_size": 96,
        "patch_size": 8,
        "vocab_size": 1000,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding,
            vocab_size=1000,
            patch_size=8,
            image_size=(96, 96),
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding,
            vocab_size=1000,
            patch_size=8,
            image_size=(96, 96),
        ),
        "min_tokens": 0,
        "max_tokens": None,
        "type": "img",
        "id": generate_uint15_hash("tok_segmap"),
        "pretokenized": True,
    },
    "tok_ebv": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_ebv"),
        "pretokenized": True,
    },
    "tok_flux_g": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_g"),
        "pretokenized": True,
    },
    "tok_flux_r": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_r"),
        "pretokenized": True,
    },
    "tok_flux_i": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_i"),
        "pretokenized": True,
    },
    "tok_flux_z": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_z"),
        "pretokenized": True,
    },
    "tok_flux_w1": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_w1"),
        "pretokenized": True,
    },
    "tok_flux_w2": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_w2"),
        "pretokenized": True,
    },
    "tok_flux_w3": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_w3"),
        "pretokenized": True,
    },
    "tok_flux_w4": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_w4"),
        "pretokenized": True,
    },
    "tok_shape_r": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_shape_r"),
        "pretokenized": True,
    },
    "tok_shape_e1": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_shape_e1"),
        "pretokenized": True,
    },
    "tok_shape_e2": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_shape_e2"),
        "pretokenized": True,
    },
    # SDSS and DESI modalities
    "tok_spectrum_desi": {
        "input_size": 273,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(273, 1),
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(273, 1),
        ),
        "min_tokens": 0,
        "max_tokens": 273,
        "type": "img",
        "id": generate_uint15_hash("tok_spectrum_desi"),
        "pretokenized": True,
    },
    "tok_spectrum_sdss": {
        "input_size": 273,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(273, 1),
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(273, 1),
        ),
        "min_tokens": 0,
        "max_tokens": 273,
        "type": "img",
        "id": generate_uint15_hash("tok_spectrum_sdss"),
        "pretokenized": True,
    },
    "tok_z": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1025,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1025, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1025, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_z"),
        "pretokenized": True,
    },
    "catalog": {
        # vocabulary size: 3_468
        #   - 96 * 2 + 1024 * 3 catalog tokens ([X, Y, E1, E2, R])
        #   - 200 sentinel tokens
        #   - 1 start token
        #   - 1 end token
        #   - 1 padding token
        #   - 1 unk token
        "vocab_size": 3_468,
        "vocab_offset": 204,
        "codec_pad_id": 9999,
        "encoder_embedding": partial(
            SequenceEncoderEmbedding, vocab_size=3_468, max_length=50, padding_idx=0
        ),
        "decoder_embedding": partial(
            SequenceDecoderEmbedding, vocab_size=3_468, max_length=50, padding_idx=0
        ),
        "min_tokens": 0,
        "max_tokens": 50,
        "type": "seq_token",
        "id": generate_uint15_hash("catalog"),
        "pretokenized": True,
    },
    # GAIA modalities
    "tok_xp_bp": {
        "input_size": 55,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(55, 1),
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(55, 1),
        ),
        "min_tokens": 0,
        "max_tokens": 55,
        "type": "img",
        "id": generate_uint15_hash("tok_xp_bp"),
        "pretokenized": True,
    },
    "tok_xp_rp": {
        "input_size": 55,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(55, 1),
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding,
            vocab_size=1024,
            patch_size=1,
            image_size=(55, 1),
        ),
        "min_tokens": 0,
        "max_tokens": 55,
        "type": "img",
        "id": generate_uint15_hash("tok_xp_rp"),
        "pretokenized": True,
    },
    "tok_flux_g_gaia": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_g_gaia"),
        "pretokenized": True,
    },
    "tok_flux_bp_gaia": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_bp_gaia"),
        "pretokenized": True,
    },
    "tok_flux_rp_gaia": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_flux_rp_gaia"),
        "pretokenized": True,
    },
    "tok_parallax": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_parallax"),
        "pretokenized": True,
    },
    "tok_ra": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_ra"),
        "pretokenized": True,
    },
    "tok_dec": {
        "input_size": 1,
        "patch_size": 1,
        "vocab_size": 1024,
        "encoder_embedding": partial(
            ImageTokenEncoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "decoder_embedding": partial(
            ImageTokenDecoderEmbedding, vocab_size=1024, patch_size=1, image_size=(1, 1)
        ),
        "min_tokens": 0,
        "max_tokens": 1,
        "type": "img",
        "id": generate_uint15_hash("tok_dec"),
        "pretokenized": True,
    },
}


# Note: @res suffix is ignored for modality transforms
MODALITY_TRANSFORMS = {
    "tok_rgb": TokTransform(),
    "tok_segmap": TokTransform(),
    "tok_depth": TokTransform(),
    "tok_normal": TokTransform(),
    "tok_semseg": TokTransform(),
    "tok_clip": TokTransform(),
    "tok_image": TokTransform(),
    "tok_ebv": TokTransform(),
    "tok_flux_g": TokTransform(),
    "tok_flux_r": TokTransform(),
    "tok_flux_i": TokTransform(),
    "tok_flux_z": TokTransform(),
    "tok_flux_w1": TokTransform(),
    "tok_flux_w2": TokTransform(),
    "tok_flux_w3": TokTransform(),
    "tok_flux_w4": TokTransform(),
    "tok_shape_r": TokTransform(),
    "tok_shape_e1": TokTransform(),
    "tok_shape_e2": TokTransform(),
    "tok_image_hsc": TokTransform(),
    "tok_mag_g": TokTransform(),
    "tok_mag_r": TokTransform(),
    "tok_mag_i": TokTransform(),
    "tok_mag_z": TokTransform(),
    "tok_mag_y": TokTransform(),
    "tok_a_g": TokTransform(),
    "tok_a_r": TokTransform(),
    "tok_a_i": TokTransform(),
    "tok_a_z": TokTransform(),
    "tok_a_y": TokTransform(),
    "tok_shape11": TokTransform(),
    "tok_shape12": TokTransform(),
    "tok_shape22": TokTransform(),
    "tok_spectrum_desi": TokTransform(),
    "tok_spectrum_sdss": TokTransform(),
    "tok_z": TokTransform(),
    "catalog": TokTransform(),
    "tok_xp_bp": TokTransform(),
    "tok_xp_rp": TokTransform(),
    "tok_flux_g_gaia": TokTransform(),
    "tok_flux_bp_gaia": TokTransform(),
    "tok_flux_rp_gaia": TokTransform(),
    "tok_parallax": TokTransform(),
    "tok_ra": TokTransform(),
    "tok_dec": TokTransform(),
}

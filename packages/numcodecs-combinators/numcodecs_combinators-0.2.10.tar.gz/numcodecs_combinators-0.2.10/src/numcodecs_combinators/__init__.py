"""
Combinator codecs for the [`numcodecs`][numcodecs] buffer compression API.

The following combinators, implementing the
[`CodecCombinatorMixin`][numcodecs_combinators.abc.CodecCombinatorMixin] are
provided:

- [`CodecStack`][numcodecs_combinators.stack.CodecStack]: a stack of codecs
- [`FramedCodecStack`][numcodecs_combinators.framed.FramedCodecStack]: a stack
  of codecs that is framed with array data type and shape information
- [`PickBestCodec`][numcodecs_combinators.best.PickBestCodec]: pick the best
  codec to encode the data
"""

__all__ = ["map_codec"]

import functools
from typing import Callable

from numcodecs.abc import Codec

from . import abc as abc
from . import best as best
from . import framed as framed
from . import stack as stack


def map_codec(codec: Codec, mapper: Callable[[Codec], Codec]) -> Codec:
    """
    Apply the `mapper` callable to the `codec` and return the mapped codec.

    If the `codec` implements the
    [`CodecCombinatorMixin`][numcodecs_combinators.abc.CodecCombinatorMixin]
    mixin, the `mapper` is applied to its inner codecs recursively.

    Parameters
    ----------
    mapper : Callable[[Codec], Codec]
        The callable that should be applied to the codec.

    Returns
    -------
    mapped : Codec
        The mapped codec.
    """
    if isinstance(codec, abc.CodecCombinatorMixin):
        codec = codec.map(functools.partial(map_codec, mapper=mapper))

    return mapper(codec)

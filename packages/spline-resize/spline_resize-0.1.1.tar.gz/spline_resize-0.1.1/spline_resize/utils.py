import math
import torch
POLE = 8 ** .5 - 3


def apply_filter(im, mask_value=None):
    if mask_value is not None:
        mask = im == mask_value
    out_im = im.clone()
    for i in range(3):
        out_im = filter_last_dim(out_im.permute(0, 1, 3, 4, 2))
    if mask_value is not None:
        out_im[mask] = mask_value
    return out_im


def filter_last_dim(im):
    im *= (1. - POLE) * (1. - 1. / POLE)
    im[..., 0] = initial_discrete_cosine_transform(im)
    for i in range(1, im.shape[-1]):
        im[..., i].add_(im[..., i - 1], alpha=POLE)
    im[..., -1] = (POLE * im[..., -2] + im[..., -1]) * (POLE / (POLE ** 2 - 1))
    for i in range(im.shape[-1] - 2, -1, -1):
        im[..., i] = POLE * (im[..., i + 1] - im[..., i])
    return im


def initial_discrete_cosine_transform(im):
    poles = POLE ** torch.arange(im.shape[-1], dtype=im.dtype, device=im.device)
    max_iter = int(math.ceil(-30 / math.log(abs(POLE))))
    if max_iter < im.shape[-1]:
        return im[..., :max_iter] @ poles[..., :max_iter]
    else:
        a = POLE ** (1 * im.shape[-1] - 1)
        poles += a ** 2 / poles
        return (im[..., 0] + im[..., 1:-1] @ poles[1:-1] + a * im[..., -1]) / (1 - a ** 2)

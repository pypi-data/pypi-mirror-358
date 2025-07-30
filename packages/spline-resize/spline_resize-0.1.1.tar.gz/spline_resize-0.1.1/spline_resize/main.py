import torch
import torch.nn.functional as F

from .utils import apply_filter


def resize(im, size=None, scale_factor=None, align_corners=False, prefilter=True, mask_value=None):
    assert im.ndim == 5, 'Image must be 5D'
    assert not (size is None and scale_factor is None), 'Either size or scale_factor must be provided'
    if size is None:
        scale_factor = 3 * [scale_factor] if isinstance(scale_factor, (int, float)) else scale_factor
        size = [int(round(f * s)) for f, s in zip(scale_factor, im.shape[-3:])]
    grid = F.affine_grid(torch.eye(4, device=im.device)[None, :3], [im.shape[0], 3, *size], align_corners=align_corners)
    return grid_sample(im, grid, align_corners=align_corners, prefilter=prefilter, mask_value=mask_value)


def grid_sample(im, grid, align_corners=False, prefilter=True, mask_value=None):
    assert im.ndim == 5 and grid.ndim == 5 and len(im) == len(grid), 'Image and grid must have same length and be 5D'
    sample_im = apply_filter(im, mask_value) if prefilter else im.clone()
    weights, idxs = fit_splines(get_indizes(grid, im.shape[-3:], align_corners), im.shape[-3:])
    out_im = 0 * weights[0][0][None].repeat(im.shape[1], 1, 1)
    sample_im = sample_im.permute(1, 0, 2, 3, 4).reshape(im.shape[1], im.shape[0], -1)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                node_im = sample_im.gather(-1, (idxs[0][i] + idxs[1][j] + idxs[2][k])[None].repeat(im.shape[1], 1 , 1).long())
                node_im *= (weights[0][i] * weights[1][j] * weights[2][k])[None]
                out_im += node_im
    return out_im.view(*out_im.shape[:2], *grid.shape[-4:-1]).permute(1, 0, 2, 3, 4)


def fit_splines(idx, shape):
    idx = idx.view(idx.shape[0], -1, idx.shape[-1])
    strides = (shape[-2] * shape[-1], shape[-1], 1)
    weights, idxs = [], []
    for i, (s, stride) in enumerate(zip(shape, strides)):
        idx_i_floor = (idx[..., i] - .5).floor()
        node_weights, node_idxs = [], []
        for node in range(3):
            node_idx = idx_i_floor + node
            floor_mask = node_idx < 0
            ceil_mask = node_idx >= s
            node_idx[floor_mask] = 0
            node_idx[ceil_mask] = s - 1
            node_idxs.append(node_idx.int() * stride)
            weight = spline_weight(idx[..., i] - idx_i_floor - node)
            weight[floor_mask | ceil_mask] = 0
            node_weights.append(weight)
        weights.append(node_weights)
        idxs.append(node_idxs)
    return weights, idxs


def spline_weight(x):
    x = x.abs()
    return torch.where(x < .5, .75 - x ** 2, .5 * (1.5 - x) ** 2)


def get_indizes(grid, shape, align_corners):
    shape = torch.tensor(shape, dtype=grid.dtype, device=grid.device)
    align = 1 if align_corners else 1 - 1 / shape.flip(-1)
    return (grid.flip(-1) / align + 1) * .5 * (shape - 1)

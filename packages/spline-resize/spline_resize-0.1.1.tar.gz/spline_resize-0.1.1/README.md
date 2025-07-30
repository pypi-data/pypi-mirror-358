# spline-resize
Resize (currently only 3D, maybe later 2D) PyTorch tensors via B-spline interpolation 

B-spline results in **higher quality than `'trilinear'`**(=best [PyTorch-native](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.interpolate.html) 3D method)

**Currently, `spline-resize` only supports zero padding!**

🛠️ **Install** via: `pip install spline-resize`
## Usage 💡
To **resize** a 3D image(=5D tensor, due to batch and channel dim.) use `resize`
```python
import torch
import spline_resize as sr

x = torch.linspace(0, 1, 5**3).view(1, 1, 5, 5, 5)
x_large = sr.resize(x, size=(7, 7, 7))
```
The arguments `size`, `scale_factor` & `align_corners` are explained [here](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.interpolate.html)

To **resample** a 3D image with a grid of coordinates use `grid_sample`
```python
import torch.nn.functional as F

# affine matrix that rotates image
affine = torch.tensor([[[1, .1, 0, 0],
                        [.1, 1, 0, 0],
                        [0, 0, 1, 0]]])
grid = F.affine_grid(affine, size=(1, 3, 7, 7, 7))

x = torch.linspace(0, 1, 5**3).view(1, 1, 5, 5, 5)
x_large_rotated = sr.grid_sample(x, grid)
```
Both `resize` and `grid_sample` also take the function arguments
- `prefilter`: Applies prefilter usually used prior to sampling. Default: `True`
- `mask_value`: Exclude value (e.g. 0) from prefilter. Default: `None`

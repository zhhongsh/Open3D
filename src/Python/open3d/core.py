import open3d as o3d
import open3d.open3d_pybind as open3d_pybind
import numpy as np


def _numpy_dtype_to_dtype(numpy_dtype):
    if numpy_dtype == np.float32:
        return o3d.Dtype.Float32
    elif numpy_dtype == np.float64:
        return o3d.Dtype.Float64
    elif numpy_dtype == np.int32:
        return o3d.Dtype.Int32
    elif numpy_dtype == np.int64:
        return o3d.Dtype.Int64
    elif numpy_dtype == np.uint8:
        return o3d.Dtype.UInt8
    else:
        raise ValueError("Unsupported numpy dtype:", numpy_dtype)


class SizeVector(open3d_pybind.SizeVector):

    def __init__(self, values=None):
        if values is None:
            values = []
        # TODO: determine whether conversion can be done in C++ as well.
        if isinstance(values, tuple) or isinstance(values, list):
            values = np.array(values)
        if not isinstance(values, np.ndarray) or values.ndim != 1:
            raise ValueError(
                "SizeVector only takes 1-D list, tuple or Numpy array.")
        super(SizeVector, self).__init__(values.astype(np.int64))


def cast_to_py_tensor(func):
    """
    Args:
        func: function returning a `o3d.open3d_pybind.Tensor`.

    Return:
        A function which returns a python object `o3d.Tensor`.
    """

    def wrapped_func(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        wrapped_result = Tensor([])
        wrapped_result.shallow_copy_from(result)
        return wrapped_result

    return wrapped_func


def _to_o3d_tensor_key(key):

    if isinstance(key, int):
        return o3d.open3d_pybind.TensorKey.index(key)
    elif isinstance(key, slice):
        return o3d.open3d_pybind.TensorKey.slice(
            o3d.none if key.start == None else key.start,
            o3d.none if key.stop == None else key.stop,
            o3d.none if key.step == None else key.step)
    elif isinstance(key, (tuple, list)):
        key = np.array(key).astype(np.int64)
        return o3d.open3d_pybind.TensorKey.index_tensor(Tensor(key))
    elif isinstance(key, np.ndarray):
        key = key.astype(np.int64)
        return o3d.open3d_pybind.TensorKey.index_tensor(Tensor(key))
    elif isinstance(key, Tensor):
        return o3d.open3d_pybind.TensorKey.index_tensor(key)
    else:
        raise TypeError(f"Invalid key type {type(key)}.")


class Tensor(open3d_pybind.Tensor):
    """
    Open3D Tensor class. A Tensor is a view of data blob with shape, strides
    and etc. Tensor can be used to perform numerical operations.
    """

    def __init__(self, data, dtype=None, device=None):
        if isinstance(data, tuple) or isinstance(data, list):
            data = np.array(data)
        if not isinstance(data, np.ndarray):
            raise ValueError("data must be a list, tuple, or Numpy array.")
        if dtype is None:
            dtype = _numpy_dtype_to_dtype(data.dtype)
        if device is None:
            device = o3d.Device("CPU:0")
        super(Tensor, self).__init__(data, dtype, device)

    @cast_to_py_tensor
    def __getitem__(self, key):
        t = self
        if isinstance(key, tuple):
            o3d_tensor_keys = [_to_o3d_tensor_key(k) for k in key]
            t = super(Tensor, self)._getitem_vector(o3d_tensor_keys)
        elif isinstance(key, (int, slice, list, np.ndarray, Tensor)):
            t = super(Tensor, self)._getitem(_to_o3d_tensor_key(key))
        else:
            raise TypeError(f"Invalid type {type(key)} for getitem.")
        return t

    @cast_to_py_tensor
    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            o3d_tensor_keys = [_to_o3d_tensor_key(k) for k in key]
            super(Tensor, self)._setitem_vector(o3d_tensor_keys, value)
        elif isinstance(key, (int, slice, list, np.ndarray, Tensor)):
            super(Tensor, self)._setitem(_to_o3d_tensor_key(key), value)
        else:
            raise TypeError(f"Invalid type {type(key)} for getitem.")
        return self

    @cast_to_py_tensor
    def cuda(self, device_id=0):
        """
        Returns a copy of this tensor in CUDA memory.

        Args:
            device_id: CUDA device id.
        """
        return super(Tensor, self).cuda(device_id)

    @cast_to_py_tensor
    def cpu(self):
        """
        Returns a copy of this tensor in CPU.

        If the Tensor is already in CPU, then no copy is performed.
        """
        return super(Tensor, self).cpu()

    def numpy(self):
        """
        Returns this tensor as a NumPy array. This tensor must be a CPU tensor,
        and the returned NumPy array shares the same memory as this tensor.
        Changes to the NumPy array will be reflected in the original tensor and
        vice versa.
        """
        return super(Tensor, self).numpy()

    @staticmethod
    @cast_to_py_tensor
    def from_numpy(np_array):
        """
        Returns a Tensor from NumPy array. The resulting tensor is a CPU tensor
        that shares the same memory as the NumPy array. Changes to the tensor
        will be reflected in the original NumPy array and vice versa.

        Args:
            np_array: The Numpy array to be converted from.
        """
        return super(Tensor, Tensor).from_numpy(np_array)

    def to_dlpack(self):
        """
        Returns a DLPack PyCapsule representing this tensor.
        """
        return super(Tensor, self).to_dlpack()

    @staticmethod
    @cast_to_py_tensor
    def from_dlpack(dlpack):
        """
        Returns a tensor converted from DLPack PyCapsule.
        """
        return super(Tensor, Tensor).from_dlpack(dlpack)

    @cast_to_py_tensor
    def add(self, value):
        """
        Adds a tensor and returns the resulting tensor.
        """
        return super(Tensor, self).add(value)

    @cast_to_py_tensor
    def add_(self, value):
        """
        In-place version of Tensor.add
        """
        return super(Tensor, self).add_(value)

    @cast_to_py_tensor
    def sub(self, value):
        """
        Substracts a tensor and returns the resulting tensor.
        """
        return super(Tensor, self).sub(value)

    @cast_to_py_tensor
    def sub_(self, value):
        """
        In-place version of Tensor.sub
        """
        return super(Tensor, self).sub_(value)

    @cast_to_py_tensor
    def mul(self, value):
        """
        Multiplies a tensor and returns the resulting tensor.
        """
        return super(Tensor, self).mul(value)

    @cast_to_py_tensor
    def mul_(self, value):
        """
        In-place version of Tensor.mul
        """
        return super(Tensor, self).mul_(value)

    @cast_to_py_tensor
    def div(self, value):
        """
        Divides a tensor and returns the resulting tensor.
        """
        return super(Tensor, self).div(value)

    @cast_to_py_tensor
    def div_(self, value):
        """
        In-place version of Tensor.div
        """
        return super(Tensor, self).div_(value)

    @cast_to_py_tensor
    def sqrt(self):
        """
        Returns element-wise square root of a tensor.
        """
        return super(Tensor, self).sqrt()

    @cast_to_py_tensor
    def sqrt_(self):
        """
        In-place version of Tensor.sqrt().
        """
        return super(Tensor, self).sqrt_()

    @cast_to_py_tensor
    def sin(self):
        """
        Returns element-wise sin of a tensor.
        """
        return super(Tensor, self).sin()

    @cast_to_py_tensor
    def sin_(self):
        """
        In-place version of Tensor.sin().
        """
        return super(Tensor, self).sin_()

    @cast_to_py_tensor
    def cos(self):
        """
        Returns element-wise cosine of a tensor.
        """
        return super(Tensor, self).cos()

    @cast_to_py_tensor
    def cos_(self):
        """
        In-place version of Tensor.cos().
        """
        return super(Tensor, self).cos_()

    @cast_to_py_tensor
    def neg(self):
        """
        Returns element-wise negation of a tensor.
        """
        return super(Tensor, self).neg()

    @cast_to_py_tensor
    def neg_(self):
        """
        In-place version of Tensor.neg().
        """
        return super(Tensor, self).neg_()

    @cast_to_py_tensor
    def exp(self):
        """
        Returns element-wise base-e exponential of a tensor.
        """
        return super(Tensor, self).exp()

    @cast_to_py_tensor
    def exp_(self):
        """
        In-place version of Tensor.exp().
        """
        return super(Tensor, self).exp_()

    @cast_to_py_tensor
    def abs(self):
        """
        Returns element-wise absolute value of a tensor.
        """
        return super(Tensor, self).abs()

    @cast_to_py_tensor
    def abs_(self):
        """
        In-place version of Tensor.abs().
        """
        return super(Tensor, self).abs_()

    @cast_to_py_tensor
    def to(self, dtype, copy=False):
        """
        Returns a tensor with the specified dtype.

        Args:
            dtype: The targeted dtype to convert to.
            copy: If true, a new tensor is always created; if false, the copy
                  is avoided when the original tensor already have the targeted
                  dtype.
        """
        return super(Tensor, self).to(dtype, copy)

    @cast_to_py_tensor
    def __add__(self, value):
        return self.add(value)

    @cast_to_py_tensor
    def __iadd__(self, value):
        return self.add_(value)

    @cast_to_py_tensor
    def __sub__(self, value):
        return self.sub(value)

    @cast_to_py_tensor
    def __isub__(self, value):
        return self.sub_(value)

    @cast_to_py_tensor
    def __mul__(self, value):
        return self.mul(value)

    @cast_to_py_tensor
    def __imul__(self, value):
        return self.mul_(value)

    @cast_to_py_tensor
    def __truediv__(self, value):
        # True div and floor div are the same for Tensor.
        return self.div(value)

    @cast_to_py_tensor
    def __itruediv__(self, value):
        # True div and floor div are the same for Tensor.
        return self.div_(value)

    @cast_to_py_tensor
    def __floordiv__(self, value):
        # True div and floor div are the same for Tensor.
        return self.div(value)

    @cast_to_py_tensor
    def __ifloordiv__(self, value):
        # True div and floor div are the same for Tensor.
        return self.div_(value)


def cast_to_py_tensorlist(func):
    """
    Args:
        func: function returning a `o3d.open3d_pybind.Tensor`.

    Return:
        A function which returns a python object `o3d.Tensor`.
    """

    def wrapped_func(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        wrapped_result = TensorList([0])
        wrapped_result.shallow_copy_from(result)
        return wrapped_result

    return wrapped_func


class TensorList(open3d_pybind.TensorList):
    """
    Open3D TensorList class. A TensorList is an extendable tensor at the 0-th dimension.
    It is similar to python list, but uses Open3D's tensor memory management system.
    """

    def __init__(self, shape, dtype=None, device=None, size=None):
        if isinstance(shape, list) or isinstance(shape, tuple):
            shape = o3d.SizeVector(shape)
        elif isinstance(shape, o3d.SizeVector):
            pass
        else:
            raise ValueError('shape must be a list, tuple, or o3d.SizeVector')

        if dtype is None:
            dtype = o3d.Dtype.Float32
        if device is None:
            device = o3d.Device("CPU:0")
        if size is None:
            size = 0

        super(TensorList, self).__init__(shape, dtype, device, size)

    @cast_to_py_tensor
    def __getitem__(self, index):
        '''
        \index can be a
        \slice, or \list or \tuple of int: return a TensorList
        \int: return a Tensor
        '''
        if isinstance(index, int):
            return self._getitem(index)
        else:
            raise ValueError('Unsupported index type, only int is supported.')

    def __setitem__(self, index, value):
        '''
        If \index is a single int, \value is a Tensor;
        If \index is a list of ints, \value is correspondingly a TensorList.
        '''
        if isinstance(index, int) and isinstance(value, o3d.Tensor):
            self._setitem(index, value)

        else:
            raise ValueError(
                'Unsupported index type.'
                'Use tensorlist.tensor() to assign value with slices or advanced indexing'
            )

    @cast_to_py_tensorlist
    def __iadd__(self, other):
        return super(TensorList, self).__iadd__(other)

    @cast_to_py_tensorlist
    def __add__(self, other):
        return super(TensorList, self).__add__(other)

    @cast_to_py_tensor
    def tensor(self):
        return super(TensorList, self).tensor()

    @staticmethod
    @cast_to_py_tensorlist
    def concat(tl_a, tl_b):
        return super(TensorList, TensorList).concat(tl_a, tl_b)

    @staticmethod
    @cast_to_py_tensorlist
    def from_tensor(tensor, inplace=False):
        """
        Returns a TensorList from an existing tensor.
        Args:
            tensor: The internal o3d.Tensor to construct from, whose 0-th dimension
                    corresponds to the size of the tensorlist.
            inplace: Reuse tensor memory in place if True, else make a copy.
        """

        if not isinstance(tensor, o3d.Tensor):
            raise ValueError('tensor must be a o3d.Tensor')

        return super(TensorList, TensorList).from_tensor(tensor, inplace)

    @staticmethod
    @cast_to_py_tensorlist
    def from_tensors(tensors, device=None):
        """
        Returns a TensorList from a list of existing tensors.
        Args:
            tensors: The list of o3d.Tensor to construct from.
                     The tensors' shapes should be compatible.
            device: The device where the tensorlist is targeted.
        """

        if not isinstance(tensors, list) and not isinstance(tensors, tuple):
            raise ValueError('tensors must be a list or tuple')

        for tensor in tensors:
            if not isinstance(tensor, o3d.Tensor):
                raise ValueError(
                    'every element of the input list must be a valid tensor')
        if device is None:
            device = o3d.Device("CPU:0")

        return super(TensorList, TensorList).from_tensors(tensors, device)
# global
from hypothesis import given, strategies as st

# local
import numpy as np
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import handle_cmd_line_args


# Helpers #
# ------- #


@st.composite
def statistical_dtype_values(draw, *, function):
    large_abs_safety_factor = 2
    small_abs_safety_factor = 2
    if function in ["mean", "median", "std", "var"]:
        large_abs_safety_factor = 24
        small_abs_safety_factor = 24
    dtype, values, axis = draw(
        helpers.dtype_values_axis(
            available_dtypes=helpers.get_dtypes("float"),
            large_abs_safety_factor=large_abs_safety_factor,
            small_abs_safety_factor=small_abs_safety_factor,
            safety_factor_scale="log",
            min_num_dims=1,
            max_num_dims=5,
            min_dim_size=2,
            valid_axis=True,
            allow_neg_axes=False,
            min_axes_size=1,
        )
    )
    shape = values[0].shape
    size = values[0].size
    max_correction = np.min(shape)
    if function == "var" or function == "std":
        if size == 1:
            correction = 0
        elif isinstance(axis, int):
            correction = draw(
                helpers.ints(min_value=0, max_value=shape[axis] - 1)
                | helpers.floats(min_value=0, max_value=shape[axis] - 1)
            )
            return dtype, values, axis, correction
        else:
            correction = draw(
                helpers.ints(min_value=0, max_value=max_correction - 1)
                | helpers.floats(min_value=0, max_value=max_correction - 1)
            )
        return dtype, values, axis, correction
    return dtype, values, axis


@handle_cmd_line_args
@given(
    dtype_x_axis=statistical_dtype_values(function="median"),
    keep_dims=st.booleans(),
    num_positional_args=helpers.num_positional_args(fn_name="median"),
)
def test_median(
    *,
    dtype_x_axis,
    keep_dims,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
):
    input_dtype, x, axis = dtype_x_axis
    helpers.test_function(
        input_dtypes=input_dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        fw=fw,
        fn_name="median",
        input=x[0],
        axis=axis,
        keepdims=keep_dims,
    )


# nanmean
@handle_cmd_line_args
@given(
    dtype_x_axis=statistical_dtype_values(function="nanmean"),
    keep_dims=st.booleans(),
    dtype=helpers.get_dtypes("float"),
    num_positional_args=helpers.num_positional_args(fn_name="nanmean"),
)
def test_nanmean(
    *,
    dtype_x_axis,
    keep_dims,
    dtype,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
):
    input_dtype, x, axis = dtype_x_axis
    helpers.test_function(
        input_dtypes=input_dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        fw=fw,
        fn_name="nanmean",
        a=x[0],
        axis=axis,
        keepdims=keep_dims,
        dtype=dtype,
    )


# unravel_index
@st.composite
def max_value_as_shape_prod(draw):
    shape = draw(
        helpers.get_shape(
            min_num_dims=1,
            max_num_dims=5,
            min_dim_size=1,
            max_dim_size=5,
        )
    )
    dtype_and_x = draw(
        helpers.dtype_values_axis(
            available_dtypes=helpers.get_dtypes("integer"),
            min_value=0,
            max_value=np.prod(shape) - 1
        )
    )
    return dtype_and_x, shape


@handle_cmd_line_args
@given(
    dtype_x_shape=max_value_as_shape_prod(),
    num_positional_args=helpers.num_positional_args(fn_name="unravel_index"),
)
def test_unravel_index(
    dtype_x_shape,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    container,
    instance_method,
    fw,
):
    dtype_and_x, shape = dtype_x_shape
    input_dtype, x = dtype_and_x[0], dtype_and_x[1]
    helpers.test_function(
        input_dtypes=input_dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        container_flags=container,
        instance_method=instance_method,
        fw=fw,
        fn_name="unravel_index",
        indices=np.asarray(x[0], dtype=input_dtype[0]),
        shape=shape
    )

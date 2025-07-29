from .event_collection import Event

from servicex.func_adl.func_adl_dataset import FuncADLQuery as sxFuncADLQuery


class FuncADLQuery(sxFuncADLQuery[Event]):
    def __init__(self, **kwargs):
        '''Builds a `FuncADLQuery` object to work with 
        datasets. Pass any argument to this function that you would normally
        pass to `FuncADLQuery`.

        Args:
        * `item_type` - The type of this object. Will default to `Event`.

        Note:
        * The current front-end ignores the `codegen` argument.
        '''
        if "item_type" not in kwargs:
            kwargs["item_type"] = Event

        super().__init__(**kwargs)

        # Initialize the code-gen with the default ServiceX code generator.
        self.default_codegen = "atlasr25"


class FuncADLQueryPHYS(sxFuncADLQuery[Event]):
    def __init__(self, **kwargs):
        '''Builds a `FuncADLQuery` object to work with PHYS
        datasets. Pass any argument to this function that you would normally
        pass to `FuncADLQuery`.

        Args:
        * `item_type` - The type of this object. Will default to `Event`.

        Note:
        * The current front-end ignores the `codegen` argument.
        '''
        if "item_type" not in kwargs:
            kwargs["item_type"] = Event

        super().__init__(**kwargs)

        # Initialize the code-gen with the default ServiceX code generator.
        self.default_codegen = "atlasr25"
        # Hack to subvert the replace-in-place.
        from .calibration_support import calib_tools
        ds = calib_tools.query_update(self, calib_tools.default_config("PHYS"))
        self._q_ast = ds._q_ast


class FuncADLQueryPHYSLITE(sxFuncADLQuery[Event]):
    def __init__(self, **kwargs):
        '''Builds a `FuncADLQuery` object to work with PHYSLITE
        datasets. Pass any argument to this function that you would normally
        pass to `FuncADLQuery`.

        Args:
        * `item_type` - The type of this object. Will default to `Event`.

        Note:
        * The current front-end ignores the `codegen` argument.
        '''
        if "item_type" not in kwargs:
            kwargs["item_type"] = Event

        super().__init__(**kwargs)

        # Initialize the code-gen with the default ServiceX code generator.
        self.default_codegen = "atlasr25"
        # Hack to subvert the replace-in-place.
        from .calibration_support import calib_tools
        ds = calib_tools.query_update(self, calib_tools.default_config("PHYSLITE"))
        self._q_ast = ds._q_ast

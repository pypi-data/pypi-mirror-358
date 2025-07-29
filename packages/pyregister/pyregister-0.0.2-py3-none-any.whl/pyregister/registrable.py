"""
` wrapper.common.registrable.Registrable` is a "mixin" for endowing
any base class with a named registry for its subclasses and a decorator
for registering them.
"""
import logging
import inspect
import operator
from collections import defaultdict
import importlib
from typing import (
    TypeVar, Optional, Dict, Tuple, Any,
    ClassVar, DefaultDict, Callable, Type,
    cast, List, Set, Union
)

from .params import Params

logger = logging.getLogger(__name__)

_T = TypeVar("_T")
_RegistrableT = TypeVar("_RegistrableT", bound="Registrable")

_SubclassRegistry = Dict[str, Tuple[type, Optional[str]]]

T = TypeVar("T", bound="Registrable")


class RegisterError(Exception):
    pass


class Registrable:
    r"""
    Any class that inherits from `Registrable` gains access to a named registry for its
    subclasses. To register them, just decorate them with the classmethod
    `@BaseClass.register(name)`.

    After which you can call `BaseClass.list_available()` to get the keys for the
    registered subclasses, and `BaseClass.by_name(name)` to get the corresponding subclass.
    Note that the registry stores the subclasses themselves; not class instances.
    In most cases you would then call `from_params(params)` on the returned subclass.

    You can specify a default by setting `BaseClass.default_implementation`.
    If it is set, it will be the first element of `list_available()`.

    Note that if you use this class to implement a new `Registrable` abstract class,
    you must ensure that all subclasses of the abstract class are loaded when the module is
    loaded, because the subclasses register themselves in their respective files. You can
    achieve this by having the abstract class and all subclasses in the __init__.py of the
    module in which they reside (as this causes any import of either the abstract class or
    a subclass to load all other subclasses and the abstract class).
    """

    _registry: ClassVar[DefaultDict[type, _SubclassRegistry]] = defaultdict(dict)

    default_implementation: Optional[str] = None

    @classmethod
    def register(
        cls, name: str, constructor: Optional[str] = None, exist_ok: bool = False
        ) -> Callable[[Type[_T]], Type[_T]]:
        r"""
        Register a class under a particular name.

        Parameters:
            name(str): The name to register the class under.
            constructor (str, optional): The name of the method to use on the
                class to construct the object.  If this is given, we will use
                this method (which must be a `@classmethod`) instead of the default
                constructor.
                (default = :obj:`None`)
            exist_ok (bool, optional): If True, overwrites any existing models
                registered under `name`. Else, throws an error if a model is already
                registered under `name`.
                (default=`False`)

        Example:

            To use this class, you would typically have a base class that inherits
            from `Registrable`:

            .. code-block:: python

                class Vocabulary(Registrable):
                    ...

        Then, if you want to register a subclass, you decorate it like this:

        .. code-block:: python

            @Vocabulary.register("my-vocabulary")
            class MyVocabulary(Vocabulary):
                def __init__(self, param1: int, param2: str):
                    ...

        Registering a class like this will let you instantiate a class from a config
        file, where you give `"type": "my-vocabulary"`, and keys corresponding to
        the parameters of the `__init__` method (note that for this to work, those
        parameters must have type annotations).

        If you want to have the instantiation from a config file call a method
        other than the constructor, either because you have several different
        construction paths that could be taken for the same object (as we do in
        `Vocabulary`) or because you have logic you want to happen before you
        get to the constructor (as we do in `Embedding`), you can register a
        specific `@classmethod` as the constructor to use, like this:

        .. code-block:: python

            @Vocabulary.register("my-vocabulary-from-instances", constructor="from_instances")
            @Vocabulary.register("my-vocabulary-from-files", constructor="from_files")
            class MyVocabulary(Vocabulary):
                def __init__(self, some_params):
                    ...

                @classmethod
                def from_instances(cls, some_other_params) -> MyVocabulary:
                    ...  # construct some_params from instances
                    return cls(some_params)

                @classmethod
                def from_files(cls, still_other_params) -> MyVocabulary:
                    ...  # construct some_params from files
                    return cls(some_params)

        """
        registry = Registrable._registry[cls]

        def add_subclass_to_registry(subclass: Type[_T]) -> Type[_T]:
            # Add to registry, raise an error if key has already been used.
            if name in registry:
                if exist_ok:
                    message = (
                        f"{name} has already been registered as {registry[name][0].__name__}, but "
                        f"exist_ok=True, so overwriting with {cls.__name__}"
                    )
                    logger.info(message)
                else:
                    message = (
                        f"Cannot register {name} as {cls.__name__}; "
                        f"name already in use for {registry[name][0].__name__}"
                    )
                    raise RegisterError(message)
            registry[name] = (subclass, constructor)
            return subclass

        return add_subclass_to_registry

    @classmethod
    def by_name(cls: Type[_RegistrableT], name: str) -> Callable[..., _RegistrableT]:
        """
        Returns a callable function that constructs an argument of the registered class. Because
        you can register particular functions as constructors for specific names, this isn't
        necessarily the `__init__` method of some class.
        """
        logger.debug(f"instantiating registered subclass {name} of {cls}")
        subclass, constructor = cls.resolve_class_name(name)
        if not constructor:
            return cast(Type[_RegistrableT], subclass)
        else:
            return cast(Callable[..., _RegistrableT], getattr(subclass, constructor))

    @classmethod
    def resolve_class_name(
        cls: Type[_RegistrableT], name: str
    ) -> Tuple[Type[_RegistrableT], Optional[str]]:
        """
        Returns the subclass that corresponds to the given `name`, along with the name of the
        method that was registered as a constructor for that `name`, if any.

        This method also allows `name` to be a fully-specified module name, instead of a name that
        was already added to the `Registry`.  In that case, you cannot use a separate function as
        a constructor (as you need to call `cls.register()` in order to tell us what separate
        function to use).
        """
        if name in Registrable._registry[cls]:
            subclass, constructor = Registrable._registry[cls][name]
            return subclass, constructor
        elif "." in name:
            # This might be a fully qualified class name, so we'll try importing its "module"
            # and finding it there.
            parts = name.split(".")
            submodule = ".".join(parts[:-1])
            class_name = parts[-1]

            try:
                module = importlib.import_module(submodule)
            except ModuleNotFoundError:
                raise RegisterError(
                    f"tried to interpret {name} as a path to a class but unable to import module {submodule}"
                )

            try:
                subclass = getattr(module, class_name)
                constructor = None
                return subclass, constructor
            except AttributeError:
                raise RegisterError(
                    f"tried to interpret {name} as a path to a class "
                    f"but unable to find class {class_name} in {submodule}"
                )

        else:
            # is not a qualified class name
            available = cls.list_available()
            suggestion = _get_suggestion(name, available)
            raise RegisterError(
                (
                    f"'{name}' is not a registered name for '{cls.__name__}'"
                    + (". " if not suggestion else f", did you mean '{suggestion}'? ")
                )
                + "If your registered class comes from custom code, you'll need to import "
                "the corresponding modules. If you're using topolearning from the command-line, "
                "this is done by using the '--include-package' flag, or by specifying your imports "
                "in a '.topoleaning_plugins' file. "
                "Alternatively, you can specify your choices "
                """using fully-qualified paths, e.g. {"model": "my_module.models.MyModel"} """
                "in which case they will be automatically imported correctly."
            )

    @classmethod
    def list_available(cls) -> List[str]:
        """List default first if it exists"""
        keys = list(Registrable._registry[cls].keys())
        default = cls.default_implementation

        if default is None:
            return keys
        elif default not in keys:
            raise RegisterError(f"Default implementation {default} is not registered")
        else:
            return [default] + [k for k in keys if k != default]

    def to_dict(self) -> Dict[str, Any]:
        """
        Default behavior to get a params dictionary from a registrable class
        that does NOT have a `to_dict` implementation.

        Returns:
            parameter_dict (Dict[str, Any]): A minimal parameter dictionary for
                a given registrable class. Will get the registered name and return
                that as well as any positional arguments it can find the value of.
        """

        # Get the list of parent classes in the MRO in order to check where to
        # look for the registered name. Skip the first because that is the
        # current class.
        mro = inspect.getmro(self.__class__)[1:]

        registered_name = None
        for parent in mro:
            # Check if Parent has any registered classes
            try:
                registered_classes = self._registry[parent]
            except KeyError:
                continue

            # Found a dict of (name,(class,constructor)) pairs. Check if the
            # current class is in it.
            for name, registered_value in registered_classes.items():
                registered_class, _ = registered_value
                if registered_class == self.__class__:
                    registered_name = name
                    break

            # Extra break to end the top loop.
            if registered_name is not None:
                break

        if registered_name is None:
            for name,  registered_value in list(self._registry.values())[0].items():
                registered_class, _ = registered_value
                if registered_class == self.__class__:
                    registered_name = name
                    break

        parameter_dict = {"type": registered_name}

        # Get the parameters from the init function.
        for parameter in inspect.signature(self.__class__).parameters.values():
            # Skip non-positional arguments. For simplicity, these are arguments
            # without a default value as those will be required for the
            # `from_params` method.
            if parameter.default != inspect.Parameter.empty:
                logger.debug(f"Skipping parameter {parameter.name}")
                continue

            # Try to get the value of the parameter from the class. Will only
            # try 'name' and '_name'. If it is not there, the parameter is not
            # added to the returned dict.
            if hasattr(self, parameter.name):
                parameter_value = getattr(self, parameter.name)
            elif hasattr(self, f"_{parameter.name}"):
                parameter_value = getattr(self, f"_{parameter.name}")
            else:
                logger.warning(f"Could not find a value for positional argument {parameter.name}")
                continue
            # Try to call `to_dict` method for parameter_value
            try:
                parameter_value = parameter_value.to_dict()
            except Exception:
                pass

            if parameter.kind == parameter.VAR_KEYWORD:
                for key, value in parameter_value.items():
                    # Try to call `to_dict` method for parameter_value
                    try:
                        value = value.to_dict()
                    except Exception:
                        pass
                    parameter_dict[key] = value
            else:
                parameter_dict[parameter.name] = parameter_value

        return parameter_dict

    @classmethod
    def from_params(
        cls: Type[T],
        params: Params,
        constructor_to_call: Callable[..., T] = None,
        constructor_to_inspect: Union[Callable[..., T], Callable[[T], None]] = None,
        **extras,
    ) -> T:
        """
        This is the automatic implementation of `from_params`. Any class that subclasses
        `Registrable` gets this
        implementation for free.  If you want your class to be instantiated from params in the
        "obvious" way -- pop off parameters and hand them to your constructor with the same names --
        this provides that functionality.

        If you need more complex logic in your from `from_params` method, you'll have to implement
        your own method that overrides this one.

        The `constructor_to_call` and `constructor_to_inspect` arguments deal with a bit of
        redirection that we do.  We allow you to register particular `@classmethods` on a class as
        the constructor to use for a registered name.  This lets you, e.g., have a single
        `Vocabulary` class that can be constructed in two different ways, with different names
        registered to each constructor.  In order to handle this, we need to know not just the class
        we're trying to construct (`cls`), but also what method we should inspect to find its
        arguments (`constructor_to_inspect`), and what method to call when we're done constructing
        arguments (`constructor_to_call`).  These two methods are the same when you've used a
        `@classmethod` as your constructor, but they are `different` when you use the default
        constructor (because you inspect `__init__`, but call `cls()`).
        """

        if isinstance(params, str):
            params = Params({"type": params})
        elif isinstance(params, Dict):
            params = Params(params)

        if not isinstance(params, Params):
            raise RegisterError(
                "from_params was passed a `params` object that was not a `Params`. This probably "
                "indicates malformed parameters in a configuration file, where something that "
                "should have been a dictionary was actually a list, or something else. "
                f"This happened when constructing an object of type {cls}."
            )

        registered_subclasses = Registrable._registry.get(cls)

        from .construct_utils import is_base_registrable, create_extras, create_kwargs, assert_empty

        if is_base_registrable(cls) and registered_subclasses is None:
            # NOTE(mattg): There are some potential corner cases in this logic if you have nested
            # Registrable types.  We don't currently have any of those, but if we ever get them,
            # adding some logic to check `constructor_to_call` should solve the issue.  Not
            # bothering to add that unnecessary complexity for now.
            # raise RegisterError(
            #     "Tried to construct an abstract Registrable base class that has no registered "
            #     "concrete types. This might mean that you need to use --include-package to get "
            #     "your concrete classes actually registered."
            # )
            pass

        if registered_subclasses is not None and not constructor_to_call:
            # We know `cls` inherits from Registrable, so we'll use a cast to make mypy happy.

            as_registrable = cast(Type[Registrable], cls)
            default_to_first_choice = as_registrable.default_implementation is not None
            choice = params.pop_choice(
                "type",
                choices=as_registrable.list_available(),
                default_to_first_choice=default_to_first_choice,
            )
            subclass, constructor_name = as_registrable.resolve_class_name(choice)
            # See the docstring for an explanation of what's going on here.
            if not constructor_name:
                constructor_to_inspect = subclass.__init__
                constructor_to_call = subclass  # type: ignore
            else:
                constructor_to_inspect = cast(Callable[..., T], getattr(subclass, constructor_name))
                constructor_to_call = constructor_to_inspect

            if hasattr(subclass, "from_params"):
                # We want to call subclass.from_params.
                extras = create_extras(subclass, extras)
                # mypy can't follow the typing redirection that we do, so we explicitly cast here.
                retyped_subclass = cast(Type[T], subclass)
                return retyped_subclass.from_params(
                    params=params,
                    constructor_to_call=constructor_to_call,
                    constructor_to_inspect=constructor_to_inspect,
                    **extras,
                )
            else:
                # In some rare cases, we get a registered subclass that does _not_ have a
                # from_params method (this happens with Activations, for instance, where we
                # register pytorch modules directly).  This is a bit of a hack to make those work,
                # instead of adding a `from_params` method for them somehow.  We just trust that
                # you've done the right thing in passing your parameters, and nothing else needs to
                # be recursively constructed.
                return subclass(**params)  # type: ignore
        else:
            # This is not a base class, so convert our params and extras into a dict of kwargs.

            # See the docstring for an explanation of what's going on here.
            if not constructor_to_inspect:
                constructor_to_inspect = cls.__init__
            if not constructor_to_call:
                constructor_to_call = cls

            if 'type' in params:
                params.pop('type')

            if constructor_to_inspect == object.__init__:
                # This class does not have an explicit constructor, so don't give it any kwargs.
                # Without this logic, create_kwargs will look at object.__init__ and see that
                # it takes *args and **kwargs and look for those.
                kwargs: Dict[str, Any] = {}
                assert_empty(params, cls.__name__)
            else:
                # This class has a constructor, so create kwargs for it.
                constructor_to_inspect = cast(Callable[..., T], constructor_to_inspect)
                kwargs = create_kwargs(constructor_to_inspect, cls, params, **extras)

            return constructor_to_call(**kwargs)  # type: ignore

    def to_params(self) -> Params:
        """
        Returns a `Params` object that can be used with `.from_params()` to recreate an
        object just like it.

        This relies on `_to_params()`. If you need this in your custom `Registrable` class,
        override `_to_params()`, not this method.
        """

        def replace_object_with_params(o: Any) -> Any:
            if isinstance(o, Registrable):
                return o.to_params()
            elif isinstance(o, List):
                return [replace_object_with_params(i) for i in o]
            elif isinstance(o, Set):
                return {replace_object_with_params(i) for i in o}
            elif isinstance(o, Dict):
                return {key: replace_object_with_params(value) for key, value in o.items()}
            else:
                return o

        return Params(replace_object_with_params(self._to_params()))

    def _to_params(self) -> Dict[str, Any]:
        """
        Default behavior to get a params dictionary from a registrable class
        that does NOT have a _to_params implementation. It is NOT recommended to
        use this method. Rather this method is a minial implementation that
        exists so that calling `_to_params` does not break.

        Returns:
            parameter_dict (Dict[str, Any]): A minimal parameter dictionary for
                a given registrable class. Will get the registered name and return
                that as well as any positional arguments it can find the value of.

        """
        logger.warning(
            f"'{self.__class__.__name__}' does not implement '_to_params`. Will"
            f" use Registrable's `_to_params`."
        )

        return self.to_dict()

# Code from nltk.metrics.distance
def _edit_dist_init(len1, len2):
    lev = []
    for i in range(len1):
        lev.append([0] * len2)  # initialize 2D array to zero
    for i in range(len1):
        lev[i][0] = i  # column 0: 0,1,2,3,4,...
    for j in range(len2):
        lev[0][j] = j  # row 0: 0,1,2,3,4,...
    return lev


def _last_left_t_init(sigma):
    return {c: 0 for c in sigma}


def _edit_dist_step(
    lev, i, j, s1, s2, last_left, last_right, substitution_cost=1, transpositions=False
):
    c1 = s1[i - 1]
    c2 = s2[j - 1]

    # skipping a character in s1
    a = lev[i - 1][j] + 1
    # skipping a character in s2
    b = lev[i][j - 1] + 1
    # substitution
    c = lev[i - 1][j - 1] + (substitution_cost if c1 != c2 else 0)

    # transposition
    d = c + 1  # never picked by default
    if transpositions and last_left > 0 and last_right > 0:
        d = lev[last_left - 1][last_right - 1] + i - last_left + j - last_right - 1

    # pick the cheapest
    lev[i][j] = min(a, b, c, d)

def edit_distance(s1, s2, substitution_cost=1, transpositions=False):
    """
    Calculate the Levenshtein edit-distance between two strings.
    The edit distance is the number of characters that need to be
    substituted, inserted, or deleted, to transform s1 into s2.  For
    example, transforming "rain" to "shine" requires three steps,
    consisting of two substitutions and one insertion:
    "rain" -> "sain" -> "shin" -> "shine".  These operations could have
    been done in other orders, but at least three steps are needed.

    Allows specifying the cost of substitution edits (e.g., "a" -> "b"),
    because sometimes it makes sense to assign greater penalties to
    substitutions.

    This also optionally allows transposition edits (e.g., "ab" -> "ba"),
    though this is disabled by default.

    :param s1, s2: The strings to be analysed
    :param transpositions: Whether to allow transposition edits
    :type s1: str
    :type s2: str
    :type substitution_cost: int
    :type transpositions: bool
    :rtype: int
    """
    # set up a 2-D array
    len1 = len(s1)
    len2 = len(s2)
    lev = _edit_dist_init(len1 + 1, len2 + 1)

    # retrieve alphabet
    sigma = set()
    sigma.update(s1)
    sigma.update(s2)

    # set up table to remember positions of last seen occurrence in s1
    last_left_t = _last_left_t_init(sigma)

    # iterate over the array
    # i and j start from 1 and not 0 to stay close to the wikipedia pseudo-code
    # see https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
    for i in range(1, len1 + 1):
        last_right_buf = 0
        for j in range(1, len2 + 1):
            last_left = last_left_t[s2[j - 1]]
            last_right = last_right_buf
            if s1[i - 1] == s2[j - 1]:
                last_right_buf = j
            _edit_dist_step(
                lev,
                i,
                j,
                s1,
                s2,
                last_left,
                last_right,
                substitution_cost=substitution_cost,
                transpositions=transpositions,
            )
        last_left_t[s1[i - 1]] = i
    return lev[len1][len2]

def _edit_dist_backtrace(lev):
    i, j = len(lev) - 1, len(lev[0]) - 1
    alignment = [(i, j)]

    while (i, j) != (0, 0):
        directions = [
            (i - 1, j),  # skip s1
            (i, j - 1),  # skip s2
            (i - 1, j - 1),  # substitution
        ]

        direction_costs = (
            (lev[i][j] if (i >= 0 and j >= 0) else float("inf"), (i, j))
            for i, j in directions
        )
        _, (i, j) = min(direction_costs, key=operator.itemgetter(0))

        alignment.append((i, j))
    return list(reversed(alignment))

def _get_suggestion(name: str, available: List[str]) -> Optional[str]:
    # First check for simple mistakes like using '-' instead of '_', or vice-versa.
    for ch, repl_ch in (("_", "-"), ("-", "_")):
        suggestion = name.replace(ch, repl_ch)
        if suggestion in available:
            return suggestion

    # If we still haven't found a reasonable suggestion, we return the first suggestion
    # with an edit distance (with transpositions allowed) of 1 to `name`.
    for suggestion in available:
        if edit_distance(name, suggestion, transpositions=True) == 1:
            return suggestion
    return None

import re
import sys
import unittest
import warnings
from collections import namedtuple
from functools import partial
from io import StringIO
from pathlib import Path
from typing import *
from unittest import TextTestRunner, TestResult

try:
    from distutils.core import Command
    from distutils.dist import Distribution
except ImportError:
    from setuptools import Command, Distribution

from setuptools import setup as setuptools_setup, find_packages

if (sys.version_info >= (3, 13)):
    from warnings import deprecated
elif (sys.version_info >= (3, 8)):
    from typing_extensions import deprecated
else:
    def deprecated(msg):
        def wrapper(func):
            def inner(*args, **kwargs):
                warnings.warn(msg, DeprecationWarning, stacklevel=2)
                return func(*args, **kwargs)
            return inner
        return wrapper

if (sys.version_info < (3, 10)):
    from typing.io import *

try:
    from typing import Literal
except ImportError:
    class _LiteralMeta(type):
        __slots__ = tuple()
        def __getitem__(self, item):
            if (not (isinstance(item, tuple))):
                item = (item, )
            return _Literal(*item)
    class _Literal(metaclass=_LiteralMeta):
        __slots__ = ('items', )
        def __init__(self, *items):
            self.items = items
        def __repr__(self) -> str:
            return f"Literal[{','.join(map(repr, self.items))}]"
    Literal = _Literal

_MISSING = object()

try:
    from functools import cached_property
except ImportError:
    from functools import wraps
    def cached_property(prop_func: Callable[[Any], Any]):
        @property
        @wraps(prop_func)
        def wrapper(self):
            cache_dict = getattr(self, '__cached_prop_cache__', _MISSING)
            if (cache_dict is _MISSING):
                cache_dict = dict()
                self.__cached_prop_cache__ = cache_dict
            
            cache = cache_dict.get(prop_func.__name__, _MISSING)
            if (cache is _MISSING):
                result = prop_func(self)
                cache_dict[prop_func.__name__] = result
            else:
                result = cache
            
            return result
        return wrapper

Version = Union[Tuple[int, ...], str]

TestReportFormat = Literal['xml', 'junit', 'html', 'default', 'text']
class ExtendedSetupManager:
    root_module_name: str
    sources_dir: Path
    category: str = 'library'
    test_report_format: TestReportFormat
    _setup_py_file: Path = None
    
    def __init__(self, root_module_name: str, sources_dir: Union[str, Path] = 'src', *, test_report_format: TestReportFormat = 'xml', setup_py_file: Union[str, Path] = None):
        self.root_module_name = root_module_name
        self.sources_dir = Path(sources_dir)
        self.test_report_format = test_report_format
        self._setup_py_file = Path(setup_py_file) if (setup_py_file) else None
    
    def __repr__(self):
        fields = ', '.join(f'{f}={getattr(self, f)!r}' for f in self.__annotations__.keys())
        return f'{type(self).__qualname__}({fields})'
    
    # region Requirements
    def read_requirements_file(self, requirements_file: Path) -> List[str]:
        if not (requirements_file.exists() and requirements_file.is_file()):
            raise FileNotFoundError(f"File {requirements_file} does not exist")
        
        requirements = requirements_file.read_text(encoding='utf-8').splitlines()
        requirements = map(str.strip, requirements)
        requirements = list(requirements)
        return requirements
    
    def read_requirements_files(self, *files: Union[str, Path], default: List[str] = None) -> List[str]:
        for r in map(Path, files):
            try:
                return self.read_requirements_file(r)
            except IOError:
                continue
        else:
            return default or [ ]
    
    @cached_property
    def requirements(self) -> List[str]:
        return self.read_requirements_files('requirements/requirements.txt', 'requirements.txt')
    
    @cached_property
    @deprecated("setup_requirements option is deprecated, use `pyproject.toml`'s `[build-system]` section instead")
    def setup_requirements(self) -> List[str]:
        return self.read_requirements_files('requirements/setup-requirements.txt', 'setup-requirements.txt')
    
    @property
    def default_test_requirements(self) -> List[str]:
        if (self.test_report_format in ('default', 'text')):
            return self.text_test_requirements
        elif (self.test_report_format in ('xml', 'junit')):
            return self.xml_test_requirements
        elif (self.test_report_format == 'html'):
            return self.html_test_requirements
        else:
            raise ValueError(f"Unsupported test report format: {self.test_report_format!r}")

    @property
    def text_test_requirements(self) -> List[str]:
        return [ ]
    
    @property
    def xml_test_requirements(self) -> List[str]:
        return [ 'lxml', 'unittest-xml-reporting' ]
    
    @property
    def html_test_requirements(self) -> List[str]:
        return [ 'html-testRunner' ]
    
    @cached_property
    def test_requirements(self) -> List[str]:
        tests_require = self.read_requirements_files('requirements/test-requirements.txt', 'test-requirements.txt', default=[ 'wheel' ])
        
        base_reqs = set(map(partial(re.compile(r'^([\w\-]+).*$', flags=re.M).sub, r'\1'), tests_require))
        for req in self.default_test_requirements:
            if (req not in base_reqs):
                tests_require.append(req)
        
        return tests_require
    
    @cached_property
    def extra_requirements(self) -> Dict[str, List[str]]:
        extras_require: Dict[str, List[str]] = dict()
        for r in Path('requirements').glob('requirements-*.txt'):
            reqs = self.read_requirements_file(r)
            feature_name = re.match(r'requirements-(.*)\.txt', r.name).group(1).title()
            extras_require[feature_name] = reqs
        extras_require.setdefault('test', self.test_requirements)
        extras_require.setdefault('all', sum(extras_require.values(), list()))
        
        return extras_require
    # endregion
    
    # region Init Script
    @property
    def init_script_file(self) -> TextIO:
        return (self.sources_dir / self.root_module_name / '__init__.py').open('rt', encoding='utf-8')
    
    @cached_property
    def init_script_content(self) -> str:
        with self.init_script_file as f:
            return f.read()
    
    def find_in_init(self, key: str) -> Optional[str]:
        p = re.compile(rf'^__{key}__\s*=\s*(?P<quote>[\'"])(?P<data>.*?(?!(?P=quote)).)?(?P=quote)', re.MULTILINE)
        m = p.search(self.init_script_content)
        return m and m.group('data')
    
    @cached_property
    def name(self) -> str:
        return self.find_in_init('title')
    
    @cached_property
    def author(self) -> str:
        return self.find_in_init('author')
    
    @cached_property
    def raw_version(self) -> str:
        return self.find_in_init('version')
    
    @cached_property
    def version(self) -> str:
        version = self.raw_version
        if (version.endswith(('a', 'b', 'rc'))):
            # append version identifier based on commit count
            try:
                import subprocess
                p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if out:
                    version += out.decode('utf-8').strip()
                p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if out:
                    version += '+g' + out.decode('utf-8').strip()
            except Exception:
                pass
        
        return version

    @cached_property
    def licence(self) -> str:
        return self.find_in_init('license')
    # endregion
    
    # region Descriptions
    @property
    def readme_file(self) -> TextIO:
        for f in self.root_dir.iterdir():
            if (f.suffix.lower() not in { 'md', 'markdown' }): continue
            if (f.stem.lower() != 'readme'): continue
            
            return f.open('rt', encoding='utf-8')
        # noinspection PyTypeChecker
        return StringIO \
(f'''
# Package {self.name}
 - Version: {self.version}
 - ReadMe: **TBD**
''')
    @cached_property
    def readme(self) -> str:
        with self.readme_file as f:
            return f.read()
    
    @cached_property
    def url_prefix(self) -> str:
        return f'https://gitlab.com/Hares-Lab/{self.category}/'
    @cached_property
    def url(self) -> str:
        return self.url_prefix + self.name
    # endregion
    
    # region Tests
    @property
    def tests_directory(self) -> Path:
        return self.root_dir / 'tests'
    
    @property
    def test_output_dir(self) -> Path:
        return self.root_dir / 'reports'
    
    @property
    def test_runner(self) -> TextTestRunner:
        if (self.test_report_format in ('default', 'text')):
            return self.text_test_runner
        elif (self.test_report_format in ('xml', 'junit')):
            return self.xml_test_runner
        elif (self.test_report_format == 'html'):
            return self.html_test_runner
        else:
            raise ValueError(f"Unsupported test report format: {self.test_report_format!r}")
    
    @property
    def text_test_runner(self) -> TextTestRunner:
        return TextTestRunner()
    
    @property
    def xml_test_runner(self) -> TextTestRunner:
        from xmlrunner import XMLTestRunner
        
        test_runner = XMLTestRunner(output=str(self.test_output_dir))
        return test_runner
    
    @property
    def html_test_runner(self) -> TextTestRunner:
        from HtmlTestRunner.runner import HTMLTestRunner
        
        template = self.tests_directory / 'report-template.html'
        if (not template.is_file()): template = None
        test_runner = HTMLTestRunner(template=template, combine_reports=False, output=self.test_output_dir)
        
        return test_runner
    
    def discover_and_run_tests(self, test_runner: TextTestRunner) -> TestResult:
        # get setup.py directory
        test_loader = unittest.defaultTestLoader
        test_suite = test_loader.discover(str(self.root_dir))
        test_result = test_runner.run(test_suite)
        
        return test_result
    
    @property
    def run_tests_command(self):
        def wrapper(_):
            test_runner = self.test_runner
            test_result = self.discover_and_run_tests(test_runner)
            exit(int(not test_result.wasSuccessful()))
        return wrapper
    
    @property
    def TestCommand(self) -> Type[Command]:
        manager = self
        
        class TestCommandClass(Command):
            user_options = list()
            def initialize_options(self): pass
            def finalize_options(self): pass
            run = manager.run_tests_command
        
        return TestCommandClass
    # endregion
    
    # region Dist Utils
    @cached_property
    def setup_file(self) -> Path:
        # PEP-517 initial support
        setup_py = Path('setup.py')
        main_file = Path(sys.modules['__main__'].__file__)
        
        def test_path(p: Optional[Path]) -> bool:
            return (p is not None) and p.exists() and p.is_file()
        
        if (test_path(self._setup_py_file)):
            return self._setup_py_file.absolute()
        elif (main_file.name == setup_py.name and test_path(main_file)):
            return main_file
        elif (test_path(setup_py)):
            return setup_py.absolute()
        else:
            raise RuntimeError("Can't determine the path to the `setup.py` file. Please specify it explicitly via constructor argument")
    
    @cached_property
    def root_dir(self) -> Path:
        return self.setup_file.parent.absolute()
    
    @cached_property
    def packages(self) -> List[str]:
        return find_packages(self.sources_dir)
    
    @cached_property
    def packages_dir(self) -> Dict[str, str]:
        return { '': str(self.sources_dir.absolute().relative_to(self.root_dir)) }
    
    @cached_property
    def commands(self) -> Dict[str, Type[Command]]:
        return dict(test=self.TestCommand)
    # endregion
    
    def make_setup_kwargs\
    (
        self,
        *,
        short_description: str,
        min_python_version: Optional[Version] = _MISSING,
        namespace_packages: List[str] = _MISSING,
        category: str = _MISSING,
        **kwargs,
    ):
        if (category is not _MISSING):
            self.category = category
        
        own_kwargs = dict \
        (
            name = self.name,
            url = self.url,
            author = self.author,
            maintainer = self.author,
            version = self.version,
            license = self.licence,
            packages = self.packages,
            package_dir = self.packages_dir,
            cmdclass = self.commands,
            description = short_description,
            long_description = self.readme,
            long_description_content_type = 'text/markdown',
            include_package_data = True,
            setup_requires = self.setup_requirements,
            install_requires = self.requirements,
            extras_require = self.extra_requirements,
        )
        
        if (isinstance(min_python_version, tuple)):
            min_python_version = '.'.join(map(str, min_python_version))
        if (isinstance(min_python_version, str)):
            own_kwargs['python_requires'] = f'>={min_python_version}'
        if (namespace_packages is not _MISSING):
            own_kwargs['packages'] = list(set(self.packages) - set(namespace_packages))
            own_kwargs['namespace_packages'] = namespace_packages
        
        own_kwargs.update(kwargs)
        
        author_email = kwargs.get('author_email', _MISSING)
        maintainer_email = kwargs.get('maintainer_email', _MISSING)
        if (author_email is _MISSING != maintainer_email is _MISSING and own_kwargs['author'] == own_kwargs['maintainer']):
            if (author_email is _MISSING):
                own_kwargs['author_email'] = own_kwargs['maintainer_email']
            else:
                own_kwargs['maintainer_email'] = own_kwargs['author_email']
        
        return own_kwargs
    
    # region Typing Integration
    @overload
    def setup \
    (
        self,
        *,
        author: str = None,
        author_email: str = None,
        category: str = None,
        classifiers: List[str],
        cmdclass: Dict[str, Type[Command]] = None,
        data_files: List[str] = None,
        dependency_links: List[str] = None,
        description: str = None,
        distclass: Type[Distribution] = None,
        download_url: str = None,
        eager_resources: List[str] = None,
        entry_points: Dict[str, Union[str, List[str]]] = None,
        exclude_package_data: Dict[str, List[str]] = None,
        ext_modules: List[str] = None,
        ext_package: str = None,
        extras_require: List[str] = None,
        include_package_data: bool = True,
        install_requires: List[str] = None,
        keywords: Union[str, List[str]] = None,
        license: str = None,
        license_file: str = None,
        license_files: List[str] = None,
        long_description: str = None,
        long_description_content_type: str = 'text/markdown',
        maintainer: str = None,
        maintainer_email: str = None,
        min_python_version: Version = None,
        name: str = None,
        namespace_packages: List[str] = None,
        obsoletes: List[str] = None,
        options: Dict[str, Any] = None,
        package_data: Dict[str, List[str]] = None,
        package_dir: str = None,
        packages: str = None,
        platforms: List[str] = None,
        project_urls: str = None,
        provides: List[str] = None,
        py_modules: List[str] = None,
        python_requires: str = None,
        requires: List[str] = None,
        script_args: List[str] = None,
        script_name: str = None,
        scripts: List[str] = None,
        setup_requires: List[str] = None,
        short_description: str,
        test_loader: str = None,
        test_suite: str = None,
        tests_require: List[str] = None,
        url: str = None,
        version: str = None,
        zip_safe: bool = None,
        **kwargs,
    ):
        """
        Performs the `setuptools.setup()` action while defining some parameters based on extracted or given information.
        All `setuptools.setup()` parameters are nested by this method, as well as the new ones are introduced:
        
         * `min_python_version`: String or version-tuple defining the minimal required Python version.
         * `category`: A simple name for the package category, such as 'tools', 'libraries', etc. Default: 'libraries'.
         * `short_description`: Same as `description` from `setuptools.setup()`.
        
        Args:
            min_python_version: String or version-tuple defining the minimal required Python version.
            category: A simple name for the package category, such as 'tools', 'libraries', etc. Default: 'libraries'.
            short_description: Same as `description`.
            
            name:
                A string specifying the name of the package.
            
            version:
                A string specifying the version number of the package.
            
            description:
                A string describing the package in a single line.
            
            long_description:
                A string providing a longer description of the package.
            
            long_description_content_type:
                A string specifying the content type is used for the long_description (e.g. text/markdown)
            
            author:
                A string specifying the author of the package.
            
            author_email:
                A string specifying the email address of the package author.
            
            maintainer:
                A string specifying the name of the current maintainer, if different from the author. Note that if the maintainer is provided, setuptools will use it as the author in PKG-INFO.
            
            maintainer_email:
                A string specifying the email address of the current maintainer, if different from the author.
            
            url:
                A string specifying the URL for the package homepage.
            
            download_url:
                A string specifying the URL to download the package.
            
            packages:
                A list of strings specifying the packages that setuptools will manipulate.
            
            py_modules:
                A list of strings specifying the modules that setuptools will manipulate.
            
            scripts:
                A list of strings specifying the standalone script files to be built and installed.
            
            ext_package:
                A string specifying the base package name for the extensions provided by this package.
            
            ext_modules:
                A list of instances of setuptools.Extension providing the list of Python extensions to be built.
            
            classifiers:
                A list of strings describing the categories for the package.
            
            distclass:
                A subclass of Distribution to use.
            
            script_name:
                A string specifying the name of the setup.py script – defaults to sys.argv[0]
            
            script_args:
                A list of strings defining the arguments to supply to the setup script.
            
            options:
                A dictionary providing the default options for the setup script.
            
            license:
                A string specifying the license of the package.
            
            license_file:
                Warning: license_file is deprecated. Use license_files instead.
            
            license_files:
                A list of glob patterns for license related files that should be included. If neither license_file nor license_files is specified, this option defaults to LICEN[CS]E*, COPYING*, NOTICE*, and AUTHORS*.
            
            keywords:
                A list of strings or a comma-separated string providing descriptive meta-data. See: Core Metadata Specifications.
            
            platforms:
                A list of strings or comma-separated string.
            
            cmdclass:
                A dictionary providing a mapping of command names to Command subclasses.
            
            data_files:
                Warning: data_files is deprecated. It does not work with wheels, so it should be avoided.
                A list of strings specifying the data files to install.
            
            package_dir:
                A dictionary that maps package names (as they will be imported by the end-users) into directory paths (that actually exist in the project’s source tree). This configuration has two main purposes:
                
                1. To effectively “rename” paths when building your package. For example, package_dir={"mypkg": "dir1/dir2/code_for_mypkg"} will instruct setuptools to copy the dir1/dir2/code_for_mypkg/... files as mypkg/... when building the final wheel distribution.  
                   Attention: While it is possible to specify arbitrary mappings, developers are STRONGLY ADVISED AGAINST that. They should try as much as possible to keep the directory names and hierarchy identical to the way they will appear in the final wheel, only deviating when absolutely necessary.
                2. To indicate that the relevant code is entirely contained inside a specific directory (instead of directly placed under the project’s root). In this case, a special key is required (the empty string, ""), for example: package_dir={"": "<name of the container directory>"}. All the directories inside the container directory will be copied directly into the final wheel distribution, but the container directory itself will not.
                   This practice is very common in the community to help separate the package implementation from auxiliary files (e.g. CI configuration files), and is referred to as src-layout, because the container directory is commonly named src.
                
                All paths in package_dir must be relative to the project root directory and use a forward slash (/) as path separator regardless of the operating system.
                Tip: When using package discovery together with setup.cfg or pyproject.toml, it is very likely that you don’t need to specify a value for package_dir. Please have a look at the definitions of src-layout and flat-layout to learn common practices on how to design a project’s directory structure and minimise the amount of configuration that is needed.
            
            requires:
                Warning: requires is superseded by install_requires and should not be used anymore.
            
            obsoletes:
                Warning: obsoletes is currently ignored by pip.
                List of strings describing packages which this package renders obsolete, meaning that the two projects should not be installed at the same time.
                Version declarations can be supplied. Version numbers must be in the format specified in Version specifiers (e.g. foo (<3.0)).
                This field may be followed by an environment marker after a semicolon (e.g. foo; os_name == "posix")
                The most common use of this field will be in case a project name changes, e.g. Gorgon 2.3 gets subsumed into Torqued Python 1.0. When you install Torqued Python, the Gorgon distribution should be removed.
            
            provides:
                Warning: provides is currently ignored by pip.
                List of strings describing package- and virtual package names contained within this package.
                A package may provide additional names, e.g. to indicate that multiple projects have been bundled together. For instance, source distributions of the ZODB project have historically included the transaction project, which is now available as a separate distribution. Installing such a source distribution satisfies requirements for both ZODB and transaction.
                A package may also provide a “virtual” project name, which does not correspond to any separately-distributed project: such a name might be used to indicate an abstract capability which could be supplied by one of multiple projects. E.g., multiple projects might supply RDBMS bindings for use by a given ORM: each project might declare that it provides ORM-bindings, allowing other projects to depend only on having at most one of them installed.
                A version declaration may be supplied and must follow the rules described in Version specifiers. The distribution’s version number will be implied if none is specified (e.g. foo (<3.0)).
                Each package may be followed by an environment marker after a semicolon (e.g. foo; os_name == "posix").
            
            include_package_data:
                If set to True, this tells setuptools to automatically include any data files it finds inside your package directories that are specified by your MANIFEST.in file. For more information, see the section on Including Data Files.
            
            exclude_package_data:
                A dictionary mapping package names to lists of glob patterns that should be excluded from your package directories. You can use this to trim back any excess files included by include_package_data. For a complete description and examples, see the section on Including Data Files.
            
            package_data:
                A dictionary mapping package names to lists of glob patterns. For a complete description and examples, see the section on Including Data Files. You do not need to use this option if you are using include_package_data, unless you need to add e.g. files that are generated by your setup script and build process. (And are therefore not in source control or are files that you don’t want to include in your source distribution.)
            
            zip_safe:
                A boolean (True or False) flag specifying whether the project can be safely installed and run from a zip file. If this argument is not supplied, the bdist_egg command will have to analyze all of your project’s contents for possible problems each time it builds an egg.
            
            install_requires:
                A string or list of strings specifying what other distributions need to be installed when this one is. See the section on Declaring required dependency for details and examples of the format of this argument.
            
            entry_points:
                A dictionary mapping entry point group names to strings or lists of strings defining the entry points. Entry points are used to support dynamic discovery of services or plugins provided by a project. See Advertising Behavior for details and examples of the format of this argument. In addition, this keyword is used to support Automatic Script Creation.
            
            extras_require:
                A dictionary mapping names of “extras” (optional features of your project) to strings or lists of strings specifying what other distributions must be installed to support those features. See the section on Declaring required dependency for details and examples of the format of this argument.
            
            python_requires:
                A string corresponding to a version specifier (as defined in PEP 440) for the Python version, used to specify the Requires-Python defined in PEP 345.
            
            setup_requires:
                Warning: Using setup_requires is discouraged in favor of PEP 518.
                A string or list of strings specifying what other distributions need to be present in order for the setup script to run. setuptools will attempt to obtain these before processing the rest of the setup script or commands. This argument is needed if you are using distutils extensions as part of your build process; for example, extensions that process setup() arguments and turn them into EGG-INFO metadata files.
            
                (Note: projects listed in setup_requires will NOT be automatically installed on the system where the setup script is being run. They are simply downloaded to the ./.eggs directory if they’re not locally available already. If you want them to be installed, as well as being available when the setup script is run, you should add them to install_requires and setup_requires.)
            
            dependency_links:
                Warning: dependency_links is deprecated. It is not supported anymore by pip.
                A list of strings naming URLs to be searched when satisfying dependencies. These links will be used if needed to install packages specified by setup_requires or tests_require. They will also be written into the egg’s metadata for use during install by tools that support them.
            
            namespace_packages:
                Warning: The namespace_packages implementation relies on pkg_resources. However, pkg_resources has some undesirable behaviours, and Setuptools intends to obviate its usage in the future. Therefore, namespace_packages was deprecated in favor of native/implicit namespaces (PEP 420). Check the Python Packaging User Guide for more information.
                A list of strings naming the project’s “namespace packages”. A namespace package is a package that may be split across multiple project distributions. For example, Zope 3’s zope package is a namespace package, because subpackages like zope.interface and zope.publisher may be distributed separately. The egg runtime system can automatically merge such subpackages into a single parent package at runtime, as long as you declare them in each project that contains any subpackages of the namespace package, and as long as the namespace package’s __init__.py does not contain any code other than a namespace declaration. See the section on Finding namespace packages for more information.
            
            test_suite:
                A string naming a unittest.TestCase subclass (or a package or module containing one or more of them, or a method of such a subclass), or naming a function that can be called with no arguments and returns a unittest.TestSuite. If the named suite is a module, and the module has an additional_tests() function, it is called and the results are added to the tests to be run. If the named suite is a package, any submodules and subpackages are recursively added to the overall test suite.
                Specifying this argument enables use of the test command to run the specified test suite, e.g. via setup.py test. See the section on the test command below for more details.
            
                Warning: Deprecated since version 41.5.0: The test command will be removed in a future version of setuptools, alongside any test configuration parameter.
            
            tests_require:
                If your project’s tests need one or more additional packages besides those needed to install it, you can use this option to specify them. It should be a string or list of strings specifying what other distributions need to be present for the package’s tests to run. When you run the test command, setuptools will attempt to obtain these. Note that these required projects will not be installed on the system where the tests are run, but only downloaded to the project’s setup directory if they’re not already installed locally.
            
                Warning: Deprecated since version 41.5.0: The test command will be removed in a future version of setuptools, alongside any test configuration parameter.
            
            test_loader:
                If you would like to use a different way of finding tests to run than what setuptools normally uses, you can specify a module name and class name in this argument. The named class must be instantiable with no arguments, and its instances must support the loadTestsFromNames() method as defined in the Python unittest module’s TestLoader class. Setuptools will pass only one test “name” in the names argument: the value supplied for the test_suite argument. The loader you specify may interpret this string in any way it likes, as there are no restrictions on what may be contained in a test_suite string.
                The module name and class name must be separated by a :. The default value of this argument is "setuptools.command.test:ScanningLoader". If you want to use the default unittest behavior, you can specify "unittest:TestLoader" as your test_loader argument instead. This will prevent automatic scanning of submodules and subpackages.
                The module and class you specify here may be contained in another package, as long as you use the tests_require option to ensure that the package containing the loader class is available when the test command is run.
                
                Warning: Deprecated since version 41.5.0: The test command will be removed in a future version of setuptools, alongside any test configuration parameter.
            
            eager_resources:
                A list of strings naming resources that should be extracted together, if any of them is needed, or if any C extensions included in the project are imported. This argument is only useful if the project will be installed as a zipfile, and there is a need to have all of the listed resources be extracted to the filesystem as a unit. Resources listed here should be ‘/’-separated paths, relative to the source root, so to list a resource foo.png in package bar.baz, you would include the string bar/baz/foo.png in this argument.
                If you only need to obtain resources one at a time, or you don’t have any C extensions that access other files in the project (such as data files or shared libraries), you probably do NOT need this argument and shouldn’t mess with it. For more details on how this argument works, see the section below on Automatic Resource Extraction.
            
            project_urls:
                An arbitrary map of URL names to hyperlinks, allowing more extensible documentation of where various resources can be found than the simple url and download_url options provide.
        
        """
    # endregion
    def setup(self, **kwargs):
        return setuptools_setup(**self.make_setup_kwargs(**kwargs))


class SingleScriptModuleSetup(ExtendedSetupManager):
    script_name: str
    
    def __init__(self, script_name: str):
        super(SingleScriptModuleSetup, self).__init__(script_name, '.')
        self.script_name = script_name
    
    @property
    def init_script_file(self) -> TextIO:
        return open(f'{self.script_name}.py', 'rt', encoding='utf-8')
    
    def make_setup_kwargs(self, **kwargs):
        result = super().make_setup_kwargs(**kwargs)
        result.pop('packages', None)
        result.pop('package_dir', None)
        result.setdefault('py_modules', [ self.script_name ])
        return result


__title__ = 'extended-setup-tools'
__author__ = 'Peter Zaitcev / USSX Hares'
__license__ = 'BSD 2-clause'
__copyright__ = 'Copyright 2021-2025 Peter Zaitcev'
__version__ = '0.2.3'

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(*__version__.split('.'), releaselevel='beta', serial=0)


__all__ = \
[
    'version_info',
    '__title__',
    '__author__',
    '__license__',
    '__copyright__',
    '__version__',
    
    'ExtendedSetupManager',
    'SingleScriptModuleSetup',
]


"""
# The following fields are still missing:
# - author_email = None     | These are half-supported.
# - maintainer = None       | These are half-supported. Same as Author
# - maintainer_email = None | These are half-supported. Author email and Maintainer email are synchronized if Author and Maintainer are the same person
# - download_url = None
# - keywords = None
# - license_files = [ 'LICENSE' ]
# - obsoletes = None
# - platforms = None
# - project_urls = {}
# - provides = None
# - provides_extras = OrderedSet()
# - requires = None
"""

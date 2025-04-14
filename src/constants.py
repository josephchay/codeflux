DEFAULT_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv",
                        "node_modules", "dist", "build", ".next", "codeflux.egg-info",
                        "codeflux"]

PYTHON_EXTENSIONS = [".py"]
PYTHON_EXCLUDE_EXTENSIONS = [".pyc", ".pyo", "__init__.py"]
PYTHON_EXCLUDE_FILENAMES = ["setup.py", "conftest.py"]

NOTEBOOK_EXTENSIONS = [".ipynb"]
NOTEBOOK_EXCLUDE_EXTENSIONS = [".nbconvert.ipynb"]
NOTEBOOK_EXCLUDE_FILENAMES = ["Untitled.ipynb"]

JSTS_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]
JSTS_EXCLUDE_EXTENSIONS = ["d.ts", ".test.js", ".test.ts", ".spec.js", ".spec.ts", ".min.js"]
JSTS_EXCLUDE_FILENAMES = ["babel.config.js", "jest.config.js", "webpack.config.js"]

MDTXT_EXTENSIONS = [".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn", ".mdtxt", ".mdtext", ".txt"]
MDTXT_EXCLUDE_EXTENSIONS = []
MDTXT_EXCLUDE_FILENAMES = ["LICENSE.md", "LICENSE.txt", "CONTRIBUTING.md", "CONTRIBUTING.txt", "CODE_OF_CONDUCT.md",
                           "CODE_OF_CONDUCT.txt", "CHANGELOG.md", "CHANGELOG.txt"]

YML_EXTENSIONS = [".yaml", ".yml"]
YML_EXCLUDE_EXTENSIONS = []
YML_EXCLUDE_FILENAMES = ["docker-compose.yaml", "docker-compose.yml", "circleci.yml"]

SHELL_EXTENSIONS = [".sh", ".bash", ".zsh"]
SHELL_EXCLUDE_EXTENSIONS = []
SHELL_EXCLUDE_FILENAMES = ["setup.sh", "install.sh", "bootstrap.sh"]

JSON_EXTENSIONS = [".json", ".jsonl", ".geojson", ".json5", ".ndjson"]
JSON_EXCLUDE_EXTENSIONS = []
JSON_EXCLUDE_FILENAMES = ["package-lock.json", "yarn.lock.json", "composer.lock", "poetry.lock"]

GO_EXTENSIONS = [".go", ".mod", ".sum", ".pb.go", ".tmpl", ".tpl"]
GO_EXCLUDE_EXTENSIONS = [".pb.go"]
GO_EXCLUDE_FILENAMES = ["main_test.go"]

INI_EXTENSIONS = [".ini", ".cfg", ".conf", ".properties"]
INI_EXCLUDE_EXTENSIONS = [".sample", ".default"]
INI_EXCLUDE_FILENAMES = ["setup.ini", "config.ini", "environment.ini", "application.properties", "database.properties",
                         "log4j.properties", "system.cfg", "local.conf", "global.conf", "defaults.ini", "template.ini"]

DB_EXTENSIONS = [".sql", ".ddl", ".dml"]
DB_EXCLUDE_EXTENSIONS = []
DB_EXCLUDE_FILENAMES = ["schema.sql", "init.sql", "migration.sql", "seed.sql"]

BAT_EXTENSIONS = [".bat", ".cmd", ".btm"]
BAT_EXCLUDE_EXTENSIONS = []
BAT_EXCLUDE_FILENAMES = ["setup.bat", "install.cmd", "system_init.bat"]

SCP_EXTENSIONS = [".scp", ".script"]
SCP_EXCLUDE_EXTENSIONS = []
SCP_EXCLUDE_FILENAMES = ["main.scp", "config.script", "setup.script"]

HTML_EXTENSIONS = [".html", ".htm", ".xhtml", ".shtml"]
HTML_EXCLUDE_EXTENSIONS = []
HTML_EXCLUDE_FILENAMES = ["index.html", "404.html", "500.html"]

CSS_EXTENSIONS = [".css", ".scss", ".sass", ".less"]
CSS_EXCLUDE_EXTENSIONS = [".min.css"]
CSS_EXCLUDE_FILENAMES = ["normalize.css", "reset.css", "bootstrap.css"]

PHP_EXTENSIONS = [".php", ".phtml", ".php5", ".php7", ".phps"]
PHP_EXCLUDE_EXTENSIONS = []
PHP_EXCLUDE_FILENAMES = ["index.php", "wp-config.php", "functions.php"]

RUBY_EXTENSIONS = [".rb", ".rake", ".gemspec", ".erb"]
RUBY_EXCLUDE_EXTENSIONS = []
RUBY_EXCLUDE_FILENAMES = ["Gemfile", "Rakefile", "config.ru"]

SWIFT_EXTENSIONS = [".swift"]
SWIFT_EXCLUDE_EXTENSIONS = []
SWIFT_EXCLUDE_FILENAMES = ["AppDelegate.swift", "SceneDelegate.swift"]

KOTLIN_EXTENSIONS = [".kt", ".kts"]
KOTLIN_EXCLUDE_EXTENSIONS = []
KOTLIN_EXCLUDE_FILENAMES = ["MainActivity.kt", "Application.kt"]

JAVA_EXTENSIONS = [".java", ".class", ".jar"]
JAVA_EXCLUDE_EXTENSIONS = [".class", ".jar"]
JAVA_EXCLUDE_FILENAMES = ["MainActivity.java", "Application.java"]

CSHARP_EXTENSIONS = [".cs", ".cshtml", ".csx"]
CSHARP_EXCLUDE_EXTENSIONS = []
CSHARP_EXCLUDE_FILENAMES = ["Program.cs", "Startup.cs"]

NOEXT_EXTENSIONS = [""]  # This will match files with no extension
NOEXT_EXCLUDE_EXTENSIONS = []
NOEXT_EXCLUDE_FILENAMES = ["README", "LICENSE", "NOTICE", "CHANGELOG", "TODO"]

POWERSHELL_EXTENSIONS = [".ps1", ".psm1", ".psd1", ".ps1xml"]
POWERSHELL_EXCLUDE_EXTENSIONS = []
POWERSHELL_EXCLUDE_FILENAMES = ["profile.ps1", "Microsoft.PowerShell_profile.ps1"]

DOCKER_EXTENSIONS = [".dockerfile", ".dockerignore"]
DOCKER_EXCLUDE_EXTENSIONS = []
DOCKER_EXCLUDE_FILENAMES = ["Dockerfile"]  # Dockerfile has no extension but is a special case

XML_EXTENSIONS = [".xml", ".xsd", ".xsl", ".xslt", ".wsdl", ".svg", ".pom"]
XML_EXCLUDE_EXTENSIONS = []
XML_EXCLUDE_FILENAMES = ["pom.xml", "web.xml", "applicationContext.xml"]

R_EXTENSIONS = [".r", ".rmd", ".rds", ".rdata", ".rda"]
R_EXCLUDE_EXTENSIONS = []
R_EXCLUDE_FILENAMES = ["install.r", "setup.r"]

CPP_EXTENSIONS = [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx", ".hh"]
CPP_EXCLUDE_EXTENSIONS = []
CPP_EXCLUDE_FILENAMES = ["main.c", "main.cpp", "stdafx.h"]

RUST_EXTENSIONS = [".rs", ".rlib"]
RUST_EXCLUDE_EXTENSIONS = []
RUST_EXCLUDE_FILENAMES = ["main.rs", "lib.rs"]

SCALA_EXTENSIONS = [".scala", ".sc"]
SCALA_EXCLUDE_EXTENSIONS = []
SCALA_EXCLUDE_FILENAMES = ["build.sbt"]

PERL_EXTENSIONS = [".pl", ".pm", ".t"]
PERL_EXCLUDE_EXTENSIONS = []
PERL_EXCLUDE_FILENAMES = ["Makefile.PL", "Build.PL"]

LUA_EXTENSIONS = [".lua"]
LUA_EXCLUDE_EXTENSIONS = []
LUA_EXCLUDE_FILENAMES = ["init.lua", "config.lua"]

GROOVY_EXTENSIONS = [".groovy", ".gvy", ".gy", ".gsh"]
GROOVY_EXCLUDE_EXTENSIONS = []
GROOVY_EXCLUDE_FILENAMES = ["Jenkinsfile", "build.gradle"]

HASKELL_EXTENSIONS = [".hs", ".lhs"]
HASKELL_EXCLUDE_EXTENSIONS = []
HASKELL_EXCLUDE_FILENAMES = ["Setup.hs"]

ERLANG_EXTENSIONS = [".erl", ".hrl", ".ex", ".exs"]
ERLANG_EXCLUDE_EXTENSIONS = []
ERLANG_EXCLUDE_FILENAMES = ["mix.exs"]

LATEX_EXTENSIONS = [".tex", ".sty", ".cls", ".bib", ".bst", ".dtx", ".ltx", ".ins"]
LATEX_EXCLUDE_EXTENSIONS = [r"\.aux\d*", r"\.log\d*", r"\.lof\d*", r"\.lot\d*", r"\.maf\d*", r"\.mlf\d*",
                            r"\.mlt\d*", r"\.mtc\d*", r"\.out\d*", r"\.synctex\.gz\d*", r"\.toc\d*", r"\.blg\d*"]
LATEX_EXCLUDE_FILENAMES = ["elsarticle.cls", "acmart.cls", "IEEEtran.cls", "llncs.cls", "spconf.sty", "beamer.cls"]

ALL_EXTENSIONS = (
    PYTHON_EXTENSIONS + NOTEBOOK_EXTENSIONS + JSTS_EXTENSIONS +
    MDTXT_EXTENSIONS + YML_EXTENSIONS + SHELL_EXTENSIONS +
    JSON_EXTENSIONS + GO_EXTENSIONS + INI_EXTENSIONS + DB_EXTENSIONS +
    BAT_EXTENSIONS + SCP_EXTENSIONS + HTML_EXTENSIONS + CSS_EXTENSIONS +
    PHP_EXTENSIONS + RUBY_EXTENSIONS + SWIFT_EXTENSIONS + KOTLIN_EXTENSIONS +
    JAVA_EXTENSIONS + CSHARP_EXTENSIONS + NOEXT_EXTENSIONS + POWERSHELL_EXTENSIONS +
    DOCKER_EXTENSIONS + XML_EXTENSIONS + R_EXTENSIONS + CPP_EXTENSIONS +
    RUST_EXTENSIONS + SCALA_EXTENSIONS + PERL_EXTENSIONS + LUA_EXTENSIONS +
    GROOVY_EXTENSIONS + HASKELL_EXTENSIONS + ERLANG_EXTENSIONS + LATEX_EXTENSIONS
)

ALL_EXCLUDE_EXTENSIONS = (
    PYTHON_EXCLUDE_EXTENSIONS + NOTEBOOK_EXCLUDE_EXTENSIONS +
    JSTS_EXCLUDE_EXTENSIONS + MDTXT_EXCLUDE_EXTENSIONS +
    YML_EXCLUDE_EXTENSIONS + SHELL_EXCLUDE_EXTENSIONS +
    JSON_EXCLUDE_EXTENSIONS + GO_EXCLUDE_EXTENSIONS + INI_EXCLUDE_EXTENSIONS +
    DB_EXCLUDE_EXTENSIONS + BAT_EXCLUDE_EXTENSIONS + SCP_EXCLUDE_EXTENSIONS +
    HTML_EXCLUDE_EXTENSIONS + CSS_EXCLUDE_EXTENSIONS + PHP_EXCLUDE_EXTENSIONS +
    RUBY_EXCLUDE_EXTENSIONS + SWIFT_EXCLUDE_EXTENSIONS + KOTLIN_EXCLUDE_EXTENSIONS +
    JAVA_EXCLUDE_EXTENSIONS + CSHARP_EXCLUDE_EXTENSIONS + NOEXT_EXCLUDE_EXTENSIONS +
    POWERSHELL_EXCLUDE_EXTENSIONS + DOCKER_EXCLUDE_EXTENSIONS + XML_EXCLUDE_EXTENSIONS +
    R_EXCLUDE_EXTENSIONS + CPP_EXCLUDE_EXTENSIONS + RUST_EXCLUDE_EXTENSIONS +
    SCALA_EXCLUDE_EXTENSIONS + PERL_EXCLUDE_EXTENSIONS + LUA_EXCLUDE_EXTENSIONS +
    GROOVY_EXCLUDE_EXTENSIONS + HASKELL_EXCLUDE_EXTENSIONS + ERLANG_EXCLUDE_EXTENSIONS +
    LATEX_EXCLUDE_EXTENSIONS
)

ALL_EXCLUDE_FILENAMES = (
    PYTHON_EXCLUDE_FILENAMES + NOTEBOOK_EXCLUDE_FILENAMES +
    JSTS_EXCLUDE_FILENAMES + MDTXT_EXCLUDE_FILENAMES +
    YML_EXCLUDE_FILENAMES + SHELL_EXCLUDE_FILENAMES +
    JSON_EXCLUDE_FILENAMES + GO_EXCLUDE_FILENAMES + INI_EXCLUDE_FILENAMES +
    DB_EXCLUDE_FILENAMES + BAT_EXCLUDE_FILENAMES + SCP_EXCLUDE_FILENAMES +
    HTML_EXCLUDE_FILENAMES + CSS_EXCLUDE_FILENAMES + PHP_EXCLUDE_FILENAMES +
    RUBY_EXCLUDE_FILENAMES + SWIFT_EXCLUDE_FILENAMES + KOTLIN_EXCLUDE_FILENAMES +
    JAVA_EXCLUDE_FILENAMES + CSHARP_EXCLUDE_FILENAMES + NOEXT_EXCLUDE_FILENAMES +
    POWERSHELL_EXCLUDE_FILENAMES + DOCKER_EXCLUDE_FILENAMES + XML_EXCLUDE_FILENAMES +
    R_EXCLUDE_FILENAMES + CPP_EXCLUDE_FILENAMES + RUST_EXCLUDE_FILENAMES +
    SCALA_EXCLUDE_FILENAMES + PERL_EXCLUDE_FILENAMES + LUA_EXCLUDE_FILENAMES +
    GROOVY_EXCLUDE_FILENAMES + HASKELL_EXCLUDE_FILENAMES + ERLANG_EXCLUDE_FILENAMES +
    LATEX_EXCLUDE_FILENAMES
)

ROOT_TREE_UI_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv", "codeflux", "node_modules",
                              "codeflux.egg-info"]

DEFAULT_FLATTEN_OUTPUT_PATH = "flattened"
DEFAULT_DEFLATTEN_OUTPUT_PATH = "deflattened"
DEFAULT_MINIFY_OUTPUT_PATH = "minified"
DEFAULT_BUNDLE_OUTPUT_PATH = "bundled.txt"
DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH = "minified_bundle.txt"
DEFAULT_TREE_OUTPUT_PATH = "source_directory_tree.txt"
DEFAULT_ROOT_TREE_OUTPUT_PATH = "root_directory_tree.txt"
DEFAULT_SUMMARY_OUTPUT_PATH = "summary.txt"

OPERATION_FLATTEN = "flatten"
OPERATION_DEFLATTEN = "deflatten"
OPERATION_MINIFY = "minify"
OPERATION_BUNDLE = "bundle"
OPERATION_MINIFY_BUNDLE = "minify_bundle"
OPERATION_SEARCH = "search"
OPERATION_PROPERTIES = "properties"
OPERATION_TREE = "tree"
OPERATION_ROOT_TREE = "root_tree"

TABULATE_FORMAT = "grid"
MINIFICATION_DESCRIPTION = "python-minifier (Python); terser (JS/TS); html-minifier (HTML); csso (CSS); php-minifier (PHP)"

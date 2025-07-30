use std::fmt::Display;

use pyo3::{prelude::*, types::PyTuple};
use ruff_python_ast::{Decorator, Expr, StmtFunctionDef};

mod extractor;
mod manager;
pub mod python;

pub use extractor::FixtureExtractor;
pub use manager::FixtureManager;

#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub enum FixtureScope {
    #[default]
    Function,
    Module,
    Package,
    Session,
}

impl TryFrom<String> for FixtureScope {
    type Error = String;

    fn try_from(s: String) -> Result<Self, Self::Error> {
        match s.as_str() {
            "module" => Ok(Self::Module),
            "session" => Ok(Self::Session),
            "package" => Ok(Self::Package),
            "function" => Ok(Self::Function),
            _ => Err(format!("Invalid fixture scope: {s}")),
        }
    }
}

impl Display for FixtureScope {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Module => write!(f, "module"),
            Self::Session => write!(f, "session"),
            Self::Package => write!(f, "package"),
            Self::Function => write!(f, "function"),
        }
    }
}

pub struct Fixture {
    name: String,
    function_def: StmtFunctionDef,
    scope: FixtureScope,
    function: Py<PyAny>,
}

impl Fixture {
    #[must_use]
    pub const fn new(
        name: String,
        function_def: StmtFunctionDef,
        scope: FixtureScope,
        function: Py<PyAny>,
    ) -> Self {
        Self {
            name,
            function_def,
            scope,
            function,
        }
    }

    #[must_use]
    pub fn name(&self) -> &str {
        &self.name
    }

    #[must_use]
    pub const fn scope(&self) -> &FixtureScope {
        &self.scope
    }

    pub fn call<'a>(
        &self,
        py: Python<'a>,
        required_fixtures: Vec<Bound<'a, PyAny>>,
    ) -> PyResult<Bound<'a, PyAny>> {
        let args = PyTuple::new(py, required_fixtures)?;
        let function_return = self.function.call(py, args, None);
        function_return.map(|r| r.into_bound(py))
    }
}

impl HasFunctionDefinition for Fixture {
    fn function_definition(&self) -> &StmtFunctionDef {
        &self.function_def
    }
}

impl std::fmt::Debug for Fixture {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Fixture(name: {}, scope: {})", self.name, self.scope)
    }
}

pub trait HasFunctionDefinition {
    #[must_use]
    fn get_required_fixture_names(&self) -> Vec<String> {
        let mut required_fixtures = Vec::new();
        for parameter in self
            .function_definition()
            .parameters
            .iter_non_variadic_params()
        {
            required_fixtures.push(parameter.parameter.name.as_str().to_string());
        }
        required_fixtures
    }

    fn function_definition(&self) -> &StmtFunctionDef;
}

pub trait RequiresFixtures: std::fmt::Debug {
    #[must_use]
    fn uses_fixture(&self, fixture_name: &str) -> bool {
        self.required_fixtures().contains(&fixture_name.to_string())
    }

    #[must_use]
    fn required_fixtures(&self) -> Vec<String>;
}

impl<T: HasFunctionDefinition + std::fmt::Debug> RequiresFixtures for T {
    fn required_fixtures(&self) -> Vec<String> {
        self.get_required_fixture_names()
    }
}

pub fn is_fixture_function(val: &StmtFunctionDef) -> bool {
    val.decorator_list.iter().any(is_fixture)
}

fn is_fixture(decorator: &Decorator) -> bool {
    match &decorator.expression {
        Expr::Name(name) => name.id == "fixture",
        Expr::Attribute(attr) => attr.attr.id == "fixture",
        Expr::Call(call) => match call.func.as_ref() {
            Expr::Name(name) => name.id == "fixture",
            Expr::Attribute(attr) => attr.attr.id == "fixture",
            _ => false,
        },
        _ => false,
    }
}

/// This trait is used to get all fixtures (from a module or package) used that have a given scope.
///
/// For example, if we are in a test module, we want to get all fixtures used in the test module.
/// If we are in a package, we want to get all fixtures used in the package from the configuration module.
pub trait HasFixtures<'proj>: std::fmt::Debug {
    fn fixtures<'a: 'proj>(
        &'a self,
        scope: &[FixtureScope],
        test_cases: &[&dyn RequiresFixtures],
    ) -> Vec<&'proj Fixture> {
        let mut graph = Vec::new();
        for fixture in self.all_fixtures(test_cases) {
            if scope.contains(fixture.scope()) {
                graph.push(fixture);
            }
        }
        graph
    }

    fn get_fixture<'a: 'proj>(&'a self, fixture_name: &str) -> Option<&'proj Fixture> {
        self.all_fixtures(&[])
            .into_iter()
            .find(|fixture| fixture.name() == fixture_name)
    }

    fn all_fixtures<'a: 'proj>(
        &'a self,
        test_cases: &[&dyn RequiresFixtures],
    ) -> Vec<&'proj Fixture>;
}

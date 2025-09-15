import pytest
import sys
import os
from types import SimpleNamespace


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ..utils.string_formater import StringFormater


# --------------------------
# String Formater tests
# --------------------------
@pytest.fixture
def sf():
    return StringFormater()


def test_remove_trailing_comma(sf):
    """
    Test removeTrailingComma method.
    Ensure trailing commas are correctly removed from strings.
    """
    assert sf.removeTrailingComma("test,") == "test"
    assert sf.removeTrailingComma("test") == "test"
    assert sf.removeTrailingComma("test,,") == "test"
    assert sf.removeTrailingComma("test, with, commas,") == "test, with, commas"
    assert sf.removeTrailingComma("") == ""


def test_addEqueToBGET(sf):
    """
    Ensure it correctly formats expressions for BGET.
    Checks that it adds '== 1' to BGET expressions and leaves others unchanged.
    """
    assert sf.addEqueToBGET("BGET(x)") == "BGET(x) == 1"
    assert sf.addEqueToBGET("BGET(x,y)") == "BGET(x,y) == 1"
    assert sf.addEqueToBGET("text") == "text"
    assert sf.addEqueToBGET("") == ""


def test_replaceValueParametrsCalls(sf):
    """
    Test replaceValueParametrsCalls method.
    Replace parameter identifiers with their corresponding values.
    """
    param_array = SimpleNamespace(
        elements=[
            SimpleNamespace(identifier="foo", value=42),
            SimpleNamespace(identifier="bar", value=7),
        ]
    )
    assert sf.replaceValueParametrsCalls(param_array, "foo + bar") == "42 + 7"
    assert sf.replaceValueParametrsCalls(param_array, "z + bar") == "z + 7"
    assert sf.replaceValueParametrsCalls(param_array, "foo + y") == "42 + y"
    assert sf.replaceValueParametrsCalls(param_array, "") == ""


def test_addSpacesAroundOperators(sf):
    """
    Test addSpacesAroundOperators method.
    Checks that spaces are added around common operators.
    """
    assert sf.addSpacesAroundOperators("a+b") == "a + b"
    assert sf.addSpacesAroundOperators("a+b*c==d") == "a + b * c == d"
    assert sf.addSpacesAroundOperators("a>=b") == "a >= b"
    assert sf.addSpacesAroundOperators("") == ""


def test_valuesToAplanStandart(sf):
    """
    Test valuesToAplanStandart method.
    Checks that it converts various value formats.
    """
    assert sf.valuesToAplanStandart("4'b1010") == "10"  # binary
    assert sf.valuesToAplanStandart("2'hf") == "15"  # hex
    assert sf.valuesToAplanStandart("'123") == "123"  # decimal


def test_addBracketsAfterNegation(sf):
    """
    Test addBracketsAfterNegation method.
    Ensure it adds brackets around expressions after negation.
    """
    assert sf.addBracketsAfterNegation("!x") == "!(x)"
    assert sf.addBracketsAfterNegation("y && !z") == "y && !(z)"
    assert sf.addBracketsAfterNegation("!!c") == "!(!c)"
    assert sf.addBracketsAfterNegation("") == ""


def test_addLeftValueForUnaryOrOperator(sf):
    """
    Test addLeftValueForUnaryOrOperator method.
    Ensure it adds left-hand value for unary "|" operator.
    """
    assert sf.addLeftValueForUnaryOrOperator("out = |x") == "out = out|x"
    assert sf.addLeftValueForUnaryOrOperator("out = x|b") == "out = x|b"
    assert sf.addLeftValueForUnaryOrOperator("out = |y|z") == "out = out|y|z"


def test_addBracketsAfterTilda(sf):
    """
    Test addBracketsAfterTilda method.
    Ensure it adds brackets around expressions after tilde (~).
    """
    assert sf.addBracketsAfterTilda("~x") == "~(x)"
    assert sf.addBracketsAfterTilda("a + ~b") == "a + ~(b)"
    assert sf.addBracketsAfterNegation("") == ""


def test_parallelAssignment2Assignment(sf):
    """
    Test parallelAssignment2Assignment method.
    Ensure it replaces the "<=" operator with "=" .
    """
    assert sf.parallelAssignment2Assignment("a <= 1") == "a = 1"


def test_doubleOperators2Aplan(sf):
    """
    Test doubleOperators2Aplan method.
    Ensure it converts double operators like "++" and "--" to their corresponding assignment operations.
    """
    assert sf.doubleOperators2Aplan("x++") == "x = x + 1"
    assert sf.doubleOperators2Aplan("x--") == "x = x - 1"
    assert sf.doubleOperators2Aplan("c++; d--") == "c = c + 1; d = d - 1"
    assert sf.addBracketsAfterNegation("") == ""


def test_notConcreteIndex2AplanStandart_with_dimension(sf):
    """
    Test notConcreteIndex2AplanStandart method when a declaration with dimension exists.
    The method should replace array-style indexing `foo.bar[i]`
    with function-style syntax `foo.bar(i)`.
    """
    mock_decl = SimpleNamespace()
    mock_decl.findDeclWithDimentionByName = lambda name: object()
    mock_design_unit = SimpleNamespace(declarations=mock_decl)
    expr = "foo.bar[i]"
    assert sf.notConcreteIndex2AplanStandart(expr, mock_design_unit) == "foo.bar(i)"


def test_notConcreteIndex2AplanStandart_without_dimension(sf):
    """
    Test notConcreteIndex2AplanStandart method when no declaration with dimension exists.
    The method should replace array-style indexing `foo.bar[i]`
    with a call to `BGET(foo.bar, i)`.
    """
    mock_decl = SimpleNamespace()
    mock_decl.findDeclWithDimentionByName = lambda name: None
    mock_design_unit = SimpleNamespace(declarations=mock_decl)
    expr = "foo.bar[i]"
    assert (
        sf.notConcreteIndex2AplanStandart(expr, mock_design_unit) == "BGET(foo.bar, i)"
    )


def test_vectorSizes2AplanStandart_single(sf):
    """
    Test vectorSizes2AplanStandart method for single index.
    Ensure it converts vector sizes expressions to a standard format like `signal[7]` to `signal(7)`.
    """
    assert sf.vectorSizes2AplanStandart("signal[7]") == "signal(7)"
    assert sf.vectorSizes2AplanStandart("signal[4:0]") == "signal(0,4)"
    assert sf.vectorSizes2AplanStandart("") == ""


def test_generatePythonStyleTernary(sf):
    """
    Test generatePythonStyleTernary method.
    Ensure it converts ternary operator into Python-style conditional expression.
    """
    assert sf.generatePythonStyleTernary("(x > 0) ? 1 : 0") == "(1 if x > 0 else 0)"
    assert sf.generatePythonStyleTernary("(x)?y:z") == "(y if x else z)"
    # Should remain unchanged if no ternary match
    assert sf.generatePythonStyleTernary("a + b") == "a + b"
    assert sf.generatePythonStyleTernary("") == ""


def test_replace_cpp_operators(sf):
    """
    Test replace_cpp_operators method.
    Ensure it replaces C++ operators with Python equivalents.
    """
    expr = "a && b || !c / d ++ true false"
    out = sf.replace_cpp_operators(expr)

    # Check replacements individually
    assert "and" in out
    assert "or" in out
    assert "not" in out
    assert "//" in out
    assert "+= 1" in out
    assert "True" in out
    assert "False" in out
    assert sf.replace_cpp_operators("x / y") == "x // y"
    assert sf.replace_cpp_operators("true && false") == "True and False"
    assert sf.replace_cpp_operators("x++") == "x += 1"

    assert sf.replace_cpp_operators("x&&y||!z") == "x and y or not z"
    assert sf.replace_cpp_operators("") == ""

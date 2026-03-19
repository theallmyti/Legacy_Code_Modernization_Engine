import pytest
from lcm_engine.core.parser import LegacyParser
from lcm_engine.core.chunker import SemanticChunker

def test_parser_divisions():
    parser = LegacyParser()
    code = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO.
       DATA DIVISION.
       PROCEDURE DIVISION.
    """
    result = parser.parse(code)
    assert len(result["ast"]["divisions"]) == 3
    assert "IDENTIFICATION" in result["ast"]["divisions"]
    assert "PROCEDURE" in result["ast"]["divisions"]

def test_parser_computations():
    parser = LegacyParser()
    code = """
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           COMPUTE WS-TOTAL = WS-AMT + WS-TAX
    """
    result = parser.parse(code)
    assert len(result["ast"]["computations"]) == 1
    assert result["ast"]["computations"][0] == "WS-TOTAL = WS-AMT + WS-TAX"
    assert "MAIN-LOGIC" in result["ast"]["paragraphs"]

def test_chunker():
    parser = LegacyParser()
    chunker = SemanticChunker(parser)
    code = """
       DATA DIVISION.
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           COMPUTE X = Y + Z
       END-LOGIC.
           STOP RUN.
    """
    chunks = chunker.chunk(code)
    assert len(chunks) == 3 # globals, MAIN-LOGIC, END-LOGIC
    assert chunks[1]["name"] == "MAIN-LOGIC"
    assert "COMPUTE X = Y + Z" in chunks[1]["content"]

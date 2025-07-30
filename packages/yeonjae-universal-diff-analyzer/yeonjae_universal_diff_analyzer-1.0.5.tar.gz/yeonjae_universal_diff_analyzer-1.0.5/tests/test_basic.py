"""
Universal Diff Analyzer 기본 테스트

모듈의 기본 임포트와 구조를 테스트합니다.
"""

import pytest


def test_models_import():
    """모델 임포트 테스트"""
    from yeonjae_universal_diff_analyzer.models import (
        ChangeType, FileType, DiffLine, FileChange, 
        DiffAnalysis, CodeComplexity, AnalysisResult
    )
    
    # 열거형 값 확인
    assert ChangeType.ADDED.value == "added"
    assert ChangeType.MODIFIED.value == "modified"
    assert ChangeType.DELETED.value == "deleted"
    assert FileType.PYTHON.value == "python"
    assert FileType.JAVASCRIPT.value == "javascript"


def test_exceptions_import():
    """예외 클래스 임포트 테스트"""
    from yeonjae_universal_diff_analyzer.exceptions import (
        DiffAnalyzerException,
        InvalidDiffFormatException,
        AnalysisException
    )
    
    # 예외 클래스 확인
    assert issubclass(InvalidDiffFormatException, DiffAnalyzerException)
    assert issubclass(AnalysisException, DiffAnalyzerException)


def test_diff_line_creation():
    """DiffLine 생성 테스트"""
    from yeonjae_universal_diff_analyzer.models import DiffLine
    
    line = DiffLine(
        line_number=10,
        content="print('hello world')",
        change_type="added"
    )
    
    assert line.line_number == 10
    assert line.content == "print('hello world')"
    assert line.change_type == "added"


def test_file_change_creation():
    """FileChange 생성 테스트"""
    from yeonjae_universal_diff_analyzer.models import FileChange, ChangeType, FileType
    
    change = FileChange(
        file_path="src/main.py",
        filename="main.py",  # 필수 필드 추가
        status="modified",   # 필수 필드 추가
        change_type=ChangeType.MODIFIED,
        file_type=FileType.PYTHON,
        additions=5,
        deletions=2
    )
    
    assert change.file_path == "src/main.py"
    assert change.change_type == ChangeType.MODIFIED
    assert change.file_type == FileType.PYTHON
    assert change.additions == 5
    assert change.deletions == 2


def test_code_complexity_creation():
    """CodeComplexity 생성 테스트"""
    from yeonjae_universal_diff_analyzer.models import CodeComplexity
    
    complexity = CodeComplexity(
        cyclomatic_complexity=5,
        cognitive_complexity=8,
        lines_of_code=100,
        maintainability_index=75.5
    )
    
    assert complexity.cyclomatic_complexity == 5
    assert complexity.cognitive_complexity == 8
    assert complexity.lines_of_code == 100
    assert complexity.maintainability_index == 75.5


def test_analysis_result_creation():
    """AnalysisResult 생성 테스트"""
    from yeonjae_universal_diff_analyzer.models import AnalysisResult, CodeComplexity
    
    complexity = CodeComplexity(
        cyclomatic_complexity=5,
        cognitive_complexity=8,
        lines_of_code=100,
        maintainability_index=75.5
    )
    
    result = AnalysisResult(
        file_path="src/main.py",  # 필수 필드 추가
        language="python",        # 필수 필드 추가
        complexity=complexity,    # 필수 필드 추가
        lines_analyzed=100,
        analysis_time=0.5
    )
    
    assert result.file_path == "src/main.py"
    assert result.language == "python"
    assert result.complexity == complexity
    assert result.lines_analyzed == 100
    assert result.analysis_time == 0.5


def test_exception_creation():
    """예외 생성 테스트"""
    from yeonjae_universal_diff_analyzer.exceptions import InvalidDiffFormatException
    
    exception = InvalidDiffFormatException("Invalid diff header", "@@invalid@@")
    
    assert "Invalid diff header" in str(exception)
    assert exception.details["reason"] == "Invalid diff header"
    assert exception.details["diff_content"] == "@@invalid@@" 
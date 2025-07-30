"""
Universal Diff Analyzer 예외 클래스

Diff 분석과 관련된 예외들을 정의합니다.
"""

from typing import Dict, Any, Optional


class DiffAnalyzerException(Exception):
    """Diff 분석 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


# Legacy alias for backward compatibility
class DiffAnalyzerError(DiffAnalyzerException):
    """Diff 분석 관련 기본 예외 클래스 (legacy alias)"""
    pass


class InvalidDiffFormatException(DiffAnalyzerException):
    """잘못된 Diff 형식 예외"""
    
    def __init__(self, reason: str, diff_content: str):
        message = f"Invalid diff format: {reason}"
        details = {
            "reason": reason,
            "diff_content": diff_content
        }
        super().__init__(message, details)


class AnalysisException(DiffAnalyzerException):
    """분석 작업 예외"""
    
    def __init__(self, analysis_type: str, original_error: Exception):
        message = f"Analysis failed for type '{analysis_type}'"
        details = {
            "analysis_type": analysis_type,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class ComplexityCalculationException(DiffAnalyzerException):
    """복잡도 계산 예외"""
    
    def __init__(self, file_path: str, original_error: Exception):
        message = f"Complexity calculation failed for file: {file_path}"
        details = {
            "file_path": file_path,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class FileTypeDetectionException(DiffAnalyzerException):
    """파일 타입 감지 예외"""
    
    def __init__(self, file_path: str, reason: str):
        message = f"File type detection failed for '{file_path}': {reason}"
        details = {
            "file_path": file_path,
            "reason": reason
        }
        super().__init__(message, details)


class RiskAssessmentException(DiffAnalyzerException):
    """위험도 평가 예외"""
    
    def __init__(self, commit_hash: str, original_error: Exception):
        message = f"Risk assessment failed for commit: {commit_hash}"
        details = {
            "commit_hash": commit_hash,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class LanguageNotSupportedError(DiffAnalyzerException):
    """지원하지 않는 언어 예외"""
    
    def __init__(self, language: str, file_path: str):
        message = f"Language '{language}' is not supported for file: {file_path}"
        details = {
            "language": language,
            "file_path": file_path
        }
        super().__init__(message, details)


class ComplexityAnalysisError(DiffAnalyzerException):
    """복잡도 분석 예외"""
    
    def __init__(self, file_path: str, reason: str):
        message = f"Complexity analysis failed for file '{file_path}': {reason}"
        details = {
            "file_path": file_path,
            "reason": reason
        }
        super().__init__(message, details)


class StructuralAnalysisError(DiffAnalyzerException):
    """구조 분석 예외"""
    
    def __init__(self, file_path: str, reason: str):
        message = f"Structural analysis failed for file '{file_path}': {reason}"
        details = {
            "file_path": file_path,
            "reason": reason
        }
        super().__init__(message, details)


class ASTParsingError(DiffAnalyzerException):
    """AST 파싱 예외"""
    
    def __init__(self, file_path: str, original_error: Exception):
        message = f"AST parsing failed for file: {file_path}"
        details = {
            "file_path": file_path,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class BinaryFileAnalysisError(DiffAnalyzerException):
    """바이너리 파일 분석 예외"""
    
    def __init__(self, file_path: str):
        message = f"Cannot analyze binary file: {file_path}"
        details = {
            "file_path": file_path,
            "reason": "Binary files are not supported for analysis"
        }
        super().__init__(message, details)


class LargeFileAnalysisError(DiffAnalyzerException):
    """대용량 파일 분석 예외"""
    
    def __init__(self, file_path: str, file_size: int, max_size: int):
        message = f"File too large for analysis: {file_path} ({file_size} bytes, max: {max_size} bytes)"
        details = {
            "file_path": file_path,
            "file_size": file_size,
            "max_size": max_size
        }
        super().__init__(message, details) 
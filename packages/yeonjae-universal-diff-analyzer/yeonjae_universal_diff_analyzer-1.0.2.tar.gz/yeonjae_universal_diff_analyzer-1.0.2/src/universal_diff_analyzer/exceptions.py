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
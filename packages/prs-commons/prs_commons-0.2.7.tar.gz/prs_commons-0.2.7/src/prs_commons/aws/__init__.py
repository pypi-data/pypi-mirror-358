"""
AWS integration module for PRS Commons.

This module provides AWS service clients and utilities for interacting with
various AWS services like S3, SQS, SNS, etc.
"""

from .s3_client import S3Client

__all__ = ["S3Client"]

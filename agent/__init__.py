"""
GigShield AI Agents Module

This module contains ONLY AI agents powered by SpoonOS and LLMs.
For infrastructure services, see /services
"""
from .paralegal import analyze_job_request
from .eye import verify_work

__all__ = ['analyze_job_request', 'verify_work']


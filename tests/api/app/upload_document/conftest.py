"""
Consolidated Fixtures for upload_document testing.

This module provides all fixtures needed for testing the upload_document method
in a single, de-duplicated file. All fixtures use the centralized Factory
and constants to eliminate code duplication across the test suite.
"""
import datetime
from typing import Dict, Any
import tempfile
import os
import time


import pytest
from freezegun import freeze_time


from ._utilities import TestDataFactory as Factory
from ._constants import (
    BAD_INPUT_TYPES,
    CID_PATTERN,
    CONCURRENCY_LEVELS,
    DEFAULT_CONFIG_VALUES,
    ERROR_CODES,
    ERROR_RESPONSE_FIELDS,
    FILE_SIZE_LIMITS,
    FILE_SIZE_PATTERN,
    FILENAME_PATTERNS,
    HTTP_STATUS_CODES,
    ISO_TIMESTAMP_PATTERN,
    MIME_TYPES,
    RESPONSE_FIELD_TYPES,
    RESPONSE_VALIDATION_RULES,
    SUCCESS_RESPONSE_FIELDS,
    SUPPORTED_FILE_TYPES,
    TEST_DATA_SIZES,
    TEXT_CONTENT_SAMPLES,
    TIMING_CONSTANTS,
    UNSUPPORTED_FILE_TYPES,
    VALID_STATUS_VALUES,
)


# ============================================================================
# File Content Fixtures - All file types handled by Factory
# ============================================================================

@pytest.fixture
def filename_patterns():
    """A dictionary of filename patterns for various test scenarios."""
    return FILENAME_PATTERNS.copy()

@pytest.fixture
def valid_file_contents():
    """A dictionary of valid file contents for all supported types."""
    return {
        'pdf': Factory.create_file_content(
            'pdf',
            text_content=TEXT_CONTENT_SAMPLES['multiline'],
            size='medium'
        ),
        'docx': Factory.create_file_content(
            'docx',
            text_content=TEXT_CONTENT_SAMPLES['multiline'],
            size='medium'
        ),
        'doc': Factory.create_file_content(
            'doc',
            text_content=TEXT_CONTENT_SAMPLES['multiline'],
            size='medium'
        ),
        'txt': Factory.create_file_content(
            'txt',
            text_content=TEXT_CONTENT_SAMPLES['basic'],
            size='small'
        )
    }


@pytest.fixture
def edge_case_file_contents():
    """A dictionary of file contents for various edge case scenarios."""
    return {
        'empty': Factory.create_file_content('empty'),
        'oversized_pdf': Factory.create_file_content('pdf', size='oversized'),
        'corrupted_pdf': Factory.create_file_content(
            'pdf',
            text_content=TEXT_CONTENT_SAMPLES['basic'],
            corruption='header'
        ),
        'unsupported_jpg': Factory.create_file_content('jpg')
    }


@pytest.fixture
def filename_edge_case_files():
    """A dictionary of files with edge case filenames."""
    return {
        'unicode': {
            'content': Factory.create_file_content(
                'txt',
                text_content=TEXT_CONTENT_SAMPLES['unicode']
            ),
            'filename': "测试文档_ñáéíóú_файл.txt"
        },
        'special_chars': {
            'content': Factory.create_file_content(
                'txt',
                text_content=TEXT_CONTENT_SAMPLES['basic']
            ),
            'filename': "test file & document (copy) [1] - final.txt"
        }
    }


# ============================================================================
# UploadFile Mock Fixtures - All use Factory
# ============================================================================

@pytest.fixture
def mock_upload_files(valid_file_contents, edge_case_file_contents, filename_edge_case_files):
    """A dictionary of mock UploadFile objects for various test scenarios."""
    files = {}

    # Create mocks for valid file types
    for file_type, content in valid_file_contents.items():
        ext = f".{file_type}"
        files[file_type] = Factory.create_mock('upload_file', {
            'content': content,
            'filename': f'test_document.{file_type}',
            'content_type': MIME_TYPES[ext],
            'size': len(content)
        })

    # Create mocks for edge case file contents
    files['empty'] = Factory.create_mock('upload_file', {
        'content': edge_case_file_contents['empty'],
        'filename': 'empty_file.txt',
        'content_type': MIME_TYPES['.txt'],
        'size': 0
    })
    files['oversized'] = Factory.create_mock('upload_file', {
        'content': edge_case_file_contents['oversized_pdf'],
        'filename': 'huge_file.pdf',
        'content_type': MIME_TYPES['.pdf'],
        'size': len(edge_case_file_contents['oversized_pdf'])
    })
    files['corrupted'] = Factory.create_mock('upload_file', {
        'content': edge_case_file_contents['corrupted_pdf'],
        'filename': 'corrupted_document.pdf',
        'content_type': MIME_TYPES['.pdf'],
        'size': len(edge_case_file_contents['corrupted_pdf'])
    })
    files['unsupported'] = Factory.create_mock('upload_file', {
        'content': edge_case_file_contents['unsupported_jpg'],
        'filename': 'image.jpg',
        'content_type': MIME_TYPES['.jpg'],
        'size': len(edge_case_file_contents['unsupported_jpg'])
    })

    # Create mocks for filename edge cases
    for name, data in filename_edge_case_files.items():
        content = data['content']
        filename = data['filename']
        ext = f".{filename.split('.')[-1]}"
        files[f'{name}_name'] = Factory.create_mock('upload_file', {
            'content': content,
            'filename': filename,
            'content_type': MIME_TYPES.get(ext, 'application/octet-stream'),
            'size': len(content)
        })

    return files


# ============================================================================
# Client and Session Fixtures - All use Factory
# ============================================================================

@pytest.fixture
def client_cid_test_cases():
    """Dictionary containing various client CID test cases."""
    return {
        'valid': Factory.make_cid("test_client_session_001"),
        'invalid': Factory.make_cid(invalid=True, format_type='malformed'),
        'none': None,
        'multiple': [Factory.make_cid(f"client_session_{i:03d}") for i in range(1, 6)],
        'concurrent': [Factory.make_cid(f"concurrent_session_{i}")for i in range(10)]
    }


@pytest.fixture
def client_cid_variations():
    """Dictionary containing various client CID test cases."""
    return {
        'valid': Factory.make_cid("valid_test_client"),
        'invalid': Factory.make_cid(invalid=True, format_type='malformed'),
        'none': None,
        'empty_string': "",
        'too_short': Factory.make_cid(invalid=True, format_type='short'),
        'too_long': Factory.make_cid(invalid=True, format_type='long'),
        'wrong_prefix': Factory.make_cid(invalid=True, format_type='wrong_prefix'),
        'non_string': 12345,
        'unicode': Factory.make_cid(invalid=True, format_type='unicode'),
        'with_spaces': Factory.make_cid(invalid=True, format_type='with_spaces'),
        'special_chars': Factory.make_cid(invalid=True, format_type='special_chars')
    }


# ============================================================================
# Database and Mock Fixtures - All use Factory
# ============================================================================


@pytest.fixture
def mock_parameters():
    """A dictionary of mock parameters for testing."""
    return {
        'database': Factory.create_mock('database'),
        'configs': Factory.create_mock('configs', DEFAULT_CONFIG_VALUES),
        'resources': Factory.create_mock('resources')
    }



@pytest.fixture
def mock_database_failures():
    """A dictionary of mock databases that simulate various failure conditions."""
    return {
        'generic': Factory.create_mock('database', should_fail=True, failure_type='generic'),
        'connection': Factory.create_mock('database', should_fail=True, failure_type='connection'),
        'constraint': Factory.create_mock('database', should_fail=True, failure_type='constraint'),
        'timeout': Factory.create_mock('database', should_fail=True, failure_type='timeout')
    }


@pytest.fixture
def mock_resources_with_db_failure():
    """Mock resources dictionary with failing database."""
    return Factory.create_mock('resources', {
        'database': {'should_fail': True}
    })


@pytest.fixture
def mock_app_instance(mock_configs, mock_resources):
    """A mock App instance with mocked dependencies."""
    return Factory.create_mock('app', {
        'configs': mock_configs,
        'resources': mock_resources
    })


@pytest.fixture
def mock_app_with_db_failure(mock_configs, mock_resources_with_db_failure):
    """A mock App instance with failing database dependencies."""
    return Factory.create_mock('app', {
        'configs': mock_configs,
        'resources': mock_resources_with_db_failure
    }, should_fail=True, failure_type='database')


# ============================================================================
# Response and Validation Fixtures - All use constants and Factory
# ============================================================================

@pytest.fixture
def expected_response_fields():
    """Dictionary of required fields for success and error responses."""
    return {
        'success': list(SUCCESS_RESPONSE_FIELDS),
        'error': list(ERROR_RESPONSE_FIELDS)
    }


@pytest.fixture
def test_patterns():
    """Dictionary of regex patterns for validation."""
    return {
        'cid': CID_PATTERN,
        'iso_timestamp': ISO_TIMESTAMP_PATTERN,
        'file_size': FILE_SIZE_PATTERN
    }


@pytest.fixture
def validation_sets():
    """Dictionary of sets for validation purposes."""
    return {
        'valid_status_values': VALID_STATUS_VALUES.copy(),
        'valid_error_codes': set(ERROR_CODES.values())
    }


@pytest.fixture
def sample_responses():
    """A dictionary of sample success and error responses."""
    return {
        'success': Factory.create_response('success', {
            'cid': Factory.make_cid("sample_success"),
            'filename': 'test_document.pdf',
            'file_size': FILE_SIZE_LIMITS['medium_file']
        }),
        'error': Factory.create_response(
            'error',
            {'message': 'Upload failed: Invalid file type'},
            error_code=ERROR_CODES['INVALID_FILE_TYPE']
        )
    }


@pytest.fixture
def response_field_types():
    """Expected types for response fields."""
    return RESPONSE_FIELD_TYPES.copy()


@pytest.fixture
def response_validation_rules():
    """Validation rules for response fields."""
    return RESPONSE_VALIDATION_RULES.copy()


# ============================================================================
# Content and Text Fixtures - All use constants
# ============================================================================

@pytest.fixture
def text_content():
    """Dictionary of various text content samples for testing."""
    return {
        'known': TEXT_CONTENT_SAMPLES['multiline'],
        'unicode': TEXT_CONTENT_SAMPLES['unicode'],
        'large': TEXT_CONTENT_SAMPLES['large'],
        'minimal': TEXT_CONTENT_SAMPLES['minimal'],
        'empty': TEXT_CONTENT_SAMPLES['empty'],
        'whitespace': TEXT_CONTENT_SAMPLES['whitespace'],
        'legal': TEXT_CONTENT_SAMPLES['legal']
    }


@pytest.fixture
def pdf_with_known_text(known_text_content):
    """PDF file containing specific known text for extraction testing."""
    pdf_content = Factory.create_file_content('pdf', text_content=known_text_content)
    return pdf_content, known_text_content


@pytest.fixture
def docx_with_unicode_text(unicode_text_content):
    """DOCX file containing Unicode text for extraction testing."""
    docx_content = Factory.create_file_content('docx', text_content=unicode_text_content)
    return docx_content, unicode_text_content


@pytest.fixture
def txt_with_legal_content(legal_document_sample):
    """TXT file containing legal document sample."""
    txt_content = Factory.create_file_content('txt', text_content=legal_document_sample)
    return txt_content, legal_document_sample


@pytest.fixture
def files_with_identical_content(known_text_content):
    """Multiple files with identical content for CID consistency testing."""
    files = Factory.create_multiple_files(
        count=4,
        file_type='pdf',
        identical_content=True,
        base_filename='identical_document'
    )
    # Add expected text for each file
    return [(content, filename, known_text_content) for content, filename in files]


@pytest.fixture
def content_extraction_test_cases():
    """Various content types for comprehensive extraction testing."""
    test_cases = {}
    for content_type, text_content in TEXT_CONTENT_SAMPLES.items():
        if content_type != 'large':  # Skip large for this fixture
            content = Factory.create_file_content('txt', text_content=text_content)
            test_cases[content_type] = (content, text_content)
    return test_cases


@pytest.fixture
def text_processing_edge_cases():
    """Edge cases for text processing validation."""
    return {
        "null_bytes": b"Content with \x00 null bytes",
        "mixed_encoding": "Mixed encoding: café".encode('utf-8') + b'\xff\xfe',
        "very_long_line": ("A" * 10000).encode('utf-8'),
        "control_characters": "Content with \t tabs \r carriage returns \n newlines".encode('utf-8'),
        "binary_content": Factory.create_file_content('jpg'),
        "partial_utf8": b'\xc3\xa9\xc3',  # Incomplete UTF-8 sequence
    }


@pytest.fixture
def expected_content_lengths():
    """Expected content lengths for validation testing."""
    return {
        content_type: len(text_content)
        for content_type, text_content in TEXT_CONTENT_SAMPLES.items()
        if content_type != 'large'
    }


# ============================================================================
# Error Simulation Fixtures - All use Factory
# ============================================================================

@pytest.fixture
def error_simulations():
    """A dictionary of mocks that simulate various error conditions."""
    type_ = "error"
    return {
        'io': Factory.create_mock(type_, failure_type='io_error'),
        'value': Factory.create_mock(type_, failure_type='value_error'),
        'type': Factory.create_mock(type_, failure_type='type_error'),
        'http_400': Factory.create_mock(type_, failure_type='http_400'),
        'http_413': Factory.create_mock(type_, failure_type='http_413'),
        'http_415': Factory.create_mock(type_, failure_type='http_415'),
        'http_500': Factory.create_mock(type_, failure_type='http_500'),
    }


@pytest.fixture
def file_read_error_simulation():
    """Simulates file read errors during upload processing."""
    return Factory.create_mock('upload_file', should_fail=True, failure_type='read_error')


@pytest.fixture
def content_extraction_error_simulation():
    """Simulates content extraction failures for various file types."""
    return {
        file_type.strip('.'): Factory.create_mock('error', failure_type='value_error')
        for file_type in SUPPORTED_FILE_TYPES
    }


@pytest.fixture
def cid_generation_error_simulation():
    """Simulates CID generation failures."""
    return Factory.create_mock('error', failure_type='value_error')


@pytest.fixture
def database_error_simulations():
    """Simulates various database error conditions."""
    return {
        'connection_error': Factory.create_mock('database', should_fail=True, failure_type='connection'),
        'timeout_error': Factory.create_mock('database', should_fail=True, failure_type='timeout'),
        'constraint_error': Factory.create_mock('database', should_fail=True, failure_type='constraint'),
        'permission_error': Factory.create_mock('error', failure_type='permission_error'),
        'disk_full_error': Factory.create_mock('error', failure_type='io_error')
    }

@pytest.fixture
def processing_error_simulations():
    """A dictionary of mocks that simulate various processing-related errors."""
    return {
        'network': Factory.create_mock('error', failure_type='network_error'),
        'memory': Factory.create_mock('error', failure_type='memory_error'),
        'permission': Factory.create_mock('error', failure_type='permission_error'),
        'timeout': Factory.create_mock('error', failure_type='timeout_error'),
        'encoding': Factory.create_mock('error', failure_type='encoding_error'),
    }


# ============================================================================
# Time and Constants Fixtures - All use constants
# ============================================================================

@pytest.fixture
def freeze_time_fixture():
    """Freezes time for timestamp testing."""
    frozen_time = datetime.datetime(2025, 9, 27, 10, 30, 0, tzinfo=datetime.timezone.utc)
    with freeze_time(frozen_time):
        yield frozen_time


@pytest.fixture
def timestamp_tolerance():
    """Acceptable timestamp tolerance for timing tests."""
    return TIMING_CONSTANTS['timestamp_tolerance_seconds']


@pytest.fixture
def test_timestamps():
    """Various timestamp formats for testing."""
    return {
        'base_time': datetime.datetime(2025, 9, 27, 10, 30, 0, tzinfo=datetime.timezone.utc),
        'valid_timestamp': Factory.create_timestamp(),
        'past_timestamp': Factory.create_timestamp(-3600),
        'future_timestamp': Factory.create_timestamp(3600),
        'invalid_format': '2025-09-27 10:30:00',
        'invalid_string': 'not-a-timestamp'
    }


@pytest.fixture
def test_constants():
    """A dictionary of all test constants and values."""
    return {
        'file_size_limits': FILE_SIZE_LIMITS.copy(),
        'bad_input_types': BAD_INPUT_TYPES.copy(),
        'test_data_sizes': TEST_DATA_SIZES.copy(),
        'timestamp_tolerance': TIMING_CONSTANTS['timestamp_tolerance_seconds'],
        'processing_timeout': TIMING_CONSTANTS['default_processing_timeout'],
        'concurrent_timeout': TIMING_CONSTANTS['concurrent_operation_timeout'],
        'valid_extensions': SUPPORTED_FILE_TYPES.copy(),
        'invalid_extensions': UNSUPPORTED_FILE_TYPES.copy(),
        'mime_types': MIME_TYPES.copy(),
        'error_codes': ERROR_CODES.copy(),
        'http_status_codes': HTTP_STATUS_CODES.copy()
    }


# ============================================================================
# Parametrized Test Data Fixtures - All use constants
# ============================================================================

@pytest.fixture(params=['pdf', 'docx', 'doc', 'txt'])
def valid_file_types(request):
    """Parametrized fixture for all valid file types."""
    return f".{request.param}"


@pytest.fixture(params=['jpg', 'png', 'mp4', 'exe'])
def invalid_file_types(request):
    """Parametrized fixture for all invalid file types."""
    return f".{request.param}"


@pytest.fixture(params=[None, 'valid_cid', 'invalid_cid'])
def client_cid_variations_param(request, valid_client_cid, invalid_client_cid):
    """Parametrized fixture for different client_cid values."""
    match request.param:
        case None:
            return None
        case 'valid_cid':
            return valid_client_cid
        case 'invalid_cid':
            return invalid_client_cid


@pytest.fixture(params=['small', 'medium', 'large'])
def file_size_variations(request, test_data_sizes):
    """Parametrized fixture for different file sizes."""
    return test_data_sizes[request.param]


@pytest.fixture(params=[1, 5, 10, 20])
def concurrency_levels(request):
    """Parametrized fixture for different concurrency levels."""
    return request.param


@pytest.fixture(params=['success', 'file_error', 'database_error', 'processing_error'])
def error_scenarios(request):
    """Parametrized fixture for different error scenarios."""
    return request.param


# ============================================================================
# Concurrent Testing Fixtures - All use Factory
# ============================================================================

@pytest.fixture
def concurrent_upload_files():
    """A dictionary of file sets for concurrent upload testing."""
    args = (5, 'pdf')
    different_files_data = Factory.create_multiple_files(*args, identical_content=False)
    identical_files_data = Factory.create_multiple_files(*args, identical_content=True)
    return {
        'different': [content for content, filename in different_files_data],
        'identical': [content for content, filename in identical_files_data]
    }


# ============================================================================
# Helper Function Fixtures - All use Factory or constants
# ============================================================================

@pytest.fixture
def create_temp_file():
    """Helper function to create temporary test files."""

    def _create_temp_file(content: bytes, suffix: str = '.tmp') -> str:
        fd, path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, 'wb') as tmp_file:
                tmp_file.write(content)
        except Exception:
            os.close(fd)
            os.unlink(path)
            raise
        return path
    
    return _create_temp_file


@pytest.fixture
def verify_database_record():
    """Helper function to verify database record creation."""
    def _verify_database_record(db_mock, expected_cid: str, expected_data: Dict[str, Any]) -> bool:
        if not db_mock.execute.called:
            return False
        call_args = db_mock.execute.call_args
        return call_args is not None
    
    return _verify_database_record


@pytest.fixture
def generate_test_cid():
    """Helper function to generate test CIDs."""
    return Factory.make_cid


@pytest.fixture
def timing_utilities():
    """Utilities for timing and performance testing."""

    
    def measure_execution_time(func, *args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def assert_execution_time(max_seconds: float):
        class TimingAssertion:
            def __enter__(self):
                self.start_time = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                elapsed = time.time() - self.start_time
                assert elapsed <= max_seconds, f"Execution took {elapsed:.2f}s, expected <= {max_seconds}s"
        
        return TimingAssertion()
    
    return {
        'measure_execution_time': measure_execution_time,
        'assert_execution_time': assert_execution_time
    }


# ============================================================================
# Comprehensive Test Scenario Fixtures
# ============================================================================

@pytest.fixture
def all_file_type_scenarios():
    """All combinations of valid file types with different content."""
    scenarios = []
    for file_type in ['pdf', 'docx', 'doc', 'txt']:
        for content_type, text_content in TEXT_CONTENT_SAMPLES.items():
            if content_type not in ['large', 'empty']:  # Skip problematic content
                content = Factory.create_file_content(file_type, text_content=text_content)
                mock_file = Factory.create_mock('upload_file', {
                    'content': content,
                    'filename': f'test_{content_type}.{file_type}',
                    'content_type': MIME_TYPES[f'.{file_type}'],
                    'size': len(content)
                })
                scenarios.append((file_type, content_type, mock_file))
    return scenarios


@pytest.fixture
def all_error_scenarios():
    """All combinations of error types and failure conditions."""
    scenarios = {}
    
    # File-related errors
    scenarios['file_errors'] = {
        'empty': Factory.create_mock('upload_file', {'content': b'', 'size': 0}),
        'oversized': Factory.create_mock('upload_file', {
            'content': Factory.create_file_content('pdf', size='oversized'),
            'size': FILE_SIZE_LIMITS['oversized']
        }),
        'corrupted': Factory.create_mock('upload_file', {
            'content': Factory.create_file_content('pdf', corruption='header')
        }),
        'unsupported': Factory.create_mock('upload_file', {
            'content': Factory.create_file_content('jpg'),
            'content_type': MIME_TYPES['.jpg'],
            'filename': 'image.jpg'
        })
    }

    # Database errors
    scenarios['database_errors'] = {
        'connection': Factory.create_mock('database', should_fail=True, failure_type='connection'),
        'constraint': Factory.create_mock('database', should_fail=True, failure_type='constraint'),
        'timeout': Factory.create_mock('database', should_fail=True, failure_type='timeout')
    }
    
    # Processing errors
    scenarios['processing_errors'] = {
        'io_error': Factory.create_mock('error', failure_type='io_error'),
        'extraction_error': Factory.create_mock('error', failure_type='value_error'),
        'memory_error': Factory.create_mock('error', failure_type='memory_error')
    }
    
    return scenarios


@pytest.fixture
def concurrent_test_matrix():
    """Matrix of concurrent testing scenarios."""
    matrix = []
    limit = 4
    for level in CONCURRENCY_LEVELS[:limit]:
        # Same files
        same_files = Factory.create_multiple_files(level, 'pdf', identical_content=True)
        matrix.append(('same_files', level, same_files))
        
        # Different files  
        diff_files = Factory.create_multiple_files(level, 'pdf', identical_content=False)
        matrix.append(('different_files', level, diff_files))
        
        # Mixed file types
        mixed_files = []
        for idx, file_type in enumerate(['pdf', 'docx', 'doc', 'txt']):
            if idx >= level:
                break
            files = Factory.create_multiple_files(1, file_type, identical_content=False)
            mixed_files.extend(files)
        matrix.append(('mixed_types', level, mixed_files[:level]))
    
    return matrix
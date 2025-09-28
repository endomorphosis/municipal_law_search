import pytest


@pytest.mark.asyncio
class TestCIDGeneration:
    """Test Content Identifier (CID) generation functionality."""

    async def test_when_different_files_uploaded_sequentially_then_expect_unique_cids_generated(self, mock_app_instance, mock_upload_files):
        """
        GIVEN two different files are uploaded sequentially
        WHEN the upload_document method processes each file
        THEN expect each file to have different CIDs generated.
        """
        # Arrange
        pdf_file = mock_upload_files['pdf']
        docx_file = mock_upload_files['docx']

        # Act
        pdf_response = await mock_app_instance.upload_document(pdf_file)
        docx_response = await mock_app_instance.upload_document(docx_file)

        # Assert
        assert pdf_response.cid != docx_response.cid, \
            f"Expected different CIDs for different files, but both got {pdf_response.cid}"

    async def test_when_file_uploaded_successfully_then_expect_cid_follows_expected_format(self, mock_app_instance, mock_upload_files, test_patterns):
        """
        GIVEN any valid file is uploaded successfully
        WHEN the upload_document method generates a CID
        THEN expect the generated CID to follow the expected format and structure.
        """
        # Arrange
        pdf_file = mock_upload_files['pdf']
        cid_pattern = test_patterns.cid

        # Act
        response = await mock_app_instance.upload_document(pdf_file)
        generated_cid = response.cid

        # Assert
        assert cid_pattern.match(generated_cid), \
            f"Expected CID to match pattern {cid_pattern.pattern}, got {generated_cid}"

    async def test_when_identical_content_uploaded_multiple_times_then_expect_same_cid_generated(self, mock_app_instance, files_with_identical_content):
        """
        GIVEN the same file content is uploaded multiple times
        WHEN the upload_document method processes each upload
        THEN expect identical file content to produce the same CID each time.
        """
        # Arrange
        num_files = 2
        first_file_data, second_file_data = files_with_identical_content[:num_files]
        first_content, _, _ = first_file_data
        second_content, _, _ = second_file_data

        # Act
        first_response = await mock_app_instance.upload_document(first_content)
        second_response = await mock_app_instance.upload_document(second_content)
        first_cid = first_response.cid
        second_cid = second_response.cid

        # Assert
        assert first_cid == second_cid, \
            f"Expected identical content to produce same CID, got {first_cid} and {second_cid}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

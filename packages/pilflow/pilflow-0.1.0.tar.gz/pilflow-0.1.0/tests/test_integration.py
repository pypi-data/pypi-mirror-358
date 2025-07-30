import pytest
from PIL import Image

from pilflow import ImgPack, Operation


class TestIntegration:
    """Integration tests for the pilflow package."""
    
    def test_operation_chaining(self, small_img_pack):
        """Test chaining multiple operations together."""
        # Chain operations
        result = (
            small_img_pack
            .decide_resolution()
            .resize(width=200)
            .blur(radius=1.5)
        )
        
        # Check the result
        assert result.img.size[0] == 200  # Width should be 200
        assert result.has_context('resolution_decision')
        blur_context = result.get_context('blur')
        assert blur_context.blur_applied is True
        assert blur_context.blur_radius == 1.5
    
    def test_custom_operation(self):
        """Test creating and using a custom operation."""
        @Operation.register('grayscale')
        class GrayscaleOperation(Operation):
            def apply(self, img_pack):
                grayscale_img = img_pack.img.convert('L')
                return img_pack.copy(new_img=grayscale_img, grayscale_applied=True)
        
        # Test the custom operation
        img_pack = ImgPack(Image.new('RGB', (100, 100), color='red'))
        result = img_pack.grayscale()
        
        assert result.img.mode == 'L'
        assert result.context['grayscale_applied'] is True
    
    def test_from_file_with_operations(self, small_image_path):
        """Test loading an image from file and applying operations."""
        # Load image and apply operations
        result = (
            ImgPack.from_file(small_image_path)
            .decide_resolution()
            .resize(width=150)
        )
        
        # Check the result
        assert result.img.size[0] == 150
        assert result.has_context('resolution_decision')
    
    def test_complex_pipeline(self, small_img_pack):
        """Test a complex pipeline with multiple operations."""
        @Operation.register('add_metadata')
        class AddMetadataOperation(Operation):
            def __init__(self, key, value):
                self.key = key
                self.value = value
            
            def apply(self, img_pack):
                return img_pack.copy(**{self.key: self.value})
        
        # Create a complex pipeline
        result = (small_img_pack
                 .resize(width=50, height=50)
                 .blur(radius=1.0)
                 .add_metadata('processed', True)
                 .add_metadata('pipeline_step', 'final'))
        
        # Verify the pipeline results
        assert result.img.size == (50, 50)
        assert result.context['processed'] is True
        assert result.context['pipeline_step'] == 'final'
        assert result.has_context('blur')
        assert result.has_context('resize')
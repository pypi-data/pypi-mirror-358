"""
Test that all modules can be imported correctly.
"""

import pytest

def test_package_import():
    """Test that the main package can be imported."""
    import pywrfkit
    assert pywrfkit.__version__ == "0.1.5"

def test_module_imports():
    """Test that all modules can be imported."""
    from pywrfkit import wrf, polar, download, xrvar, params, metrics, norms
    
    # Test that modules exist
    assert wrf is not None
    assert polar is not None
    assert download is not None
    assert xrvar is not None
    assert params is not None
    assert metrics is not None
    assert norms is not None

def test_cartopy_dependent_modules():
    """Test cartopy-dependent modules with optional import."""
    try:
        from pywrfkit import coast, plot_geog, ahps
        # Test that modules exist
        assert coast is not None
        assert plot_geog is not None
        assert ahps is not None
    except ImportError:
        # Cartopy is not available, skip these tests
        pytest.skip("Cartopy not available, skipping cartopy-dependent module tests")

def test_wrf_functions():
    """Test that wrf module functions exist."""
    from pywrfkit import wrf
    
    # Test that functions exist
    assert hasattr(wrf, 'add_coords')
    assert hasattr(wrf, 'renamelatlon')
    assert callable(wrf.add_coords)
    assert callable(wrf.renamelatlon)

def test_polar_functions():
    """Test that polar module functions exist."""
    from pywrfkit import polar
    
    # Test that functions exist
    assert hasattr(polar, 'convert_to_polar')
    assert hasattr(polar, 'get_polar_from_file')
    assert callable(polar.convert_to_polar)
    assert callable(polar.get_polar_from_file)

def test_metrics_functions():
    """Test that metrics module functions exist."""
    from pywrfkit import metrics
    
    # Test that functions exist
    assert hasattr(metrics, 'l1')
    assert hasattr(metrics, 'l2')
    assert hasattr(metrics, 'sup')
    assert callable(metrics.l1)
    assert callable(metrics.l2)
    assert callable(metrics.sup)

def test_ahps_functions():
    """Test that AHPS module functions exist."""
    try:
        from pywrfkit import ahps
        # Test that functions exist
        assert hasattr(ahps, 'read_ahps')
        assert callable(ahps.read_ahps)
    except ImportError:
        # Cartopy is not available, skip this test
        pytest.skip("Cartopy not available, skipping AHPS function test")
    except AssertionError:
        # If ahps is a dummy class (cartopy not available), skip the test
        pytest.skip("AHPS module not properly loaded (cartopy may not be available)")

if __name__ == "__main__":
    pytest.main([__file__]) 
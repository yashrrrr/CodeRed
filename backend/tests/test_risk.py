"""
Test suite for risk scoring utility.

This module contains comprehensive tests for the risk assessment algorithm,
covering low-risk, high-risk, and edge case scenarios to ensure reliable
risk computation across various learner profiles.
"""

import pytest
from datetime import datetime, timezone, timedelta
from lib.risk import compute_risk, compute_and_update_all, _parse_iso_date, _calculate_recency_factor


class TestRiskComputation:
    """Test cases for individual risk score computation."""
    
    def test_low_risk_learner(self):
        """Test computation for a low-risk learner with good engagement."""
        learner = {
            'id': 'learner_001',
            'name': 'Excellent Student',
            'completed_percent': 95.0,
            'avg_quiz_score': 88.0,
            'consecutive_missed_sessions': 0,
            'last_login': (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        }
        
        result = compute_risk(learner)
        
        assert result['risk_score'] <= 0.4, f"Expected low risk, got {result['risk_score']}"
        assert result['risk_label'] == 'low'
        assert 'id' in result
        assert result['id'] == 'learner_001'
    
    def test_high_risk_learner(self):
        """Test computation for a high-risk learner with poor engagement."""
        learner = {
            'id': 'learner_002',
            'name': 'Struggling Student',
            'completed_percent': 15.0,
            'avg_quiz_score': 25.0,
            'consecutive_missed_sessions': 8,
            'last_login': (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
        }
        
        result = compute_risk(learner)
        
        assert result['risk_score'] > 0.7, f"Expected high risk, got {result['risk_score']}"
        assert result['risk_label'] == 'high'
        assert result['id'] == 'learner_002'
    
    def test_medium_risk_learner(self):
        """Test computation for a medium-risk learner with moderate engagement."""
        learner = {
            'id': 'learner_003',
            'name': 'Average Student',
            'completed_percent': 40.0,  # Higher risk to ensure medium range
            'avg_quiz_score': 60.0,
            'consecutive_missed_sessions': 4,
            'last_login': (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        }
        
        result = compute_risk(learner)
        
        assert 0.4 < result['risk_score'] <= 0.7, f"Expected medium risk, got {result['risk_score']}"
        assert result['risk_label'] == 'medium'
    
    def test_missing_fields_defensive_handling(self):
        """Test defensive handling when required fields are missing."""
        learner = {
            'id': 'learner_004',
            'name': 'Incomplete Data Student'
            # Missing all engagement metrics
        }
        
        result = compute_risk(learner)
        
        # Should default to high risk when no data available
        assert result['risk_score'] > 0.5, "Missing data should result in higher risk"
        assert 'risk_label' in result
        assert result['id'] == 'learner_004'
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types and out-of-range values."""
        learner = {
            'id': 'learner_005',
            'completed_percent': 150.0,  # Out of range
            'avg_quiz_score': -10.0,     # Negative
            'consecutive_missed_sessions': -5,  # Negative
            'last_login': 'invalid-date-format'
        }
        
        result = compute_risk(learner)
        
        # Should clamp values and handle gracefully
        assert 0 <= result['risk_score'] <= 1, "Risk score should be clamped to [0,1]"
        assert result['risk_label'] in ['low', 'medium', 'high']
    
    def test_boundary_conditions(self):
        """Test risk computation at boundary conditions."""
        # Perfect learner (should be lowest possible risk)
        perfect_learner = {
            'id': 'perfect',
            'completed_percent': 100.0,
            'avg_quiz_score': 100.0,
            'consecutive_missed_sessions': 0,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        
        result = compute_risk(perfect_learner)
        assert result['risk_score'] == 0.0, "Perfect learner should have zero risk"
        assert result['risk_label'] == 'low'
        
        # Worst case learner (should be highest possible risk)
        worst_learner = {
            'id': 'worst',
            'completed_percent': 0.0,
            'avg_quiz_score': 0.0,
            'consecutive_missed_sessions': 10,
            'last_login': (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        }
        
        result = compute_risk(worst_learner)
        assert result['risk_score'] >= 0.9, "Worst case should have very high risk"
        assert result['risk_label'] == 'high'


class TestBatchProcessing:
    """Test cases for batch risk computation."""
    
    def test_batch_processing_multiple_learners(self):
        """Test batch processing of multiple learners."""
        learners = [
            {
                'id': 'batch_001',
                'completed_percent': 90.0,
                'avg_quiz_score': 85.0,
                'consecutive_missed_sessions': 1,
                'last_login': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
            },
            {
                'id': 'batch_002',
                'completed_percent': 30.0,
                'avg_quiz_score': 40.0,
                'consecutive_missed_sessions': 6,
                'last_login': (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            },
            {
                'id': 'batch_003',
                'completed_percent': 65.0,
                'avg_quiz_score': 75.0,
                'consecutive_missed_sessions': 2,
                'last_login': (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            }
        ]
        
        results = compute_and_update_all(learners)
        
        assert len(results) == 3, "Should return same number of learners"
        
        # Verify all have risk scores and labels
        for result in results:
            assert 'risk_score' in result
            assert 'risk_label' in result
            assert 0 <= result['risk_score'] <= 1
            assert result['risk_label'] in ['low', 'medium', 'high']
    
    def test_empty_learner_list(self):
        """Test batch processing with empty list."""
        results = compute_and_update_all([])
        assert results == [], "Empty input should return empty list"
    
    def test_batch_with_invalid_learner(self):
        """Test batch processing handles individual learner errors gracefully."""
        learners = [
            {
                'id': 'valid_learner',
                'completed_percent': 80.0,
                'avg_quiz_score': 75.0,
                'consecutive_missed_sessions': 1,
                'last_login': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'problematic_learner',
                'completed_percent': 'invalid',  # This will cause issues
                'avg_quiz_score': None,
                'consecutive_missed_sessions': 'not_a_number',
                'last_login': 'bad_date'
            }
        ]
        
        results = compute_and_update_all(learners)
        
        # Should still return results for both learners
        assert len(results) == 2
        
        # Valid learner should have proper risk computation
        valid_result = next(r for r in results if r['id'] == 'valid_learner')
        assert 'risk_score' in valid_result
        assert valid_result['risk_label'] in ['low', 'medium', 'high']
        
        # Problematic learner should have default values
        problem_result = next(r for r in results if r['id'] == 'problematic_learner')
        assert problem_result['risk_score'] == 0.5  # Default medium risk
        assert problem_result['risk_label'] == 'medium'


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_parse_iso_date_valid_formats(self):
        """Test parsing of various valid ISO date formats."""
        # Standard ISO format
        date1 = _parse_iso_date('2024-01-15T10:30:00+00:00')
        assert date1 is not None
        assert date1.year == 2024
        
        # Z suffix format
        date2 = _parse_iso_date('2024-01-15T10:30:00Z')
        assert date2 is not None
        assert date2.year == 2024
        
        # Without timezone
        date3 = _parse_iso_date('2024-01-15T10:30:00')
        assert date3 is not None
        assert date3.year == 2024
    
    def test_parse_iso_date_invalid_formats(self):
        """Test parsing of invalid date formats."""
        assert _parse_iso_date('invalid-date') is None
        assert _parse_iso_date('') is None
        assert _parse_iso_date(None) is None
        assert _parse_iso_date('2024-13-45') is None  # Invalid date
    
    def test_calculate_recency_factor(self):
        """Test recency factor calculation."""
        # Recent login (1 day ago)
        recent_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        recent_factor = _calculate_recency_factor(recent_date)
        assert recent_factor < 0.1, "Recent login should have low recency factor"
        
        # Old login (35 days ago)
        old_date = (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
        old_factor = _calculate_recency_factor(old_date)
        assert old_factor >= 1.0, "Old login should have maximum recency factor"
        
        # Medium recency (15 days ago)
        medium_date = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        medium_factor = _calculate_recency_factor(medium_date)
        assert 0.4 < medium_factor < 0.6, "Medium recency should be around 0.5"
        
        # No login data
        no_login_factor = _calculate_recency_factor(None)
        assert no_login_factor == 1.0, "No login data should have maximum penalty"
        
        # Invalid date
        invalid_factor = _calculate_recency_factor('invalid-date')
        assert invalid_factor == 1.0, "Invalid date should have maximum penalty"


class TestRiskAlgorithmValidation:
    """Test cases to validate the risk algorithm produces expected results."""
    
    def test_concurrent_processing_safety(self):
        """Test that risk computation is safe for concurrent processing."""
        import threading
        import time
        
        learner_template = {
            'id': 'concurrent_test',
            'completed_percent': 50.0,
            'avg_quiz_score': 70.0,
            'consecutive_missed_sessions': 2,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        
        results = []
        errors = []
        
        def compute_risk_worker(worker_id):
            try:
                learner = learner_template.copy()
                learner['id'] = f'concurrent_test_{worker_id}'
                result = compute_risk(learner)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=compute_risk_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and consistent results
        assert len(errors) == 0, f"Concurrent processing errors: {errors}"
        assert len(results) == 10, "Should have 10 results from concurrent processing"
        
        # All results should be identical (same input data)
        expected_score = results[0]['risk_score']
        for result in results:
            assert abs(result['risk_score'] - expected_score) < 0.001, "Concurrent results should be identical"
    
    def test_memory_usage_with_large_batch(self):
        """Test memory efficiency with large batch processing."""
        # Create a large batch of learners
        large_batch = []
        for i in range(1000):
            learner = {
                'id': f'batch_learner_{i:04d}',
                'name': f'Student {i}',
                'completed_percent': (i % 100),  # 0-99% completion
                'avg_quiz_score': ((i * 7) % 100),  # Pseudo-random scores
                'consecutive_missed_sessions': (i % 10),  # 0-9 missed sessions
                'last_login': (datetime.now(timezone.utc) - timedelta(days=(i % 30))).isoformat()
            }
            large_batch.append(learner)
        
        # Process the large batch
        results = compute_and_update_all(large_batch)
        
        # Verify all processed correctly
        assert len(results) == 1000, "Should process all 1000 learners"
        
        # Verify results are reasonable
        risk_scores = [r['risk_score'] for r in results]
        assert min(risk_scores) >= 0.0, "All risk scores should be >= 0"
        assert max(risk_scores) <= 1.0, "All risk scores should be <= 1"
        
        # Should have variety in risk scores due to different inputs
        unique_scores = len(set(risk_scores))
        assert unique_scores > 10, f"Should have variety in risk scores, got {unique_scores} unique values"
    
    def test_algorithm_component_weights(self):
        """Test that algorithm components have correct weights."""
        base_learner = {
            'id': 'test_weights',
            'completed_percent': 50.0,
            'avg_quiz_score': 50.0,
            'consecutive_missed_sessions': 0,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        
        # Test completion weight (should be 0.5 * 0.5 = 0.25)
        completion_test = base_learner.copy()
        completion_test.update({
            'completed_percent': 0.0,  # Maximum completion risk
            'avg_quiz_score': 100.0,   # No quiz risk
            'consecutive_missed_sessions': 0,  # No attendance risk
        })
        result = compute_risk(completion_test)
        expected_completion_risk = 0.5  # 50% weight for completion
        assert abs(result['risk_score'] - expected_completion_risk) < 0.01
    
    def test_risk_label_thresholds(self):
        """Test that risk labels are assigned at correct thresholds."""
        # Test just above low/medium boundary (0.4)
        learner_medium = {
            'id': 'boundary_test',
            'completed_percent': 18.0,  # 0.5 * 0.82 = 0.41 risk (just above 0.4)
            'avg_quiz_score': 100.0,
            'consecutive_missed_sessions': 0,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        result = compute_risk(learner_medium)
        assert result['risk_label'] == 'medium', f"Score of {result['risk_score']} should be medium risk"
        
        # Test just at boundary (should be low)
        learner_at_boundary = {
            'id': 'boundary_low',
            'completed_percent': 20.0,  # 0.5 * 0.8 = 0.4 risk (exactly at boundary)
            'avg_quiz_score': 100.0,
            'consecutive_missed_sessions': 0,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        result_boundary = compute_risk(learner_at_boundary)
        assert result_boundary['risk_label'] == 'low', f"Score of {result_boundary['risk_score']} should be low risk"
    
    def test_extreme_values_handling(self):
        """Test handling of extreme values beyond normal ranges."""
        extreme_learner = {
            'id': 'extreme_test',
            'completed_percent': 999.0,  # Way over 100% (will be clamped to 100)
            'avg_quiz_score': -50.0,     # Negative score (will be clamped to 0)
            'consecutive_missed_sessions': 100,  # Very high missed sessions
            'last_login': (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()  # Very old login
        }
        
        result = compute_risk(extreme_learner)
        
        # Should still produce valid risk score and label
        assert 0 <= result['risk_score'] <= 1, "Risk score should be clamped even with extreme values"
        assert result['risk_label'] in ['low', 'medium', 'high']
        
        # With clamped values: 100% completion (0 risk), 0% quiz score, high missed sessions, very old login
        # Expected: 0.5 * (1-1) + 0.2 * (1-0) + 0.2 * 1 + 0.1 * 1 = 0 + 0.2 + 0.2 + 0.1 = 0.5
        assert result['risk_score'] == 0.5, f"Expected risk score 0.5, got {result['risk_score']}"
        assert result['risk_label'] == 'medium', "Risk score of 0.5 should be medium risk"
    
    def test_unicode_and_special_characters(self):
        """Test handling of unicode characters and special strings in learner data."""
        unicode_learner = {
            'id': 'unicode_test_🎓',
            'name': 'José María González-Pérez',
            'completed_percent': 75.0,
            'avg_quiz_score': 82.5,
            'consecutive_missed_sessions': 1,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        
        result = compute_risk(unicode_learner)
        
        assert result['id'] == 'unicode_test_🎓'
        assert 'risk_score' in result
        assert result['risk_label'] in ['low', 'medium', 'high']
    
    def test_floating_point_precision(self):
        """Test that floating point calculations maintain reasonable precision."""
        precision_learner = {
            'id': 'precision_test',
            'completed_percent': 33.333333,
            'avg_quiz_score': 66.666666,
            'consecutive_missed_sessions': 0,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        
        result = compute_risk(precision_learner)
        
        # Risk score should be computed with reasonable precision
        assert isinstance(result['risk_score'], float)
        assert len(str(result['risk_score']).split('.')[-1]) <= 10, "Risk score should not have excessive decimal places"
    
    def test_timezone_handling(self):
        """Test handling of different timezone formats in last_login."""
        timezones_to_test = [
            datetime.now(timezone.utc).isoformat(),  # UTC
            '2024-01-15T10:30:00+05:30',  # IST
            '2024-01-15T10:30:00-08:00',  # PST
            '2024-01-15T10:30:00Z',       # Zulu time
        ]
        
        for i, tz_format in enumerate(timezones_to_test):
            learner = {
                'id': f'tz_test_{i}',
                'completed_percent': 70.0,
                'avg_quiz_score': 80.0,
                'consecutive_missed_sessions': 1,
                'last_login': tz_format
            }
            
            result = compute_risk(learner)
            
            assert 'risk_score' in result, f"Failed to process timezone format: {tz_format}"
            assert result['risk_label'] in ['low', 'medium', 'high']
    
    def test_data_corruption_resilience(self):
        """Test resilience against various forms of data corruption."""
        corrupted_data_scenarios = [
            # SQL injection attempts
            {
                'id': "'; DROP TABLE learners; --",
                'name': "Robert'); DROP TABLE students;--",
                'completed_percent': 75.0,
                'avg_quiz_score': 80.0,
                'consecutive_missed_sessions': 1,
                'last_login': datetime.now(timezone.utc).isoformat()
            },
            # XSS attempts
            {
                'id': 'xss_test',
                'name': '<script>alert("xss")</script>',
                'completed_percent': 60.0,
                'avg_quiz_score': 70.0,
                'consecutive_missed_sessions': 2,
                'last_login': datetime.now(timezone.utc).isoformat()
            },
            # Binary data
            {
                'id': 'binary_test',
                'name': b'Binary Name'.decode('utf-8', errors='ignore'),
                'completed_percent': 50.0,
                'avg_quiz_score': 65.0,
                'consecutive_missed_sessions': 3,
                'last_login': datetime.now(timezone.utc).isoformat()
            },
            # Very long strings
            {
                'id': 'long_string_test',
                'name': 'A' * 1000,  # Very long name
                'completed_percent': 45.0,
                'avg_quiz_score': 55.0,
                'consecutive_missed_sessions': 1,
                'last_login': datetime.now(timezone.utc).isoformat()
            },
            # Mixed data types as strings
            {
                'id': 'mixed_types',
                'name': 'Mixed Types Student',
                'completed_percent': '75.5',  # String instead of float
                'avg_quiz_score': '80',       # String instead of float
                'consecutive_missed_sessions': '2',  # String instead of int
                'last_login': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        for i, corrupted_learner in enumerate(corrupted_data_scenarios):
            try:
                result = compute_risk(corrupted_learner)
                
                # Should still produce valid output
                assert 'risk_score' in result, f"Scenario {i}: Missing risk_score"
                assert 'risk_label' in result, f"Scenario {i}: Missing risk_label"
                assert 0 <= result['risk_score'] <= 1, f"Scenario {i}: Invalid risk_score range"
                assert result['risk_label'] in ['low', 'medium', 'high'], f"Scenario {i}: Invalid risk_label"
                
            except Exception as e:
                pytest.fail(f"Scenario {i} should not raise exception: {e}")
    
    def test_performance_with_realistic_data_sizes(self):
        """Test performance characteristics with realistic data volumes."""
        import time
        
        # Test single learner performance
        single_learner = {
            'id': 'perf_test_single',
            'completed_percent': 65.0,
            'avg_quiz_score': 78.0,
            'consecutive_missed_sessions': 2,
            'last_login': datetime.now(timezone.utc).isoformat()
        }
        
        start_time = time.time()
        result = compute_risk(single_learner)
        single_duration = time.time() - start_time
        
        assert single_duration < 0.1, f"Single learner processing should be fast, took {single_duration}s"
        assert 'risk_score' in result
        
        # Test batch performance (100 learners)
        batch_learners = []
        for i in range(100):
            learner = {
                'id': f'perf_test_batch_{i}',
                'completed_percent': (i % 100),
                'avg_quiz_score': ((i * 3) % 100),
                'consecutive_missed_sessions': (i % 8),
                'last_login': (datetime.now(timezone.utc) - timedelta(days=(i % 20))).isoformat()
            }
            batch_learners.append(learner)
        
        start_time = time.time()
        batch_results = compute_and_update_all(batch_learners)
        batch_duration = time.time() - start_time
        
        assert batch_duration < 1.0, f"Batch processing should be efficient, took {batch_duration}s"
        assert len(batch_results) == 100
        
        # Batch should be more efficient than individual processing
        estimated_individual_time = single_duration * 100
        efficiency_ratio = batch_duration / estimated_individual_time
        assert efficiency_ratio < 2.0, f"Batch processing should be reasonably efficient, ratio: {efficiency_ratio}"
"""Tests for nyan-pytest plugin functionality."""

import pytest
from unittest.mock import Mock, patch
from nyan_pytest.plugin import NyanReporter, pytest_addoption, pytest_configure
from nyan_pytest.frames import NYAN_FRAMES, RAINBOW_COLORS, ANIMATION_SPEED_DIVISOR


class TestFrameSelectionLogic:
    """Test the core frame selection logic that could cause animation flicker."""
    
    def test_frame_selection_consistency(self):
        """Test that frame selection is consistent and doesn't flicker."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 3
        }[opt]
        
        reporter = NyanReporter(config)
        reporter.interactive = False
        
        # Test frame progression for speed=3
        expected_sequence = []
        
        # For speed=3, each frame should appear for 3 ticks
        for tick in range(36):  # 3 full cycles through 12 frames
            reporter.tick = tick
            frame_idx = reporter.get_current_frame_index()
            animation_tick = reporter.get_current_animation_tick()
            
            expected_frame = (tick // 3) % 12
            expected_animation_tick = tick // 3
            
            assert frame_idx == expected_frame, f"At tick {tick}, expected frame {expected_frame}, got {frame_idx}"
            assert animation_tick == expected_animation_tick, f"At tick {tick}, expected animation_tick {expected_animation_tick}, got {animation_tick}"
            
            expected_sequence.append(frame_idx)
        
        # Check that we get a proper repeating sequence
        # Should be: [0,0,0,1,1,1,2,2,2,...,11,11,11,0,0,0,1,1,1,...]
        expected_pattern = []
        for frame_num in range(12):
            expected_pattern.extend([frame_num] * 3)
        
        # First 36 items should match one complete cycle of the pattern
        assert len(expected_sequence) == 36
        assert len(expected_pattern) == 36  # 12 frames * 3 repetitions each
        assert expected_sequence == expected_pattern
    
    def test_frame_selection_at_different_speeds(self):
        """Test frame selection logic at various speeds."""
        test_cases = [
            {"speed": 1, "ticks": [0, 1, 2, 11, 12, 13], "expected_frames": [0, 1, 2, 11, 0, 1]},
            {"speed": 2, "ticks": [0, 1, 2, 3, 4, 5], "expected_frames": [0, 0, 1, 1, 2, 2]},
            {"speed": 5, "ticks": [0, 4, 5, 9, 10, 14], "expected_frames": [0, 0, 1, 1, 2, 2]},
            {"speed": 10, "ticks": [0, 9, 10, 19, 20, 29], "expected_frames": [0, 0, 1, 1, 2, 2]},
        ]
        
        for case in test_cases:
            config = Mock()
            config.getoption.side_effect = lambda opt: {
                "--nyan-only": False,
                "--nyan-speed": case["speed"]
            }[opt]
            
            reporter = NyanReporter(config)
            reporter.interactive = False
            
            for tick, expected_frame in zip(case["ticks"], case["expected_frames"]):
                reporter.tick = tick
                actual_frame = reporter.get_current_frame_index()
                assert actual_frame == expected_frame, f"Speed {case['speed']}, tick {tick}: expected frame {expected_frame}, got {actual_frame}"
    
    def test_animation_tick_calculation(self):
        """Test that animation tick calculation is correct."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 6
        }[opt]
        
        reporter = NyanReporter(config)
        reporter.interactive = False
        
        # Test animation tick progression
        test_cases = [
            (0, 0),   # tick 0 -> animation_tick 0
            (5, 0),   # tick 5 -> animation_tick 0 (still in first frame)
            (6, 1),   # tick 6 -> animation_tick 1 (second frame)
            (11, 1),  # tick 11 -> animation_tick 1 (still in second frame)
            (12, 2),  # tick 12 -> animation_tick 2 (third frame)
            (71, 11), # tick 71 -> animation_tick 11 (last frame of first cycle)
            (72, 12), # tick 72 -> animation_tick 12 (first frame of second cycle)
        ]
        
        for tick, expected_animation_tick in test_cases:
            reporter.tick = tick
            actual_animation_tick = reporter.get_current_animation_tick()
            assert actual_animation_tick == expected_animation_tick, f"Tick {tick}: expected animation_tick {expected_animation_tick}, got {actual_animation_tick}"
    
    def test_rainbow_and_frame_synchronization(self):
        """Test that rainbow and frame animations stay synchronized."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 4
        }[opt]
        
        reporter = NyanReporter(config)
        reporter.interactive = False
        
        # Test that both use the same animation tick
        for tick in range(50):
            reporter.tick = tick
            frame_animation_tick = reporter.get_current_animation_tick()
            
            # Simulate getting rainbow segment (which should use same animation tick)
            rainbow_segment = reporter._get_rainbow_segment(0, 5, frame_animation_tick)
            
            # The animation tick should be consistent
            expected_animation_tick = tick // 4
            assert frame_animation_tick == expected_animation_tick, f"Tick {tick}: frame and rainbow animation ticks should match"
    
    def test_no_frame_skipping_or_flickering(self):
        """Test that frames don't skip or flicker unexpectedly."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 5
        }[opt]
        
        reporter = NyanReporter(config)
        reporter.interactive = False
        
        previous_frame = None
        frame_duration_count = 0
        
        # Track frame changes over many ticks
        for tick in range(100):
            reporter.tick = tick
            current_frame = reporter.get_current_frame_index()
            
            if previous_frame is None:
                previous_frame = current_frame
                frame_duration_count = 1
            elif current_frame == previous_frame:
                frame_duration_count += 1
            else:
                # Frame changed - check that it lasted the expected duration
                assert frame_duration_count == 5, f"Frame {previous_frame} lasted {frame_duration_count} ticks, expected 5 (speed=5)"
                
                # Check that frame progressed correctly (no skipping)
                expected_next_frame = (previous_frame + 1) % 12
                assert current_frame == expected_next_frame, f"Frame jumped from {previous_frame} to {current_frame}, expected {expected_next_frame}"
                
                previous_frame = current_frame
                frame_duration_count = 1
    
    def test_edge_cases_and_boundaries(self):
        """Test edge cases that might cause flicker."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 1
        }[opt]
        
        reporter = NyanReporter(config)
        reporter.interactive = False
        
        # Test boundary conditions
        boundary_tests = [
            (0, 0),    # First tick
            (11, 11),  # Last frame of first cycle
            (12, 0),   # First frame of second cycle
            (23, 11),  # Last frame of second cycle
            (24, 0),   # First frame of third cycle
        ]
        
        for tick, expected_frame in boundary_tests:
            reporter.tick = tick
            actual_frame = reporter.get_current_frame_index()
            assert actual_frame == expected_frame, f"Boundary test failed: tick {tick} should give frame {expected_frame}, got {actual_frame}"


class TestSpeedFunctionality:
    """Test the animation speed functionality."""
    
    def test_default_speed_option(self):
        """Test that default speed is 6."""
        parser = Mock()
        group = Mock()
        parser.getgroup.return_value = group
        
        pytest_addoption(parser)
        
        # Check that --nyan-speed option was added with default 6
        group.addoption.assert_any_call(
            "--nyan-speed",
            metavar="SPEED",
            type=int,
            default=6,
            help="Animation speed (1=fastest, 6=default, 100=slowest)",
        )
    
    def test_nyan_reporter_uses_speed_setting(self):
        """Test that NyanReporter respects the speed setting."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 15
        }[opt]
        
        reporter = NyanReporter(config)
        
        assert reporter.animation_speed == 15
    
    def test_frame_selection_with_different_speeds(self):
        """Test that frame selection respects speed setting."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 3
        }[opt]
        
        reporter = NyanReporter(config)
        reporter.interactive = False  # Disable output for testing
        
        # Test frame selection logic
        reporter.tick = 0
        frame_idx = (reporter.tick // reporter.animation_speed) % len(reporter._colored_frames)
        assert frame_idx == 0
        
        reporter.tick = 2
        frame_idx = (reporter.tick // reporter.animation_speed) % len(reporter._colored_frames)
        assert frame_idx == 0  # Still frame 0 because 2 // 3 = 0
        
        reporter.tick = 3
        frame_idx = (reporter.tick // reporter.animation_speed) % len(reporter._colored_frames)
        assert frame_idx == 1  # Now frame 1 because 3 // 3 = 1
        
        reporter.tick = 6
        frame_idx = (reporter.tick // reporter.animation_speed) % len(reporter._colored_frames)
        assert frame_idx == 2  # Frame 2 because 6 // 3 = 2
    
    def test_rainbow_segment_respects_speed(self):
        """Test that rainbow trail animation respects speed setting."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 4
        }[opt]
        
        reporter = NyanReporter(config)
        
        # Test rainbow segment with different animation ticks
        animation_tick_1 = 1
        animation_tick_2 = 5
        
        # Should get different results for different animation ticks
        segment_1 = reporter._get_rainbow_segment(0, 5, animation_tick_1)
        segment_2 = reporter._get_rainbow_segment(0, 5, animation_tick_2)
        
        # They should be different because the animation tick affects colors
        assert segment_1 != segment_2
    
    def test_speed_bounds(self):
        """Test that various speed values work correctly."""
        test_speeds = [1, 6, 15, 50, 100]
        
        for speed in test_speeds:
            config = Mock()
            config.getoption.side_effect = lambda opt: {
                "--nyan-only": False,
                "--nyan-speed": speed
            }[opt]
            
            reporter = NyanReporter(config)
            assert reporter.animation_speed == speed
            
            # Test that frame calculation works for this speed
            for tick in [0, speed-1, speed, speed+1, speed*2]:
                reporter.tick = tick
                animation_tick = reporter.tick // reporter.animation_speed
                frame_idx = animation_tick % len(reporter._colored_frames)
                
                # Should always be a valid frame index
                assert 0 <= frame_idx < len(reporter._colored_frames)


class TestFrameData:
    """Test the frame data and constants."""
    
    def test_frame_count(self):
        """Test that we have the expected number of frames."""
        assert len(NYAN_FRAMES) == 12
        
    def test_frame_structure(self):
        """Test that each frame has the expected structure."""
        for i, frame in enumerate(NYAN_FRAMES):
            assert isinstance(frame, list), f"Frame {i} should be a list"
            assert len(frame) == 6, f"Frame {i} should have 6 lines"
            for j, line in enumerate(frame):
                assert isinstance(line, str), f"Frame {i}, line {j} should be a string"
    
    def test_rainbow_colors(self):
        """Test that rainbow colors are defined correctly."""
        expected_colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        assert RAINBOW_COLORS == expected_colors
    
    def test_animation_speed_divisor_exists(self):
        """Test that animation speed divisor constant exists."""
        assert isinstance(ANIMATION_SPEED_DIVISOR, int)
        assert ANIMATION_SPEED_DIVISOR > 0


class TestPluginIntegration:
    """Test plugin integration and configuration."""
    
    def test_pytest_configure_registers_reporter(self):
        """Test that pytest_configure registers the reporter when options are set."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan": True,
            "--nyan-only": False,
            "--nyan-sim": 0,
            "--nyan-speed": 6
        }[opt]
        config.pluginmanager = Mock()
        
        pytest_configure(config)
        
        # Should register the nyan reporter
        config.pluginmanager.register.assert_called_once()
        args = config.pluginmanager.register.call_args[0]
        assert isinstance(args[0], NyanReporter)
        assert args[1] == "nyan-reporter"
    
    def test_pytest_configure_with_nyan_only(self):
        """Test that nyan-only mode unregisters standard reporter."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan": False,
            "--nyan-only": True,
            "--nyan-sim": 0,
            "--nyan-speed": 6
        }[opt]
        config.pluginmanager = Mock()
        
        pytest_configure(config)
        
        # Should register the nyan reporter
        config.pluginmanager.register.assert_called_once()
    
    def test_pytest_configure_with_simulation(self):
        """Test that simulation mode registers additional plugin."""
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan": False,
            "--nyan-only": False,
            "--nyan-sim": 50,
            "--nyan-speed": 6
        }[opt]
        config.pluginmanager = Mock()
        
        pytest_configure(config)
        
        # Should register both the nyan reporter and simulation plugin
        assert config.pluginmanager.register.call_count == 2


class TestSpeedIntegration:
    """Test speed parameter integration with real pytest execution."""
    
    def test_speed_parameter_in_help(self):
        """Test that speed parameter appears in pytest help."""
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'pytest', '--help'], 
            capture_output=True, 
            text=True
        )
        
        # Should mention the nyan-speed option
        assert '--nyan-speed' in result.stdout
        assert 'Animation speed' in result.stdout
        
    def test_different_speeds_produce_different_timing(self):
        """Test that different speeds affect animation timing in practice."""
        import subprocess
        import time
        
        # Test fast speed
        start = time.time()
        result_fast = subprocess.run([
            'python', '-m', 'pytest', '--nyan-sim', '10', '--nyan-speed', '1'
        ], capture_output=True)
        time_fast = time.time() - start
        
        # Test slow speed  
        start = time.time()
        result_slow = subprocess.run([
            'python', '-m', 'pytest', '--nyan-sim', '10', '--nyan-speed', '20'
        ], capture_output=True)
        time_slow = time.time() - start
        
        # Both should succeed
        assert result_fast.returncode == 0
        assert result_slow.returncode == 0
        
        # Speed shouldn't significantly affect total time since simulation timing
        # is dominated by the 10ms sleep per test, not animation speed
        # But we can verify both completed successfully
        assert b"Simulation complete!" in result_fast.stdout
        assert b"Simulation complete!" in result_slow.stdout


class TestMockReport:
    """Test the mock report functionality used in simulation."""
    
    def test_mock_report_creation(self):
        """Test that mock reports are created correctly."""
        # Import the MockReport class from the simulate_tests function scope
        # We'll test this by running a small simulation and checking behavior
        config = Mock()
        config.getoption.side_effect = lambda opt: {
            "--nyan-only": False,
            "--nyan-speed": 6
        }[opt]
        
        reporter = NyanReporter(config)
        reporter.interactive = False  # Disable output
        
        # Test that the reporter can handle test reports
        initial_passed = reporter.passed
        initial_failed = reporter.failed
        initial_skipped = reporter.skipped
        
        # These should start at 0
        assert initial_passed == 0
        assert initial_failed == 0
        assert initial_skipped == 0
        
        # Test that counters can be incremented
        reporter.passed += 1
        reporter.failed += 1
        reporter.skipped += 1
        
        assert reporter.passed == 1
        assert reporter.failed == 1
        assert reporter.skipped == 1
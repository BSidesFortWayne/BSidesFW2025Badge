import unittest

from src.lib.list_view import ListView

class TestListView(unittest.TestCase):
    def setUp(self):
        """Set up a ListView instance for testing."""
        self.items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
        self.list_view = ListView(items=self.items, window_size=3, peek_behind=1, peek_ahead=1)

    def test_initial_state(self):
        """Test the initial state of the ListView."""
        self.assertEqual(self.list_view.get_selected_index(), 0)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 1", "Item 2", "Item 3"])

    def test_move_selection(self):
        """Test moving the selection up and down."""
        self.list_view.move_selection(1)
        self.assertEqual(self.list_view.get_selected_index(), 1)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 1", "Item 2", "Item 3"])

        self.list_view.move_selection(1)
        self.assertEqual(self.list_view.get_selected_index(), 2)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 1", "Item 2", "Item 3"])

        self.list_view.move_selection(-1)
        self.assertEqual(self.list_view.get_selected_index(), 1)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 1", "Item 2", "Item 3"])

    def test_wrap_selection(self):
        """Test wrapping selection around the list."""
        self.list_view.set_selected_index(4)  # Last item
        self.list_view.move_selection(1)       # Should wrap to first item
        self.assertEqual(self.list_view.get_selected_index(), 0)
        
        self.list_view.move_selection(-1)      # Should wrap to last item
        self.assertEqual(self.list_view.get_selected_index(), 4)

    def test_get_selected_item(self):
        """Test getting the currently selected item."""
        self.assertEqual(self.list_view.get_selected_item(), "Item 1")
        
        self.list_view.move_selection(2)       # Move to Item 3
        self.assertEqual(self.list_view.get_selected_item(), "Item 3")

    def test_set_selected_index(self):
        """Test setting the selected index."""
        self.list_view.set_selected_index(2)
        self.assertEqual(self.list_view.get_selected_index(), 2)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 1", "Item 2", "Item 3"])

        # Test out of bounds
        with self.assertRaises(IndexError):
            self.list_view.set_selected_index(10)

        # Test wrapping
        self.list_view.set_selected_index(10)
        self.assertEqual(self.list_view.get_selected_index(), 0)

    def test_get_visible_items(self):
        """Test getting the visible items based on the current selection."""
        self.list_view.set_selected_index(2)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 1", "Item 2", "Item 3"])
        self.list_view.set_selected_index(0)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 1", "Item 2", "Item 3"])
        self.list_view.set_selected_index(4)
        self.assertEqual(self.list_view.get_visible_items(), ["Item 3", "Item 4", "Item 5"])
    
    def test_length(self):
        """Test the length of the ListView."""
        self.assertEqual(len(self.list_view), len(self.items))
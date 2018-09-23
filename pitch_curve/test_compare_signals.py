import numpy as np
import unittest
import compare_signals

class TestCalc(unittest.TestCase):
    
    def test_match_len(self):
        matrix_1 = np.random.rand(20,4)
        matrix_2 = np.random.rand(18,4)
        matrix_3 = np.random.rand(3,4)
        matrix_4 = np.random.rand(20,2)

        matrix_list1 = [matrix_1,matrix_2,matrix_3]
        matrix_list2 = [matrix_1,matrix_2,matrix_3,matrix_4]
        
        matrix_matched = [3,3,3]
        _, lens_list = compare_signals.match_len(matrix_list1)
        
        self.assertEqual(lens_list,matrix_matched)
        
        #test for not matching columns
        #self.assertRaises(ValueError,compare_signals.match_len,matrix_list2)
        
        #or via context manager
        with self.assertRaises(ValueError):
            compare_signals.match_len(matrix_list2)

        
if __name__ == '__main__':
    unittest.main()

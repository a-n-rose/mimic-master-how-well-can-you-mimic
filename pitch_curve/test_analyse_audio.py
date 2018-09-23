import numpy as np
import unittest
import analyse_audio

class TestCalc(unittest.TestCase):
    
    def test_stft2power(self):
        #test positive floats
        matrix = np.random.rand(10,4)
        self.assertEqual(analyse_audio.stft2power(matrix).all(),(np.abs(matrix)**2).all())
        #test positive and negative floats
        matrix = np.random.randn(10,4)
        self.assertEqual(analyse_audio.stft2power(matrix).all(),(np.abs(matrix)**2).all())
        #test high and low positive and negative floats
        matrix = np.random.uniform(low=-100.0,high=100.0,size=(10,4))
        self.assertEqual(analyse_audio.stft2power(matrix).all(),(np.abs(matrix)**2).all())
        #test high and low positive and negative integers:
        matrix = np.random.randint(low=-100.0,high=100.0,size=(10,4))
        
        
        #test for empty or None input
        #self.assertRaises(TypeError,analyse_audio.stft2power,[])
        #self.assertRaises(TypeError,analyse_audio.stft2power,None)
        
        #or via context manager
        with self.assertRaises(TypeError):
            analyse_audio.stft2power([])
        with self.assertRaises(TypeError):
            analyse_audio.stft2power(None)
        
if __name__ == '__main__':
    unittest.main()

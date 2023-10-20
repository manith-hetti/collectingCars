import unittest
import car_database


class TestCarDatabase(unittest.TestCase):

    def test_find_car(self):
        self.assertEqual(car_database.find_car('bmw', 'm3', 'e46', ''), 3)
        self.assertEqual(car_database.find_car('alpine', 'a110', '', 'premiere edition'), 4)

    def test_insert_car(self):
        self.assertEqual(car_database.insert_car(4, 39500, 8450, 2018, 'automatic', '2023-05-23', 'Blanc Solaire', 'sold' , 20660), 1)
        self.assertEqual(car_database.insert_car(4, 35250, 27000, 2018, 'automatic', '2023-04-21', 'Bleu Alpine', 'sold' , 19578), 1)

    def test_find_auction(self):
        self.assertEqual(car_database.find_auction(20660), 10)
        self.assertEqual(car_database.find_auction(19578), 11)

    

if __name__ == '__main__':
    unittest.main()
from typing import List, Tuple
import matplotlib.pyplot as plt
from numberdividend import controller

class NumberCore:
    @staticmethod
    def dividend(array: List[float], target_sum: float, limit: int = None, decimal: int = 2) -> List[Tuple[float, float]]:
        """
        Calculate the dividend distribution of an array.

        Args:
            array (List[float]): List of float numbers to be distributed.
            target_sum (float): Target sum for the distribution.
            limit (int, optional): Optional limit on the number of elements to consider from the array.
            decimal (int, optional): Optional number of decimal places for the output.

        Returns:
            List[Tuple[int, float]]: List of tuples containing the index and the dividend value.
        """
        controller.check_type_list("array", array)
        controller.check_type_float("target_sum", target_sum)

        if limit is not None:
            controller.check_type_int("limit", limit)

        if decimal is not None:
            controller.check_type_int("decimal", decimal)

        if limit:
            array = array[:limit]

        total = sum(array)
        if total == 0:
            raise ValueError("The sum of the array elements is zero, cannot calculate dividend.")
        
        scale = target_sum / total
        dividend = [round(x * scale, decimal) for x in array]
        return dividend
    
    @staticmethod
    def display(array: List[float]):
        """
        Display the dividend distribution using matplotlib.

        Args:
            array (List[float]): List of dividend values to be displayed.

        Returns:
            None
        """
        print(f"Dividend Distribution Sum: {sum(array)}")
        
        fig, ax = plt.subplots()
        ax.bar(range(len(array)), array, color='orange')
        
        plt.title('Dividend Distribution')
        plt.xlabel('Index')
        plt.ylabel('Dividend Value')
        plt.grid(True)
        plt.show()
    
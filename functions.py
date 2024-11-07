


def compute_smallest_path(list):
    """
    Returns the best path to collect all the packages located
    or prints "NO" if its not possible

    Args:
        list (nd.array): The list containing the coordinates ordered based on the distance from the starting position
    
    Returns:
        Null: Prints "YES" or "NO", and if "YES" it prints the smallest path to collect all the packages ordered lexicographically 
    
    
    """

    # Init the starting coordinates
    current_coordinate = (0, 0)
    # Init the list that will contain the Path
    result = []

    # Iterate over the number of packages
    for target_x, target_y in list:
        # Stop the iteration when next package cannot be reached with "U" and "R"
        if (target_x < current_coordinate[0]) or (target_y < current_coordinate[1]):
            print("NO")
            return
        # Compute the number of Steps we have to make to reach the next package in the list 
        # summing the absolute value of the differences between the current coordinates and 
        # the target coordinates 
        distance_from_next = target_x - current_coordinate[0] + target_y - current_coordinate[1]

        # Loop over this distance
        for _ in range(distance_from_next):

            # We give to return the best path ordered lexigraphically so 
            # we prefer appending the "R" to the result if they match the condition
            if current_coordinate[0] < target_x:
                # We update our coordinates because we have moved right
                current_coordinate = (current_coordinate[0] + 1, current_coordinate[1])
                result.append("R")
                continue
            # Otherwise we move upper if our Y coordinate is lower than the target one
            if current_coordinate[1] < target_y:
                # We update the current coordinates after the step and we append to the result "U"
                current_coordinate = (current_coordinate[0] , current_coordinate[1] + 1)
                result.append("U")

    # After the loop we print "YES", bacause if the loop ended without 
    # entering if the first if we are able to collect all the packages 
    print("YES")
    # In the end we print all the elements in the 'result' list
    # representing the best path to collect all the packages
    print("".join(result))



def extended_compute_smallest_path(list):
    """
    Returns the best path to collect all the packages located

    Args:
        list (nd.array): The list containing the coordinates ordered based on the distance from the starting position
    
    Returns:
        Null: Prints "YES" and prints the smallest path to collect all the packages ordered lexicographically 
    
    """

    # Init the starting coordinates
    current_coordinate = (0, 0)
    # Init the list that will contain the Path
    result = []

    # Iterate over the number of packages
    for target_x, target_y in list:
        # Compute the number of Steps we have to make to reach the next package in the list 
        # summing the absolute value of the differences between the current coordinates and 
        # the target coordinates 
        distance_from_next = abs(target_x - current_coordinate[0]) + abs(target_y - current_coordinate[1])

        # Loop over this distance
        for _ in range(distance_from_next):

            # Checks if the Y coordinate of our target package is under our current position 
            if current_coordinate[1] > target_y:
                # We update the current coordinates after the step and we append to the result "D"
                current_coordinate = (current_coordinate[0] , current_coordinate[1] - 1)
                result.append("D")

            # Checks if the X coordinate of our target package is on the left of our current position 
            if current_coordinate[0] > target_x:
                # We update the current coordinates after the step and we append to the result "L"
                current_coordinate = (current_coordinate[0] - 1, current_coordinate[1])
                result.append("L")                            

            # We give to return the best path ordered lexigraphically so 
            # we prefer appending the "R" to the result if they match the condition
            if current_coordinate[0] < target_x:
                # We update our coordinates because we have moved right
                current_coordinate = (current_coordinate[0] + 1, current_coordinate[1])
                result.append("R")
                continue
            # Otherwise we move upper if our Y coordinate is lower than the target one
            if current_coordinate[1] < target_y:
                # We update the current coordinates after the step and we append to the result "U"
                current_coordinate = (current_coordinate[0] , current_coordinate[1] + 1)
                result.append("U")

    # After the loop we print "YES", bacause if the loop ended without 
    # entering if the first if we are able to collect all the packages 
    print("YES")
    # In the end we print all the elements in the 'result' list
    # representing the best path to collect all the packages
    print("".join(result))




        


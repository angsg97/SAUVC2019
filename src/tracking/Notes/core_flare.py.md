# core_flare.py

* # class

  #### TwoPointLine

  ​	This class defines the lines which takes 4 parameter, specified by two points.

  ​	reverse function will turn the two point line, make the two ends changed.

  #### Vector

  ​	This class defines a two dimensional vector.

   * methods
      * **dot** returns the dot product of the two vectors
      * **norm** returns the modules of a vector. 
      * **angle** use the cos method. but it will return 0 if the cos value is larger than 1 this is when meet some errors
      * **add_vector** add vector returns the new vector that is the sum of twp vectors

  #### Flare

  ​	Inherited from **ITrackingCore** so that we can directly get the frames, instead of get the new picture by capture using the camera.

   * methods

      * **__inital_filter** this function takes in a line, we filter it by setting the minimal dy is 40 and maximal dx to be 20 so that it will not be a long horizontal lines.

      * **__secondary_filter** we the aim is to find out the pares of lines that is parallel, vertical, and close with each other. the  first step is to loop over all of the lines. make sure y1 is always smaller than y2, so it is easier to compare latter. and create two different vectors. 

         * we create a total score and check the difference between the lines we wish to get and the lines we get and assign a score to each standard, and finally multiply them up. 
            * This includes the angle between the two vectors(best is to be parallel, but can allow it to be 10 degree with each other)
            * we check what is the different between the vertical line and it, we wish to get a vertical line, but we allow 10 degree error.
            * the distance between the two lines, as the flare is very thin so we want it to be as thin as possible but not inline with each other, so that latter we use __parallel_lines to filter it out.
            * we take the average value of the colors over the area between the two lines, as we hope it is yellow, but this can be affected by different reasons.

      * **__sub_score** is a function that returns the score of a value. it tells us how far it is from our value. with a permitted error

      * **__sub_score_core** this is a function that gives a weight to the value due to how far the value is different from our expected values. 

        (function :1/(x**6 + 1))![1554831784983](/home/luo/.config/Typora/typora-user-images/1554831784983.png)

      * **__parallel_lines** this function is used to check if the lines are parallel. inside the function we created a vector, and parallel_lines is a list that stores the lines that is not parallel, if the line taken in is parallel to any lines that is inside the lines(less than 5 degree), then we will remove the line stored inside the lines list. so that finally we can get all un parallel lines(or overlap each other)

      * **find** this function takes in a frame and resize it to 640 by 360 (16:9). we separate out the blue frame. and use GaussianBlur to make it blur, it is higher in the horizontal direction than in the vertical direction. so that the lines on the bottom of the swimming pool can be clear out in the frame. then we use canny to detect the edges. using the blurred frame. then use the HoughLinesP to detect the lines inside the edge frame, and make sure the minimal length is 75 and the gas is larger than 5

         * if there is line detected, then we loop all the lines, use __initial_filter and __secondary_filter one following each other.
         * then we find out the best pare of lines, (the one with the highest score, as it is the most close one that is near the expected value)
         * finally draw a line following the final line using green color, and return the average distance between the different between center of the two lines and the center of the frame, 
         * any frame inside the returned list will be shown 
         * if there is no line detected, then None for angle will be returned.

  ​	

  ​	
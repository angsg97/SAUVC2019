# core_gate.py

## class

have almost two same classes as the core_flare. TwoPointLine, and Vector,  GateTrackerV2 and GateTrackerV3 are two different versions of the GateTracker.

#### special method that is different from the core_flare

## v2

**__possible_gate** 

​	this method create four vectors from the two lines left, right, up and down.

 * if the up and down vector has 0 length, then the two lines are in line so we decide this is not the possible gate
 * if the left line is not parallel with the right line then we decide this is not the possible gate.
 * the angle between the vertical ones and the horizontal ones is more than 70 and less than 110, or else, it is not a possible gate
 * the length of the vertical line is either the same as the horizontal line or more than 2/3 of the horizontal line or else it is not a gate

**find** 

this function takes the two lines compare and find a possible gate filter using __possible_line and possible gate.

​	there's a function gate total defined in side that is to get the length of the height sum of the two lines. 

​	and in the end we return the gate with the longest length .

### v3

same method as core_flare using score to sort the two lines. 

 * left one parallel with right one
 * left line is perpendicular with the up one
 * right line is perpendicular with the down one
 * left line is perpendicular with the down one
* right line is perpendicular with the upper one
* left length + right length == upper length + bottom length
* left line and right line are vertical

the find method is same as the one used in core_flare.py

please check **core_flare.py.md**





​	